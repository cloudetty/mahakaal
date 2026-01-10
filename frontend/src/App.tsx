import { useState, useRef, useEffect } from 'react';
import './App.css';

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

type ChatSession = {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
};

type ThinkingState = {
  isActive: boolean;
  message: string;
  icon: string;
  color: string;
};

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [thinkingState, setThinkingState] = useState<ThinkingState>({
    isActive: false,
    message: '',
    icon: '',
    color: ''
  });
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentTime, setCurrentTime] = useState('');
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Chicago time update
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const chicagoTime = now.toLocaleTimeString('en-US', {
        timeZone: 'America/Chicago',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      });
      setCurrentTime(chicagoTime);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    checkAuthStatus();
    loadChatSessions();
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

  const loadChatSessions = async () => {
    try {
      const res = await fetch('http://localhost:8000/chat/sessions');
      const data = await res.json();
      setChatSessions(data);
    } catch (e) {
      console.error("Failed to load sessions", e);
    }
  };

  const loadChatSession = async (sessionId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/chat/sessions/${sessionId}`);
      const data = await res.json();
      setMessages(data.messages || []);
      setCurrentSessionId(sessionId);
      setLogs([]);
      setSidebarOpen(false);
    } catch (e) {
      console.error("Failed to load session", e);
    }
  };

  const createNewChat = async () => {
    try {
      const res = await fetch('http://localhost:8000/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: `Chat ${new Date().toLocaleString()}` })
      });
      const data = await res.json();
      setCurrentSessionId(data.id);
      setMessages([]);
      setLogs([]);
      loadChatSessions();
      setSidebarOpen(false);
    } catch (e) {
      console.error("Failed to create session", e);
    }
  };

  const deleteChatSession = async (sessionId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await fetch(`http://localhost:8000/chat/sessions/${sessionId}`, {
        method: 'DELETE'
      });
      if (currentSessionId === sessionId) {
        setMessages([]);
        setCurrentSessionId(null);
      }
      loadChatSessions();
    } catch (error) {
      console.error("Failed to delete session", error);
    }
  };

  const saveMessageToDB = async (message: Message) => {
    if (!currentSessionId) return;

    try {
      await fetch('http://localhost:8000/chat/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId,
          role: message.role,
          content: message.content,
          tool_call_id: message.tool_call_id,
          tool_calls: message.tool_calls,
          name: message.name
        })
      });
    } catch (e) {
      console.error("Failed to save message", e);
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

  const updateThinkingState = (content: string) => {
    const lowerContent = content.toLowerCase();

    if (lowerContent.includes('calendar') || lowerContent.includes('scheduling')) {
      if (lowerContent.includes('creating') || lowerContent.includes('schedule')) {
        setThinkingState({
          isActive: true,
          message: '📅 Creating Calendar Event...',
          icon: '📅',
          color: 'rgba(59, 130, 246, 0.8)'
        });
      } else if (lowerContent.includes('updating') || lowerContent.includes('modifying')) {
        setThinkingState({
          isActive: true,
          message: '✏️ Updating Calendar...',
          icon: '✏️',
          color: 'rgba(168, 85, 247, 0.8)'
        });
      } else if (lowerContent.includes('searching') || lowerContent.includes('finding')) {
        setThinkingState({
          isActive: true,
          message: '🔍 Searching Calendar...',
          icon: '🔍',
          color: 'rgba(34, 197, 94, 0.8)'
        });
      } else {
        setThinkingState({
          isActive: true,
          message: '📅 Working with Calendar...',
          icon: '📅',
          color: 'rgba(59, 130, 246, 0.8)'
        });
      }
    } else if (lowerContent.includes('skill') || lowerContent.includes('tool')) {
      setThinkingState({
        isActive: true,
        message: '⚡ Executing Skill...',
        icon: '⚡',
        color: 'rgba(255, 215, 0, 0.8)'
      });
    } else {
      setThinkingState({
        isActive: true,
        message: '🤔 Thinking...',
        icon: '🤔',
        color: 'rgba(107, 70, 193, 0.8)'
      });
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Create new session if none exists
    if (!currentSessionId) {
      await createNewChat();
    }

    const newMessages: Message[] = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);

    // Save user message
    await saveMessageToDB({ role: 'user', content: input });

    setInput('');
    setThinkingState({
      isActive: true,
      message: '🤔 Thinking...',
      icon: '🤔',
      color: 'rgba(107, 70, 193, 0.8)'
    });
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
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);

            if (event.type === 'status') {
              addLog('status', event.content);
              updateThinkingState(event.content);
            } else if (event.type === 'log') {
              addLog('log', event.content, event.data);
              updateThinkingState(event.content);
            } else if (event.type === 'history_append') {
              const msg = event.data;
              setMessages(prev => [...prev, msg]);
              await saveMessageToDB(msg);
            } else if (event.type === 'answer') {
              currentAnswer = event.content;
              setMessages(prev => {
                const last = prev[prev.length - 1];
                const answerMsg = { role: 'assistant' as const, content: currentAnswer };
                if (last?.role === 'assistant' && last.content !== null) {
                  return [...prev.slice(0, -1), answerMsg];
                } else {
                  saveMessageToDB(answerMsg);
                  return [...prev, answerMsg];
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
      loadChatSessions(); // Refresh session list

    } catch (error) {
      addLog('error', String(error));
    } finally {
      setThinkingState({ isActive: false, message: '', icon: '', color: '' });
    }
  };

  return (
    <div className="flex h-screen w-full bg-void-black text-gray-300 font-sans overflow-hidden">

      {/* Chat History Sidebar */}
      <div className={`${sidebarOpen ? 'chat-sidebar' : 'chat-sidebar-collapsed'}`}>
        <div className="p-4 border-b border-void-gray">
          <button
            onClick={createNewChat}
            className="w-full bg-divine-gold/10 hover:bg-divine-gold/20 text-divine-gold border border-divine-gold/30 py-2 px-4 rounded-lg font-mono text-sm transition-all"
          >
            + New Chat
          </button>
        </div>
        <div className="overflow-y-auto flex-1">
          {chatSessions.map((session) => (
            <div
              key={session.id}
              onClick={() => loadChatSession(session.id)}
              className={`chat-session-item ${currentSessionId === session.id ? 'active' : ''}`}
            >
              <div className="text-sm text-gray-300 truncate">{session.title}</div>
              <div className="flex justify-between items-center mt-1">
                <span className="text-xs text-gray-500 font-mono">
                  {session.message_count || 0} msgs
                </span>
                <button
                  onClick={(e) => deleteChatSession(session.id, e)}
                  className="text-red-400 hover:text-red-300 text-xs"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Left: Chat Panel */}
      <div className="flex-1 flex flex-col border-r border-void-gray">
        <header className="glass-header p-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-divine-gold hover:text-white text-2xl transition-colors"
            >
              ☰
            </button>
            <div>
              <h1 className="text-xl font-bold tracking-widest text-divine-gold uppercase">Mahakaal</h1>
              <span className="text-xs text-gray-500 font-mono">v1.0.0 // EXECUTIVE_AGENT</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="time-display">
              🕐 {currentTime} <span className="text-xs opacity-60">Chicago</span>
            </div>
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

        <div className="flex-1 overflow-y-auto p-6 space-y-6" ref={scrollRef}>
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center opacity-30">
              <div className="text-center">
                <div className="text-6xl mb-4">⏳</div>
                <p className="text-lg">Time flows. I await your command.</p>
                <p className="text-sm text-gray-500 mt-2">Chicago Time: {currentTime}</p>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            msg.role !== 'tool' && (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}>
                  {msg.role === 'assistant' && (
                    <div className="text-xs text-divine-gold/50 mb-2 font-mono uppercase">Mahakaal</div>
                  )}
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              </div>
            )
          ))}

          {thinkingState.isActive && (
            <div className="flex justify-start">
              <div className="thinking-indicator thinking-glow" style={{ borderColor: thinkingState.color }}>
                <div className="thinking-spinner"></div>
                <span className="text-sm font-mono" style={{ color: thinkingState.color }}>
                  {thinkingState.message}
                </span>
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
              className="chat-input w-full rounded-lg p-4 pr-12 text-white font-mono"
            />
            <button
              onClick={sendMessage}
              disabled={thinkingState.isActive}
              className="absolute right-2 top-2 bottom-2 px-4 text-divine-gold hover:text-white disabled:opacity-50 transition-colors"
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