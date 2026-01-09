import { useState, useRef, useEffect } from 'react';

// Types
type Message = {
  role: 'user' | 'assistant' | 'tool';
  content: string | null;
  tool_call_id?: string;
  name?: string;
  tool_calls?: any[];
};

type Log = {
  type: 'status' | 'log' | 'error';
  content: string;
  data?: any;
  timestamp: string;
};

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    checkAuthStatus();
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, logs]);

  const checkAuthStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/auth/status');
      const data = await res.json();
      setIsAuthenticated(data.authenticated);
    } catch (e) {
      console.error("Auth check failed", e);
    }
  };

  const handleConnect = async () => {
    try {
      const res = await fetch('http://localhost:8000/auth/login');
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (e) {
      addLog('error', "Failed to initiate login");
    }
  };

  const addLog = (type: Log['type'], content: string, data?: any) => {
    setLogs(prev => [...prev, {
      type,
      content,
      data,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    // IMPORTANT: Users messages always have non-null content
    const newMessages: Message[] = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setIsThinking(true);
    addLog('status', 'Sending request to Agent...');

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let currentAnswer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);

            if (event.type === 'status') {
              addLog('status', event.content);
            } else if (event.type === 'log') {
              addLog('log', event.content, event.data);
            } else if (event.type === 'history_append') {
              // Backend sent a hidden history item (tool call or result)
              // We add it to state so it's included in next request
              const msg = event.data;
              setMessages(prev => [...prev, msg]);
            } else if (event.type === 'answer') {
              currentAnswer = event.content;
              setMessages(prev => {
                // Check if last message is assistant, if so update it, else add it
                const last = prev[prev.length - 1];
                if (last.role === 'assistant' && last.content !== null) {
                  return [...prev.slice(0, -1), { role: 'assistant', content: currentAnswer }];
                } else {
                  return [...prev, { role: 'assistant', content: currentAnswer }];
                }
              });
            } else if (event.type === 'error') {
              addLog('error', event.content);
            }
          } catch (e) {
            console.error("Parse error", e);
          }
        }
      }

      addLog('status', 'Agent finished.');

    } catch (error) {
      addLog('error', String(error));
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-void-black text-gray-300 font-sans overflow-hidden">

      {/* Left: Chat Panel */}
      <div className="w-3/5 flex flex-col border-r border-void-gray">
        <header className="p-4 border-b border-void-gray flex justify-between items-center bg-void-black/50 backdrop-blur">
          <div>
            <h1 className="text-xl font-bold tracking-widest text-divine-gold uppercase">Mahakaal</h1>
            <span className="text-xs text-gray-500 font-mono">v1.0.0 // EXECUTIVE_AGENT</span>
          </div>
          <div>
            {isAuthenticated ? (
              <span className="text-xs font-mono text-terminal-green border border-terminal-green/30 px-2 py-1 rounded bg-terminal-green/10">
                ● Calendar Active
              </span>
            ) : (
              <button
                onClick={handleConnect}
                className="text-xs font-mono text-divine-gold border border-divine-gold/30 px-3 py-1 rounded hover:bg-divine-gold/10 transition-colors"
              >
                + Connect Calendar
              </button>
            )}
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-void-gray" ref={scrollRef}>
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center opacity-30">
              <div className="text-center">
                <div className="text-6xl mb-4">⏳</div>
                <p>Time flows. I await your command.</p>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-lg ${msg.role === 'user'
                ? 'bg-void-gray text-white border border-gray-700'
                : 'bg-black border border-divine-gold/30 text-divine-gold shadow-[0_0_15px_rgba(255,215,0,0.1)]'
                }`}>
                {msg.role === 'assistant' && (
                  <div className="text-xs text-divine-gold/50 mb-1 font-mono uppercase">Mahakaal</div>
                )}
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
            </div>
          ))}

          {isThinking && (
            <div className="flex justify-start animate-pulse">
              <div className="bg-black border border-divine-gold/10 p-4 rounded-lg">
                <span className="text-divine-gold text-sm font-mono">Thinking...</span>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-void-gray bg-void-black">
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Command the flow of time..."
              className="w-full bg-void-gray border border-gray-700 rounded-md p-4 pr-12 text-white focus:outline-none focus:border-divine-gold transition-colors font-mono"
            />
            <button
              onClick={sendMessage}
              disabled={isThinking}
              className="absolute right-2 top-2 bottom-2 px-4 text-divine-gold hover:text-white disabled:opacity-50"
            >
              ➤
            </button>
          </div>
        </div>
      </div>

      {/* Right: Brain Panel */}
      <div className="w-2/5 flex flex-col bg-[#0a0a0a]">
        <header className="p-4 border-b border-void-gray bg-void-black">
          <h2 className="text-sm font-mono text-terminal-green uppercase flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-terminal-green animate-pulse"></span>
            Agent Neural Stream
          </h2>
        </header>

        <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-3">
          {logs.map((log, i) => (
            <div key={i} className={`p-3 border-l-2 rounded-r ${log.type === 'status' ? 'border-gray-500 text-gray-400' :
              log.type === 'error' ? 'border-red-500 text-red-400 bg-red-900/10' :
                'border-terminal-green text-terminal-green bg-terminal-green/5'
              }`}>
              <div className="flex justify-between opacity-50 mb-1">
                <span>[{log.timestamp}]</span>
                <span className="uppercase">{log.type}</span>
              </div>
              <div className="font-bold">{log.content}</div>
              {log.data && (
                <pre className="mt-2 p-2 bg-black/50 overflow-x-auto text-gray-300">
                  {JSON.stringify(log.data, null, 2)}
                </pre>
              )}
            </div>
          ))}
          {logs.length === 0 && (
            <div className="text-gray-600 italic text-center mt-10">Neural stream idle...</div>
          )}
        </div>
      </div>

    </div>
  )
}

export default App