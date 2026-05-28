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
      { path: '/threat-intel', element: <ProtectedRoute><ThreatIntel /></ProtectedRoute> },
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
