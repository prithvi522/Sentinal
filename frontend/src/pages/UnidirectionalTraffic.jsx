import { useCallback, useEffect, useState } from 'react';
import { Activity, Pause, Play, RotateCcw, ShieldCheck, Square } from 'lucide-react';
import AppShell from '../components/AppShell';
import KpiCard from '../components/KpiCard';
import { api } from '../lib/api';

const scenarios = [['normal', 'Normal'], ['ddos', 'DDoS'], ['c2', 'C2'], ['dga', 'DGA / DNS Tunnel'], ['port_scan', 'Port Scan'], ['tls_malware', 'TLS Malware'], ['exfiltration', 'Exfiltration'], ['mixed', 'Mixed']];
const tone = { CRITICAL: 'text-danger border-danger/40 bg-danger/10', HIGH: 'text-warning border-warning/40 bg-warning/10', MEDIUM: 'text-warning border-warning/40 bg-warning/10', LOW: 'text-lime border-lime/40 bg-lime/10' };

export default function UnidirectionalTraffic() {
  const [data, setData] = useState(null);
  const [scenario, setScenario] = useState('normal');
  const [speed, setSpeed] = useState(1);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const { data: overview } = await api.get('/unidirectional/overview');
      setData(overview); setError('');
    } catch { setError('Passive traffic service is unavailable.'); }
  }, []);

  const control = async (path, payload) => {
    try {
      const { data: overview } = await api.post(`/unidirectional/demo/${path}`, payload);
      setData(overview); setError('');
    } catch { setError('Unable to update the offline demo.'); }
  };

  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    const socket = new WebSocket(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/v1/ws/unidirectional`);
    socket.onopen = () => socket.send('subscribe');
    socket.onmessage = (event) => {
      try { const message = JSON.parse(event.data); if (message.channel === 'unidirectional_update') setData(message.payload); } catch { /* ignore malformed telemetry */ }
    };
    return () => socket.close();
  }, []);

  const traffic = data?.traffic || {};
  const simulation = data?.simulation || {};
  const airGap = data?.air_gap || {};
  return <AppShell><div className="space-y-5">
    <div className="glass-card content-surface p-5 border border-cyan/25">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div><p className="text-xs uppercase tracking-[.28em] text-white/45">SIH26145 · passive telemetry</p><h1 className="font-display text-3xl md:text-4xl text-cyan mt-2">Unidirectional Traffic</h1><p className="text-white/65 mt-2 max-w-3xl">Offline, read-only analysis of ingress telemetry. This module never probes hosts, injects packets, or decrypts payloads.</p></div>
        <div className="flex flex-wrap gap-2"><button onClick={() => control('start', { scenario, speed })} className="px-4 py-2 rounded bg-cyan text-black font-semibold inline-flex gap-2"><Play size={16}/>Start demo</button><button onClick={() => control('pause')} className="px-3 py-2 rounded border border-warning/40 text-warning"><Pause size={16}/></button><button onClick={() => control('stop')} className="px-3 py-2 rounded border border-danger/40 text-danger"><Square size={16}/></button><button onClick={() => control('reset')} className="px-3 py-2 rounded border border-white/20 text-white/75"><RotateCcw size={16}/></button></div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">{scenarios.map(([id, label]) => <button key={id} onClick={() => setScenario(id)} className={`rounded-full px-3 py-1 text-xs border ${scenario === id ? 'border-cyan bg-cyan/15 text-cyan' : 'border-white/15 text-white/65'}`}>{label}</button>)}{[0.5,1,2,5].map((value) => <button key={value} onClick={() => setSpeed(value)} className={`rounded-full px-3 py-1 text-xs border ${speed === value ? 'border-lime bg-lime/10 text-lime' : 'border-white/15 text-white/65'}`}>{value}x</button>)}</div>
    </div>
    {error && <div className="rounded-xl border border-danger/40 bg-danger/10 p-3 text-danger">{error}</div>}
    <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">{[['READ ONLY', airGap.read_only ? 'ACTIVE' : '—'], ['INGRESS ONLY', airGap.ingress_only ? 'ACTIVE' : '—'], ['RETURN PATH', airGap.return_path || 'BLOCKED'], ['ACTIVE PROBES', airGap.active_probes ?? 0], ['PACKET INJECTION', airGap.packet_injection ?? 0]].map(([label,value]) => <div key={label} className="glass-card p-3 border border-lime/20"><p className="text-[10px] tracking-[.2em] text-white/45">{label}</p><p className="text-lime mt-1 font-semibold">{value}</p></div>)}</div>
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4"><KpiCard title="Packets / sec" value={traffic.packets_per_second || 0}/><KpiCard title="Bytes / sec" value={traffic.bytes_per_second || 0}/><KpiCard title="Total flows" value={traffic.total_flows || 0}/><KpiCard title="Security score" value={`${data?.security_score ?? 98}/100`} accent={(data?.security_score ?? 98) < 70 ? 'danger' : 'cyan'}/></div>
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-4"><div className="glass-card p-4 xl:col-span-2"><div className="flex justify-between gap-3"><div><p className="text-xs uppercase tracking-[.2em] text-white/45">Live packet stream</p><h2 className="font-display text-xl text-cyan mt-1">Ingress summaries only</h2></div><span className="text-sm text-white/55">{simulation.mode || 'STOPPED'} · {simulation.scenario || 'normal'}</span></div><div className="mt-4 max-h-[360px] overflow-auto"><table className="w-full min-w-[620px] text-sm"><thead className="text-left text-white/40"><tr><th>Time</th><th>Source</th><th>Destination</th><th>Protocol</th><th>Size</th><th>Risk</th></tr></thead><tbody>{(data?.packets || []).map((packet, index) => <tr key={`${packet.time}-${index}`} className="border-t border-white/10 text-white/75"><td className="py-2">{new Date(packet.time).toLocaleTimeString()}</td><td>{packet.source}</td><td>{packet.destination}</td><td className="text-cyan">{packet.protocol}</td><td>{packet.size}</td><td className={packet.risk === 'LOW' ? 'text-lime' : 'text-danger'}>{packet.risk}</td></tr>)}</tbody></table></div></div>
      <div className="glass-card p-4"><p className="text-xs uppercase tracking-[.2em] text-white/45">Protocol distribution</p><h2 className="font-display text-xl text-lime mt-1">Observed metadata</h2><div className="mt-4 space-y-3">{Object.entries(traffic.protocols || {}).map(([protocol,count]) => <div key={protocol}><div className="flex justify-between text-sm"><span>{protocol}</span><span className="text-cyan">{count}</span></div><div className="mt-1 h-2 rounded bg-white/10"><div className="h-full rounded bg-cyan" style={{width:`${Math.min(100,count*10)}%`}}/></div></div>)}{!Object.keys(traffic.protocols || {}).length && <p className="text-white/50 text-sm">Start a demo to observe passive telemetry.</p>}</div><div className="mt-5 rounded-xl border border-white/10 bg-black/20 p-3 text-xs text-white/60"><ShieldCheck size={14} className="inline text-lime mr-2"/>Payload decryption: disabled · outbound requests: 0</div></div></div>
    <div className="glass-card p-4"><p className="text-xs uppercase tracking-[.2em] text-white/45">Threat investigation queue</p><h2 className="font-display text-xl text-warning mt-1">Confidence and evidence</h2><div className="mt-4 space-y-3">{(data?.alerts || []).map((alert) => <div key={alert.alert_id} className="rounded-xl border border-white/10 bg-black/25 p-3"><div className="flex flex-wrap justify-between gap-2"><p className="text-white font-medium">{alert.threat_class}</p><span className={`rounded-full border px-2 py-0.5 text-xs ${tone[alert.severity]}`}>{alert.severity} · {alert.confidence}%</span></div><p className="text-white/55 text-sm mt-1">{alert.source_ip} → {alert.destination_ip} · {alert.protocol}</p><p className="text-white/75 text-sm mt-2">{alert.evidence?.indicators?.join(' · ')}</p><p className="text-cyan text-xs mt-2">{alert.model} · {alert.latency_ms?.total} ms fusion path</p></div>)}{!(data?.alerts || []).length && <p className="text-white/50 text-sm">No passive detections yet.</p>}</div></div>
  </div></AppShell>;
}
