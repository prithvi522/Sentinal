import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Mic, MicOff, Radio, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../components/AppShell';
import { initiateLockdown } from '../lib/securityCenter';

const COMMANDS = [
  { match: /show active threats/i, response: 'Opening live attack feed.', action: '/live-attack-feed' },
  { match: /start security scan/i, response: 'Launching AI Analyst scan.', action: '/analyst' },
  { match: /enable lockdown/i, response: 'Enabling lockdown mode now.', action: 'lockdown' },
  { match: /generate incident report/i, response: 'Opening incident response workflow.', action: '/incident-response' },
  { match: /show malware alerts/i, response: 'Displaying malware analyzer.', action: '/malware-analyzer' },
];

export default function VoiceAssistant() {
  const navigate = useNavigate();
  const [recognition, setRecognition] = useState(null);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('Say a command to control the SOC.');
  const [status, setStatus] = useState('Idle');

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const r = new SpeechRecognition();
    r.lang = 'en-US';
    r.interimResults = false;
    r.maxAlternatives = 1;
    r.onresult = async (event) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
      const matched = COMMANDS.find((item) => item.match.test(text));
      if (!matched) {
        setResponse('Command not recognized. Try a supported SOC phrase.');
        setStatus('No action taken');
        return;
      }

      setResponse(matched.response);
      setStatus('Executing');
      if (matched.action === 'lockdown') {
        await initiateLockdown();
        navigate('/lockdown-mode');
      } else {
        navigate(matched.action);
      }
      setStatus('Completed');
    };
    setRecognition(r);
    return () => {
      r.onresult = null;
      if (listening) {
        try { r.stop(); } catch {}
      }
    };
  }, [listening, navigate]);

  function toggleListening() {
    if (!recognition) return;
    if (listening) {
      recognition.stop();
      setListening(false);
      setStatus('Listening stopped');
    } else {
      recognition.start();
      setListening(true);
      setStatus('Listening for command');
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <div className="glass-card p-5 border border-cyan/15">
          <p className="text-xs uppercase tracking-[0.25em] text-white/40">Voice-Controlled Security Assistant</p>
          <h1 className="font-display text-3xl text-cyan mt-2">Browser-native SOC command control</h1>
        </div>

        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          onClick={toggleListening}
          className={`w-full rounded-3xl border-2 p-8 font-display text-3xl tracking-[0.3em] ${listening ? 'border-rose-500/60 bg-rose-500/15 text-rose-100 animate-pulse' : 'border-cyan/50 bg-cyan/10 text-cyan'}`}
        >
          {listening ? <MicOff className="mx-auto mb-3" size={36} /> : <Mic className="mx-auto mb-3" size={36} />}
          {listening ? 'STOP LISTENING' : 'START SECURITY VOICE'}
        </motion.button>

        <div className="grid gap-4 xl:grid-cols-3">
          <div className="glass-card p-4 border border-white/10 xl:col-span-2">
            <p className="text-white/40 text-xs uppercase tracking-[0.2em]">Transcript</p>
            <p className="mt-2 text-lg text-white">{transcript || 'Waiting for voice input...'}</p>
            <div className="mt-4 rounded-2xl border border-white/10 bg-black/25 p-3">
              <p className="text-white/40 text-xs uppercase tracking-[0.2em] mb-2">AI response</p>
              <p className="text-white/80">{response}</p>
            </div>
          </div>

          <div className="glass-card p-4 border border-white/10 space-y-3">
            <div className="rounded-2xl border border-white/10 bg-black/25 p-3">
              <p className="text-xs uppercase tracking-[0.2em] text-white/40">Execution status</p>
              <p className="text-2xl text-lime-200 mt-2">{status}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/25 p-3 terminal-box">
              <p className="text-lime-200">&gt; Show active threats</p>
              <p className="text-lime-200">&gt; Start security scan</p>
              <p className="text-lime-200">&gt; Enable lockdown</p>
              <p className="text-lime-200">&gt; Generate incident report</p>
              <p className="text-lime-200">&gt; Show malware alerts</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/25 p-3 flex items-center gap-2 text-white/70 text-sm">
              <ShieldCheck size={16} className="text-cyan" /> SpeechRecognition API only, no cloud AI.
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/25 p-3 flex items-center gap-2 text-white/70 text-sm">
              <Radio size={16} className="text-rose-300" /> Supports lockdown and navigation commands.
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
