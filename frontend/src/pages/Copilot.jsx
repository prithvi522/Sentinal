import { useRef, useState } from 'react';
import AppShell from '../components/AppShell';
import TypingText from '../components/TypingText';
import { api } from '../lib/api';

const quickCommands = [
  'Analyze this threat',
  'Explain this vulnerability',
  'Generate secure code',
  'How severe is this attack?',
];

export default function Copilot() {
  const [message, setMessage] = useState('Analyze this threat pattern for immediate containment actions.');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [provider, setProvider] = useState('openai');
  const endRef = useRef(null);

  async function ask() {
    const userMessage = message.trim();
    if (!userMessage || loading) return;

    setLoading(true);
    setError('');
    try {
      const nextMessages = [...messages, { role: 'user', content: userMessage }];
      setMessages(nextMessages);
      setMessage('');
      const { data } = await api.post(
        '/copilot/chat',
        {
          message: userMessage,
          context: { module: 'soc_assistant' },
          history: nextMessages,
          provider,
        },
        { timeout: 60000 }
      );
      setMessages((current) => [...current, { role: 'assistant', content: data.answer, provider: data.provider, status: data.status, reason: data.reason }]);
      requestAnimationFrame(() => endRef.current?.scrollIntoView({ behavior: 'smooth' }));
    } catch (requestError) {
      const isTimeout = requestError?.code === 'ECONNABORTED' || /timeout/i.test(requestError?.message || '');
      setError(
        isTimeout
          ? 'The Copilot request took longer than 60 seconds. The backend AI provider is slow or unavailable right now.'
          : requestError?.response?.data?.detail || requestError?.message || 'Copilot request failed.'
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-4">
        <h1 className="font-display text-3xl text-cyan">AI Security Copilot Chat</h1>
        <div className="glass-card p-4 space-y-4">
          <div className="flex flex-wrap items-center gap-2 text-sm text-white/70">
            <span className="uppercase tracking-[0.2em] text-white/50">Provider</span>
            <button onClick={() => setProvider('auto')} className={`px-3 py-1 rounded border ${provider === 'auto' ? 'border-cyan text-cyan bg-cyan/10' : 'border-white/15 hover:border-cyan/40'}`}>
              Auto
            </button>
            <button onClick={() => setProvider('openai')} className={`px-3 py-1 rounded border ${provider === 'openai' ? 'border-cyan text-cyan bg-cyan/10' : 'border-white/15 hover:border-cyan/40'}`}>
              OpenAI
            </button>
            <button onClick={() => setProvider('gemini')} className={`px-3 py-1 rounded border ${provider === 'gemini' ? 'border-cyan text-cyan bg-cyan/10' : 'border-white/15 hover:border-cyan/40'}`}>
              Gemini
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {quickCommands.map((cmd) => (
              <button key={cmd} onClick={() => setMessage(cmd)} className="px-3 py-1 rounded border border-cyan/40 text-cyan hover:bg-cyan/10 text-sm">
                {cmd}
              </button>
            ))}
          </div>
          {error ? <div className="rounded border border-red-400/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">{error}</div> : null}
          <div className="space-y-3 max-h-[52vh] overflow-y-auto pr-1">
            {messages.length === 0 ? (
              <p className="text-white/60">Start a conversation. Ask for containment steps, explain a vulnerability, or request secure code guidance.</p>
            ) : null}

            {messages.map((entry, index) => (
              <div key={`${entry.role}-${index}`} className={`flex ${entry.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-3xl rounded-2xl px-4 py-3 border ${entry.role === 'user' ? 'bg-cyan/10 border-cyan/30 text-white' : 'bg-black/35 border-lime/20 text-lime'}`}>
                  {entry.role === 'assistant' ? (
                    <div className="mb-2 text-[11px] uppercase tracking-[0.2em] text-lime/70 flex flex-wrap gap-2">
                      <span>{entry.provider === 'openai' ? 'OpenAI' : entry.provider === 'gemini' ? 'Gemini' : 'Fallback'}</span>
                      {entry.status ? <span className={entry.status === 'ready' ? 'text-emerald-300' : 'text-amber-300'}>{entry.status === 'ready' ? 'Live' : 'Fallback'}</span> : null}
                      {entry.reason ? <span className="text-white/40">{entry.reason}</span> : null}
                    </div>
                  ) : null}
                  {entry.role === 'assistant' ? <TypingText text={entry.content} /> : <p className="whitespace-pre-wrap">{entry.content}</p>}
                </div>
              </div>
            ))}
            <div ref={endRef} />
          </div>

          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                ask();
              }
            }}
            rows={4}
            className="w-full p-3 bg-black/40 rounded border border-cyan/30"
            placeholder="Ask the security copilot something..."
          />
          <button onClick={ask} disabled={loading} className="px-4 py-2 rounded bg-cyan text-black font-semibold">
            {loading ? 'Copilot is typing...' : 'Send'}
          </button>
        </div>
      </div>
    </AppShell>
  );
}