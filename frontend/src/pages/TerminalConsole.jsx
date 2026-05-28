import { useState } from 'react';
import AppShell from '../components/AppShell';

export default function TerminalConsole() {
  const [command, setCommand] = useState('');
  const [output, setOutput] = useState('');
  const [running, setRunning] = useState(false);

  async function runCommand(e) {
    e.preventDefault();
    if (!command.trim()) return;
    setRunning(true);
    try {
      const res = await fetch('/api/v1/terminal/exec', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      });
      const data = await res.json();
      setOutput((prev) => `${prev}\n$ ${command}\n${data.output}\n`);
      setCommand('');
    } catch (err) {
      setOutput((prev) => `${prev}\nError: ${String(err)}`);
    } finally {
      setRunning(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-4">
        <div>
          <h1 className="font-display text-2xl text-cyan">Terminal Console</h1>
          <p className="text-white/70">Run lightweight administrative commands (mocked by default).</p>
        </div>

        <div className="glass-card p-4">
          <form onSubmit={runCommand} className="mb-3">
            <input value={command} onChange={(e) => setCommand(e.target.value)} placeholder="Enter command (e.g. status)" className="w-full p-2 rounded bg-black/20 border border-white/10 text-white" />
            <div className="mt-2">
              <button type="submit" disabled={running} className="px-3 py-2 rounded bg-cyan text-black font-semibold">{running ? 'Running...' : 'Run'}</button>
            </div>
          </form>

          <pre className="bg-black/10 p-3 rounded text-sm text-white/80 h-60 overflow-auto">{output || 'Console output will appear here.'}</pre>
        </div>
      </div>
    </AppShell>
  );
}
