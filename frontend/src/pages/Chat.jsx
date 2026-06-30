import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Send, Paperclip, ChevronDown, ChevronUp, MessageSquare, 
  Sparkles, Zap, BookOpen, Brain, Plus, Trash2, Edit2, Pin, X, Search, StopCircle 
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import ChatMessage from '../components/ChatMessage';
import BackgroundLayout from '../components/BackgroundLayout';
import { backgroundImages } from '../constants/backgrounds';

import API_BASE from '../config/api';

function Chat() {
  const { t, i18n } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const [typingIndicator, setTypingIndicator] = useState(false);
  const [progress, setProgress] = useState(null);
  const [followups, setFollowups] = useState([]);

  // Chat Session states
  const [currentSessionId, setCurrentSessionId] = useState(() => localStorage.getItem('currentSessionId') || null);
  const [sessions, setSessions] = useState([]);
  const [sessionSearch, setSessionSearch] = useState('');
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const messagesEndRef = useRef(null);
  const messagesAreaRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const lastUserMessageRef = useRef('');
  const abortControllerRef = useRef(null);

  const scrollToBottom = useCallback((force = false) => {
    if (force || !showScrollBtn) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [showScrollBtn]);

  // Load session list and current chat on startup
  useEffect(() => {
    fetchSessions().then(loadedSessions => {
      if (loadedSessions && loadedSessions.length > 0) {
        const savedId = localStorage.getItem('currentSessionId');
        const exists = loadedSessions.some(s => s.session_id === savedId);
        if (savedId && exists) {
          selectSession(savedId);
        } else {
          selectSession(loadedSessions[0].session_id);
        }
      } else {
        handleNewChat();
      }
    });
  }, []);

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

  const fetchSessions = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_BASE}/conversations/sessions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
        return data;
      }
    } catch (e) {
      console.error('Failed to fetch chat sessions:', e);
    }
    return [];
  };

  const selectSession = async (session_id) => {
    if (!session_id) return;
    setCurrentSessionId(session_id);
    localStorage.setItem('currentSessionId', session_id);
    setFollowups([]);
    setMessages([]);
    
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_BASE}/conversations/session/${session_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
        if (data.length >= 2) {
          lastUserMessageRef.current = data[data.length - 2].content;
        }
      }
    } catch (e) {
      console.error('Failed to fetch session messages:', e);
    }
  };

  const handleNewChat = () => {
    setCurrentSessionId(null);
    localStorage.removeItem('currentSessionId');
    setMessages([]);
    setFollowups([]);
    if (inputRef.current) inputRef.current.focus();
  };

  const handleClearChat = async () => {
    if (!currentSessionId) return;
    if (!confirm(t('chat.clearConfirm', 'Are you sure you want to clear the messages in this chat session?'))) return;
    
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_BASE}/conversations/session/${currentSessionId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setMessages([]);
        setFollowups([]);
        fetchSessions();
      }
    } catch (e) {
      console.error('Failed to clear conversation turns:', e);
    }
  };

  const handleDeleteSession = async (session_id) => {
    if (!confirm(t('chat.deleteConfirm', 'Are you sure you want to delete this entire chat session?'))) return;
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_BASE}/conversations/session/${session_id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        if (session_id === currentSessionId) {
          handleNewChat();
        }
        fetchSessions();
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  const handlePinToggle = async (session_id, is_pinned) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_BASE}/conversations/session/${session_id}/pin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ is_pinned: !is_pinned })
      });
      if (res.ok) {
        fetchSessions();
      }
    } catch (e) {
      console.error('Failed to toggle pin:', e);
    }
  };

  const startRename = (session_id, currentTitle) => {
    setEditingSessionId(session_id);
    setEditTitle(currentTitle);
  };

  const saveRename = async () => {
    if (!editingSessionId || !editTitle.trim()) {
      setEditingSessionId(null);
      return;
    }
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_BASE}/conversations/session/${editingSessionId}/rename`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ title: editTitle.trim() })
      });
      if (res.ok) {
        fetchSessions();
      }
    } catch (e) {
      console.error('Failed to rename session:', e);
    } finally {
      setEditingSessionId(null);
    }
  };

  const handleStopGenerating = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  const submitChatMessage = async (text, isContinue = false, editIndex = null) => {
    if (isLoading) return;
    
    const token = localStorage.getItem('token');
    const targetMessage = text.trim();
    if (!targetMessage && !isContinue) return;

    let updatedMessages = [...messages];
    
    if (isContinue) {
      setIsLoading(true);
      setTypingIndicator(true);
    } else if (editIndex !== null) {
      const sliced = messages.slice(0, editIndex);
      const userMsg = { role: 'user', content: targetMessage, timestamp: new Date().toISOString() };
      const aiMsg  = { role: 'assistant', content: '', sources: [], timestamp: new Date().toISOString() };
      updatedMessages = [...sliced, userMsg, aiMsg];
      setMessages(updatedMessages);
      setIsLoading(true);
    } else {
      const userMsg = { role: 'user', content: targetMessage, timestamp: new Date().toISOString() };
      const aiMsg  = { role: 'assistant', content: '', sources: [], timestamp: new Date().toISOString() };
      updatedMessages = [...updatedMessages, userMsg, aiMsg];
      setMessages(updatedMessages);
      setInput('');
      setIsLoading(true);
      scrollToBottom(true);
    }

    if (!isContinue) {
      lastUserMessageRef.current = targetMessage;
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: targetMessage,
          session_id: currentSessionId,
          language: i18n.language || 'en',
          continue_generating: isContinue
        }),
        signal: controller.signal
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = isContinue ? messages[messages.length - 1]?.content || '' : '';

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
              if (data.session_id) {
                setCurrentSessionId(data.session_id);
                localStorage.setItem('currentSessionId', data.session_id);
                fetchSessions();
              }
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
      if (err.name === 'AbortError') {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: updated[updated.length - 1].content + "\n\n*(Generation stopped)*"
          };
          return updated;
        });
      } else {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: `⚠️ Connection error: ${err.message}.`,
          };
          return updated;
        });
      }
    } finally {
      setIsLoading(false);
      setTypingIndicator(false);
      setProgress(null);
      abortControllerRef.current = null;
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitChatMessage(input);
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
            content: `✅ **${file.name}** processed successfully!\n\n📊 Memories extracted and saved to your knowledge base.\n\nYou can now ask me questions about this document.`,
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

  const filteredSessions = sessions.filter(s =>
    (s.title || '').toLowerCase().includes(sessionSearch.toLowerCase())
  );

  const isEmpty = messages.length === 0;

  return (
    <BackgroundLayout image={backgroundImages.chat}>
      <div className="min-h-screen flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <div className="flex-1 flex flex-col lg:ml-64 min-h-screen">
          <Navbar onMenuClick={() => setSidebarOpen(true)} title={t('chat.title')} subtitle="Ask anything about your memories" />

          <main className="flex-1 flex overflow-hidden">
            {/* Conversation History Panel */}
            <div className="w-72 border-r border-white/5 bg-slate-950/20 flex flex-col shrink-0 hidden lg:flex">
              <div className="p-3 border-b border-white/5 space-y-2">
                <div className="flex gap-2">
                  <button
                    onClick={handleNewChat}
                    className="flex-1 py-2 px-3 rounded-xl bg-purple-600/20 border border-purple-500/30 text-purple-300 hover:bg-purple-600/30 transition flex items-center justify-center gap-1.5 font-medium text-xs shadow-md"
                    title="Start fresh conversation"
                  >
                    <Plus size={13} />
                    New Chat
                  </button>
                  <button
                    onClick={handleClearChat}
                    disabled={!currentSessionId}
                    className="py-2 px-3 rounded-xl bg-slate-800/40 border border-white/10 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 transition flex items-center justify-center disabled:opacity-40"
                    title="Clear current session"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 text-slate-500" size={13} />
                  <input
                    type="text"
                    placeholder="Search conversations..."
                    value={sessionSearch}
                    onChange={e => setSessionSearch(e.target.value)}
                    className="w-full pl-8 pr-3 py-2 bg-slate-800/40 border border-white/5 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
                  />
                </div>
              </div>

              {/* Session list scrollbox */}
              <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {filteredSessions.map(session => {
                  const isSelected = session.session_id === currentSessionId;
                  return (
                    <div
                      key={session.session_id}
                      className={`group relative flex items-center justify-between p-2.5 rounded-xl cursor-pointer transition ${
                        isSelected 
                          ? 'bg-purple-600/20 border border-purple-500/20 text-white' 
                          : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                      }`}
                    >
                      <div className="flex items-center gap-2 min-w-0 flex-1" onClick={() => selectSession(session.session_id)}>
                        <MessageSquare size={13} className="shrink-0 text-slate-500" />
                        {editingSessionId === session.session_id ? (
                          <input
                            type="text"
                            value={editTitle}
                            onChange={e => setEditTitle(e.target.value)}
                            onBlur={saveRename}
                            onKeyDown={e => e.key === 'Enter' && saveRename()}
                            autoFocus
                            onClick={e => e.stopPropagation()}
                            className="bg-slate-800 text-white text-xs border border-purple-500 rounded px-1.5 py-0.5 focus:outline-none w-full"
                          />
                        ) : (
                          <span className="text-xs truncate font-medium flex-1">
                            {session.title || 'Untitled Chat'}
                          </span>
                        )}
                      </div>

                      {editingSessionId !== session.session_id && (
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-1 bg-gradient-to-l from-slate-950 via-slate-950 pl-2 shrink-0">
                          <button
                            onClick={(e) => { e.stopPropagation(); handlePinToggle(session.session_id, session.is_pinned); }}
                            className={`p-1 rounded hover:bg-white/10 ${session.is_pinned ? 'text-amber-400' : 'text-slate-500'}`}
                            title={session.is_pinned ? 'Unpin' : 'Pin'}
                          >
                            <Pin size={10} className={session.is_pinned ? 'fill-current' : ''} />
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); startRename(session.session_id, session.title); }}
                            className="p-1 rounded text-slate-500 hover:bg-white/10 hover:text-slate-200"
                            title="Rename"
                          >
                            <Edit2 size={10} />
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleDeleteSession(session.session_id); }}
                            className="p-1 rounded text-slate-500 hover:bg-white/10 hover:text-rose-400"
                            title="Delete"
                          >
                            <Trash2 size={10} />
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Chat Pane */}
            <div className="flex-1 flex flex-col overflow-hidden relative">
              <div ref={messagesAreaRef} className="flex-1 overflow-y-auto px-4 py-6">
                <div className="max-w-3xl mx-auto">
                  {isEmpty ? (
                    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center animate-fade-in">
                      <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500/20 to-violet-600/20 border border-purple-500/30 flex items-center justify-center mb-6 animate-float">
                        <MessageSquare size={36} className="text-purple-400" />
                      </div>
                      <h2 className="text-2xl font-bold text-white mb-2">{t('chat.startConversation')}</h2>
                      <p className="text-slate-400 mb-8 max-w-sm">
                        {t('chat.description')}
                      </p>
                    </div>
                  ) : (
                    <>
                      {messages.map((msg, idx) => (
                        <ChatMessage
                          key={idx}
                          message={msg}
                          isLast={idx === messages.length - 1}
                          isLoading={isLoading}
                          onRegenerate={idx === messages.length - 1 && msg.role === 'assistant' ? () => submitChatMessage(lastUserMessageRef.current) : null}
                          onEdit={msg.role === 'user' ? (newContent) => submitChatMessage(newContent, false, idx) : null}
                          onContinue={idx === messages.length - 1 && msg.role === 'assistant' ? () => submitChatMessage('[Continue]', true) : null}
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
                                onClick={() => submitChatMessage(followup)}
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

              {showScrollBtn && (
                <button
                  onClick={() => scrollToBottom(true)}
                  className="absolute bottom-28 left-1/2 -translate-x-1/2 z-10 p-2 rounded-full glass border border-purple-500/30 text-purple-400 hover:text-white transition animate-fade-in shadow-lg"
                  aria-label="Scroll to bottom"
                >
                  <ChevronDown size={18} />
                </button>
              )}

              {/* Input section */}
              <div className="glass-navbar border-t border-white/5 px-4 py-4">
                <div className="max-w-3xl mx-auto">
                  <div className="flex items-end gap-3">
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
                        placeholder={t('chat.placeholder')}
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

                    {isLoading ? (
                      <button
                        onClick={handleStopGenerating}
                        className="p-3 rounded-xl bg-rose-600 hover:bg-rose-700 text-white transition flex-shrink-0 shadow-lg shadow-rose-950/40"
                        title="Stop generating"
                      >
                        <StopCircle size={18} />
                      </button>
                    ) : (
                      <button
                        onClick={() => submitChatMessage(input)}
                        disabled={isLoading || !input.trim()}
                        className="p-3 rounded-xl bg-gradient-to-br from-purple-600 to-violet-700 text-white hover:from-purple-500 hover:to-violet-600 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-purple-900/40 hover:shadow-purple-900/60 flex-shrink-0"
                        aria-label="Send message"
                      >
                        <Send size={18} />
                      </button>
                    )}
                  </div>

                  <p className="text-center text-[10px] text-slate-600 mt-2">
                    All processing is done locally · No data leaves your device · Powered by llama.cpp
                  </p>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </BackgroundLayout>
  );
}

export default Chat;
