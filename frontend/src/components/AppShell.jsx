import { motion } from 'framer-motion';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { Shield, Radar, FlaskConical, Siren, Bot, LogOut, Mic, CircleCheckBig, TriangleAlert, CircleSlash2, RefreshCw, ArrowUpRight, Database } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../lib/api';
import { useState, useEffect } from 'react';
import { createAlertsSocket } from '../lib/socket';

const navItems = [
  { to: '/', label: 'Dashboard', icon: Shield },
  { to: '/analyst', label: 'AI Analyst', icon: FlaskConical },
  { to: '/vulnerability-intelligence', label: 'Vuln Intel', icon: Database },
  { to: '/threat-intel', label: 'Threat Intel', icon: Radar },
  { to: '/prompt-firewall', label: 'Prompt Firewall', icon: Radar },
  { to: '/threat-hunter', label: 'Threat Hunter', icon: Siren },
  { to: '/incident-response', label: 'Incident Response', icon: Shield },
  { to: '/copilot', label: 'Security Copilot', icon: Bot },
];

export default function AppShell({ children }) {
  const { logout, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [moduleStatuses, setModuleStatuses] = useState([]);
  const [statusLoading, setStatusLoading] = useState(false);
  const [statusError, setStatusError] = useState('');

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const r = new SpeechRecognition();
    r.lang = 'en-US';
    r.interimResults = false;
    r.maxAlternatives = 1;
    r.onresult = async (event) => {
      const text = event.results[0][0].transcript;
      try {
        const { data } = await api.post('/copilot/chat', { message: text });
        // speak response
          const utter = new SpeechSynthesisUtterance(typeof data === 'string' ? data : data?.answer || JSON.stringify(data));
        window.speechSynthesis.speak(utter);
      } catch (error) {
        console.error('Error sending message to copilot:', error);
        const utter = new SpeechSynthesisUtterance("I'm sorry, I'm having trouble connecting to the copilot.");
        window.speechSynthesis.speak(utter);
      }
    };
    r.onerror = (e) => console.error('Speech recognition error', e);
    setRecognition(r);
    return () => {
      if (r) {
        r.onresult = null;
        r.onerror = null;
      }
    };
  }, []);

  useEffect(() => {
    let alive = true;

    const loadModuleStatuses = async () => {
      setStatusLoading(true);
      try {
        const { data } = await api.get('/dashboard/enterprise');
        if (!alive) return;
        setModuleStatuses(data?.module_statuses || []);
        setStatusError('');
      } catch (error) {
        if (!alive) return;
        setStatusError('Status feed unavailable');
      } finally {
        if (alive) setStatusLoading(false);
      }
    };

    loadModuleStatuses();
    const timer = window.setInterval(loadModuleStatuses, 30000);
    const socket = createAlertsSocket((evt) => {
      if (evt?.channel === 'module_status_update' || evt?.channel === 'threat_alert' || evt?.channel === 'simulation_alert') {
        void loadModuleStatuses();
      }
    });

    return () => {
      alive = false;
      window.clearInterval(timer);
      if (typeof socket.safeClose === 'function') {
        socket.safeClose();
      } else {
        socket.close();
      }
    };
  }, []);

  const handleMicClick = () => {
    if (!recognition) return;
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  const statusIcon = (state) => {
    if (state === 'healthy') return <CircleCheckBig size={16} className="text-emerald-400" />;
    if (state === 'warning') return <TriangleAlert size={16} className="text-amber-400" />;
    if (state === 'error') return <TriangleAlert size={16} className="text-rose-400" />;
    return <CircleSlash2 size={16} className="text-white/35" />;
  };

  const statusTone = (state) => {
    if (state === 'healthy') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200';
    if (state === 'warning') return 'border-amber-500/30 bg-amber-500/10 text-amber-100';
    if (state === 'error') return 'border-rose-500/30 bg-rose-500/10 text-rose-100';
    return 'border-white/10 bg-white/5 text-white/60';
  };

  const formatLastSeen = (value) => {
    if (!value) return 'Idle';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return 'Idle';
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const moduleRoutes = {
    vulnerability_intelligence: '/vulnerability-intelligence',
    ai_analyst: '/analyst',
    prompt_firewall: '/prompt-firewall',
    threat_hunter: '/threat-hunter',
    incident_response: '/incident-response',
    ai_copilot: '/copilot',
    threat_intel: '/threat-intel',
    reporting: '/',
  };

  const activeModule = Object.entries(moduleRoutes).find(([, route]) => {
    if (route === '/') return location.pathname === '/';
    return location.pathname.startsWith(route);
  })?.[0];

  return (
    <div className="min-h-screen flex">
      <div className="fixed bottom-3 left-3 right-3 z-50 lg:hidden glass-card p-2 flex items-center justify-between gap-1">
        {navItems.slice(0, 5).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex-1 text-center text-xs rounded p-2 border ${
                isActive ? 'border-cyan text-cyan bg-cyan/10' : 'border-cyan/20 text-white/80'
              }`
            }
          >
            {item.label.split(' ')[0]}
          </NavLink>
        ))}
      </div>

      <aside className="w-72 hidden lg:flex flex-col p-5 border-r border-cyan/20 bg-black/25 backdrop-blur-xl">
        <Link to="/" className="font-display text-2xl text-cyan tracking-wider mb-8">
          SentinelAI OS
        </Link>
        <div className="space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 p-3 rounded-lg border transition ${
                  isActive ? 'border-cyan bg-cyan/15 text-cyan shadow-neon' : 'border-cyan/20 hover:border-cyan/60'
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </div>
        <div className="mt-auto terminal-box text-lime">
          <p>User: {user?.full_name}</p>
          <p>Role: {user?.role}</p>
        </div>
        <button onClick={logout} className="mt-4 flex items-center justify-center gap-2 p-3 rounded-lg border border-danger/70 text-danger hover:bg-danger/10">
          <LogOut size={16} />
          Logout
        </button>
      </aside>

      <main className="flex-1 p-4 md:p-6 lg:p-8 pb-24 lg:pb-8">
        <div className="flex justify-end mb-4">
          <button onClick={handleMicClick} className="p-2 rounded-full bg-cyan/20 text-cyan hover:bg-cyan/30">
            <Mic size={20} />
          </button>
        </div>
        <div className="mb-5 glass-card border border-cyan/15 p-3 md:p-4">
          <div className="flex items-center justify-between gap-3 mb-3">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-white/40">Module status</p>
              <p className="text-sm text-white/70">Live health and last execution across the platform</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-white/45">
              {statusLoading ? <RefreshCw size={14} className="animate-spin" /> : <CircleCheckBig size={14} />}
              <span>{statusError || 'Auto-refreshing every 30s'}</span>
            </div>
          </div>
          <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-6">
            {moduleStatuses.length > 0 ? moduleStatuses.map((module) => (
              <button
                key={module.module}
                type="button"
                onClick={() => navigate(moduleRoutes[module.module] || '/')}
                title={`Open ${module.label}`}
                className={`rounded-xl border px-3 py-2 backdrop-blur-sm text-left transition hover:-translate-y-0.5 hover:shadow-lg ${statusTone(module.state)} ${activeModule === module.module ? 'ring-2 ring-cyan/60 shadow-neon scale-[1.01]' : ''}`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    {statusIcon(module.state)}
                    <span className="text-sm font-medium truncate">{module.label}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <ArrowUpRight size={12} className="opacity-70" />
                    <span className="text-[10px] uppercase tracking-[0.2em] opacity-70">{module.state}</span>
                    {activeModule === module.module ? (
                      <span className="animate-pulse rounded-full border border-cyan/40 bg-cyan/15 px-2 py-0.5 text-[9px] uppercase tracking-[0.2em] text-cyan">
                        Current
                      </span>
                    ) : null}
                  </div>
                </div>
                <div className="mt-2 text-xs text-white/60 flex items-center justify-between gap-2">
                  <span>{formatLastSeen(module.last_seen_at)}</span>
                  <span>{module.last_status_code ? `HTTP ${module.last_status_code}` : 'No activity'}</span>
                </div>
              </button>
            )) : (
              <div className="col-span-full rounded-xl border border-white/10 bg-white/5 px-3 py-4 text-sm text-white/50">
                No module activity yet. Run a scan, open Copilot, or trigger an incident workflow to populate live status.
              </div>
            )}
          </div>
        </div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          {children}
        </motion.div>
      </main>
    </div>
  );
}