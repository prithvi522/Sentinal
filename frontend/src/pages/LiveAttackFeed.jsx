import { useEffect, useState } from 'react';
import AppShell from '../components/AppShell';
import AlertTicker from '../components/AlertTicker';
import { createAlertsSocket } from '../lib/socket';

export default function LiveAttackFeed() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const ws = createAlertsSocket((evt) => {
      if (evt.payload) {
        setAlerts((prev) => [evt.payload, ...prev].slice(0, 200));
      }
    });

    return () => {
      if (typeof ws.safeClose === 'function') ws.safeClose(); else ws.close();
    };
  }, []);

  return (
    <AppShell>
      <div className="space-y-4">
        <div>
          <h1 className="font-display text-2xl text-cyan">Live Attack Feed</h1>
          <p className="text-white/70">Real-time incoming alerts and telemetry stream.</p>
        </div>

        <div className="glass-card p-4">
          <AlertTicker alerts={alerts} />
        </div>
      </div>
    </AppShell>
  );
}
