import { lazy, Suspense } from 'react';
import { Navigate } from 'react-router-dom';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Analyst = lazy(() => import('./pages/Analyst'));
const PromptFirewall = lazy(() => import('./pages/PromptFirewall'));
const ThreatHunter = lazy(() => import('./pages/ThreatHunter'));
const IncidentResponse = lazy(() => import('./pages/IncidentResponse'));
const Copilot = lazy(() => import('./pages/Copilot'));
const VulnerabilityIntelligence = lazy(() => import('./pages/VulnerabilityIntelligence'));
const ThreatIntel = lazy(() => import('./pages/ThreatIntel'));
const LiveAttackFeed = lazy(() => import('./pages/LiveAttackFeed'));
const TerminalConsole = lazy(() => import('./pages/TerminalConsole'));
const AttackSimulator = lazy(() => import('./pages/AttackSimulator'));
const PhishingDetector = lazy(() => import('./pages/PhishingDetector'));
const LogAnalyzer = lazy(() => import('./pages/LogAnalyzer'));
const MalwareAnalyzer = lazy(() => import('./pages/MalwareAnalyzer'));
const ThreatMap = lazy(() => import('./pages/ThreatMap'));
const CommandCenter = lazy(() => import('./pages/CommandCenter'));
const VoiceAssistant = lazy(() => import('./pages/VoiceAssistant'));
const SocActivityFeed = lazy(() => import('./pages/SocActivityFeed'));
const IntegrityMonitor = lazy(() => import('./pages/IntegrityMonitor'));
const LockdownMode = lazy(() => import('./pages/LockdownMode'));
const ThreatPrediction = lazy(() => import('./pages/ThreatPrediction'));
const AIRecommendations = lazy(() => import('./pages/AIRecommendations'));

function RouteFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#040814] text-white/70">
      Loading SentinelAI OS...
    </div>
  );
}

export default function App() {
  const router = createBrowserRouter(
    [
      { path: '/login', element: <Login /> },
      { path: '/register', element: <Register /> },
      { path: '/', element: <ProtectedRoute><Dashboard /></ProtectedRoute> },
      { path: '/analyst', element: <ProtectedRoute><Analyst /></ProtectedRoute> },
      { path: '/prompt-firewall', element: <ProtectedRoute><PromptFirewall /></ProtectedRoute> },
      { path: '/vulnerability-intelligence', element: <ProtectedRoute><VulnerabilityIntelligence /></ProtectedRoute> },
      { path: '/live-attack-feed', element: <ProtectedRoute><LiveAttackFeed /></ProtectedRoute> },
      { path: '/attack-simulator', element: <ProtectedRoute><AttackSimulator /></ProtectedRoute> },
      { path: '/phishing-detector', element: <ProtectedRoute><PhishingDetector /></ProtectedRoute> },
      { path: '/log-analyzer', element: <ProtectedRoute><LogAnalyzer /></ProtectedRoute> },
      { path: '/malware-analyzer', element: <ProtectedRoute><MalwareAnalyzer /></ProtectedRoute> },
      { path: '/threat-map', element: <ProtectedRoute><ThreatMap /></ProtectedRoute> },
      { path: '/command-center', element: <ProtectedRoute><CommandCenter /></ProtectedRoute> },
      { path: '/voice-assistant', element: <ProtectedRoute><VoiceAssistant /></ProtectedRoute> },
      { path: '/soc-activity-feed', element: <ProtectedRoute><SocActivityFeed /></ProtectedRoute> },
      { path: '/integrity-monitor', element: <ProtectedRoute><IntegrityMonitor /></ProtectedRoute> },
      { path: '/lockdown-mode', element: <ProtectedRoute><LockdownMode /></ProtectedRoute> },
      { path: '/threat-prediction', element: <ProtectedRoute><ThreatPrediction /></ProtectedRoute> },
      { path: '/ai-recommendations', element: <ProtectedRoute><AIRecommendations /></ProtectedRoute> },
      { path: '/threat-intel', element: <ProtectedRoute><ThreatIntel /></ProtectedRoute> },
      { path: '/terminal-console', element: <ProtectedRoute><TerminalConsole /></ProtectedRoute> },
      { path: '/threat-hunter', element: <ProtectedRoute><ThreatHunter /></ProtectedRoute> },
      { path: '/incident-response', element: <ProtectedRoute><IncidentResponse /></ProtectedRoute> },
      { path: '/copilot', element: <ProtectedRoute><Copilot /></ProtectedRoute> },
      { path: '*', element: <Navigate to='/' replace /> },
    ],
    { future: { v7_startTransition: true, v7_relativeSplatPath: true } }
  );

  return (
    <AuthProvider>
      <Suspense fallback={<RouteFallback />}>
        <RouterProvider
          router={router}
          future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
        />
      </Suspense>
    </AuthProvider>
  );
}
