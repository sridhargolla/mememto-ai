import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Send, Paperclip, ChevronDown, MessageSquare, Sparkles, Zap, BookOpen, Brain } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import ChatMessage from '../components/ChatMessage';
import BackgroundLayout from '../components/BackgroundLayout';
import { backgroundImages } from '../constants/backgrounds';

const API_BASE = '/api';

const SUGGESTIONS = [
  { icon: <Brain size={16} />, text: 'What are my recent memories?' },
  { icon: <BookOpen size={16} />, text: 'Summarize my documents' },
  { icon: <Sparkles size={16} />, text: 'What did I learn this week?' },
  { icon: <Zap size={16} />, text: 'Show my top memories' },
];

function Chat() {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const [typingIndicator, setTypingIndicator] = useState(false);
  const [progress, setProgress] = useState(null);
  const [followups, setFollowups] = useState([]);
  const messagesEndRef = useRef(null);
  const messagesAreaRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const lastUserMessageRef = useRef('');

  const scrollToBottom = useCallback((force = false) => {
    if (force || !showScrollBtn) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [showScrollBtn]);

  useEffect(() => { fetchHistory(); }, []);

  useEffect(() => {
    const area = messagesAreaRef.current;
    if (!area) return;
    const onScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = area;
      setShowScrollBtn(scrollHeight - scrollTop - clientHeight > 100);
    };
    area.addEventListener('scroll', onScroll);
    return () => area.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => scrollToBottom(true), 50);
    }
  }, [messages.length]);

  const fetchHistory = async () => {
    const token = localStorage.getItem('token');
    
    // First, try to load from localStorage for immediate display
    const localMessages = localStorage.getItem('chatMessages');
    if (localMessages) {
      try {
        setMessages(JSON.parse(localMessages));
      } catch (e) {
        console.error('Failed to parse local messages:', e);
      }
    }
    
    // Then fetch from backend
    try {
      const res = await fetch(`${API_BASE}/conversations?limit=20`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        const loaded = [];
        [...data].reverse().forEach(conv => {
          loaded.push({ role: 'user',      content: conv.question, timestamp: conv.timestamp });
          loaded.push({ role: 'assistant', content: conv.answer,   timestamp: conv.timestamp });
        });
        setMessages(loaded);
      }
    } catch (e) {
      console.error('History fetch failed:', e);
    }
  };

  const sendMessage = async (text) => {
    const userInput = (text || input).trim();
    if (!userInput || isLoading) return;

    const token = localStorage.getItem('token');
    lastUserMessageRef.current = userInput;
    const userMsg = { role: 'user', content: userInput, timestamp: new Date().toISOString() };
    const aiMsg  = { role: 'assistant', content: '', sources: [], timestamp: new Date().toISOString() };

    setMessages(prev => [...prev, userMsg, aiMsg]);
    setInput('');
    setIsLoading(true);
    scrollToBottom(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: userInput }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.token) {
              fullContent += data.token;
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = { ...updated[updated.length - 1], content: fullContent };
                return updated;
              });
            }
            if (data.type === 'typing') {
              setTypingIndicator(true);
            }
            if (data.type === 'progress') {
              setProgress(data);
            }
            if (data.sources) {
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = { ...updated[updated.length - 1], sources: data.sources };
                return updated;
              });
            }
            if (data.followups) {
              setFollowups(data.followups);
            }
            if (data.metrics) {
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = { ...updated[updated.length - 1], metrics: data.metrics };
                return updated;
              });
            }
            if (data.done) {
              setTypingIndicator(false);
              setProgress(null);
            }
            if (data.error) {
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = { ...updated[updated.length - 1], content: `⚠️ ${data.error}` };
                return updated;
              });
            }
          } catch { /* ignore partial JSON */ }
        }
      }
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content: `⚠️ Connection error: ${err.message}. Make sure the backend is running on port 8000.`,
        };
        // Save to localStorage on error
        localStorage.setItem('chatMessages', JSON.stringify(updated));
        return updated;
      });
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleRegenerate = () => {
    if (!lastUserMessageRef.current || isLoading) return;
    // Remove last assistant message
    setMessages(prev => prev.slice(0, -1));
    sendMessage(lastUserMessageRef.current);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const token = localStorage.getItem('token');
    setUploading(true);

    const progressMsg = {
      role: 'assistant',
      content: `📎 Uploading **${file.name}**...`,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, progressMsg]);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: `✅ **${file.name}** processed successfully!\n\n📊 **${data.memories_created || 0}** memories extracted and saved to your knowledge base.\n\nYou can now ask me questions about this document.`,
          };
          return updated;
        });
      } else {
        throw new Error(data.detail || 'Upload failed');
      }
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content: `❌ Upload failed: ${err.message}`,
        };
        return updated;
      });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <BackgroundLayout image={backgroundImages.chat}>
      <div className="min-h-screen flex">
        <div className="app-bg" />
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <div className="flex-1 flex flex-col lg:ml-64 min-h-screen">
          <Navbar onMenuClick={() => setSidebarOpen(true)} title="AI Chat" subtitle="Ask anything about your memories" />

          <main className="flex-1 flex flex-col overflow-hidden">
          {/* Messages area */}
          <div
            ref={messagesAreaRef}
            className="flex-1 overflow-y-auto px-4 py-6"
          >
            <div className="max-w-3xl mx-auto">
              {isEmpty ? (
                /* Empty state */
                <div className="flex flex-col items-center justify-center min-h-[60vh] text-center animate-fade-in">
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500/20 to-violet-600/20 border border-purple-500/30 flex items-center justify-center mb-6 animate-float">
                    <MessageSquare size={36} className="text-purple-400" />
                  </div>
                  <h2 className="text-2xl font-bold text-white mb-2">Start a conversation</h2>
                  <p className="text-slate-400 mb-8 max-w-sm">
                    Ask questions about your memories, documents, and personal knowledge base — all processed locally.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-md">
                    {SUGGESTIONS.map((s, i) => (
                      <button
                        key={i}
                        onClick={() => sendMessage(s.text)}
                        className="glass-card p-3 flex items-center gap-3 text-left hover:border-purple-500/40 transition group"
                        style={{ animationDelay: `${i * 80}ms` }}
                      >
                        <span className="text-purple-400 group-hover:scale-110 transition-transform">{s.icon}</span>
                        <span className="text-sm text-slate-300">{s.text}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, idx) => (
                    <ChatMessage
                      key={idx}
                      message={msg}
                      isLast={idx === messages.length - 1}
                      isLoading={isLoading}
                      onRegenerate={idx === messages.length - 1 && msg.role === 'assistant' ? handleRegenerate : null}
                    />
                  ))}
                  {typingIndicator && (
                    <div className="flex items-center gap-2 text-slate-400 text-sm py-4">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                      </div>
                      <span>Memento AI is thinking...</span>
                    </div>
                  )}
                  {progress && (
                    <div className="text-slate-400 text-sm py-2">
                      {progress.message}
                    </div>
                  )}
                  {followups.length > 0 && !isLoading && (
                    <div className="mt-4 pt-4 border-t border-white/10">
                      <p className="text-xs text-slate-500 mb-2">You might also ask:</p>
                      <div className="flex flex-wrap gap-2">
                        {followups.map((followup, i) => (
                          <button
                            key={i}
                            onClick={() => sendMessage(followup)}
                            className="px-3 py-1.5 text-xs glass border border-white/10 text-slate-300 hover:text-purple-400 hover:border-purple-500/40 rounded-lg transition"
                          >
                            {followup}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>
          </div>

          {/* Scroll to bottom button */}
          {showScrollBtn && (
            <button
              onClick={() => scrollToBottom(true)}
              className="absolute bottom-28 left-1/2 -translate-x-1/2 z-10 p-2 rounded-full glass border border-purple-500/30 text-purple-400 hover:text-white transition animate-fade-in shadow-lg"
              aria-label="Scroll to bottom"
            >
              <ChevronDown size={18} />
            </button>
          )}

          {/* Input area */}
          <div className="glass-navbar border-t border-white/5 px-4 py-4">
            <div className="max-w-3xl mx-auto">
              <div className="flex items-end gap-3">
                {/* File upload */}
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  id="chat-file-upload"
                  accept="*/*"
                  onChange={handleFileUpload}
                  disabled={uploading || isLoading}
                />
                <label
                  htmlFor="chat-file-upload"
                  className={`p-3 rounded-xl glass border border-white/10 text-slate-400 hover:text-purple-400 hover:border-purple-500/40 cursor-pointer transition flex-shrink-0 ${
                    uploading || isLoading ? 'opacity-40 pointer-events-none' : ''
                  }`}
                  title="Upload document"
                >
                  <Paperclip size={18} />
                </label>

                {/* Text input */}
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={e => {
                      setInput(e.target.value);
                      e.target.style.height = 'auto';
                      e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px';
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask about your memories... (Enter to send, Shift+Enter for newline)"
                    disabled={isLoading}
                    rows={1}
                    className="w-full px-4 py-3 glass-input rounded-xl text-sm text-white placeholder-slate-500 resize-none focus:ring-2 focus:ring-purple-500/40 disabled:opacity-50 leading-relaxed"
                    style={{ minHeight: '48px', maxHeight: '160px' }}
                    aria-label="Message input"
                  />
                  {input.length > 0 && (
                    <span className="absolute bottom-2 right-3 text-[10px] text-slate-600">
                      {input.length}
                    </span>
                  )}
                </div>

                {/* Send button */}
                <button
                  onClick={() => sendMessage()}
                  disabled={isLoading || !input.trim()}
                  className="p-3 rounded-xl bg-gradient-to-br from-purple-600 to-violet-700 text-white hover:from-purple-500 hover:to-violet-600 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-purple-900/40 hover:shadow-purple-900/60 flex-shrink-0"
                  aria-label="Send message"
                >
                  <Send size={18} />
                </button>
              </div>

              <p className="text-center text-[10px] text-slate-600 mt-2">
                All processing is done locally · No data leaves your device · Powered by llama.cpp
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
    </BackgroundLayout>
  );
}

export default Chat;
