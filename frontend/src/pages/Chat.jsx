import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import ChatMessage from '../components/ChatMessage';

function Chat() {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const fetchHistory = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/conversations?limit=20', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        // Convert database conversations to message objects (sorted chronologically)
        const loadedMessages = [];
        const sorted = [...data].reverse();
        for (const conv of sorted) {
          loadedMessages.push({
            role: 'user',
            content: conv.question,
            timestamp: conv.timestamp
          });
          loadedMessages.push({
            role: 'assistant',
            content: conv.answer,
            timestamp: conv.timestamp
          });
        }
        setMessages(loadedMessages);
      }
    } catch (err) {
      console.error('Failed to fetch chat history:', err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const token = localStorage.getItem('token');
    const userMessage = { role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setIsLoading(true);

    const assistantMessage = { role: 'assistant', content: '', sources: [], timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message: userInput }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.token) {
                fullContent += data.token;
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    ...updated[updated.length - 1],
                    content: fullContent
                  };
                  return updated;
                });
              }
              
              if (data.sources) {
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    ...updated[updated.length - 1],
                    sources: data.sources
                  };
                  return updated;
                });
              }
              
              if (data.metrics) {
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    ...updated[updated.length - 1],
                    metrics: data.metrics
                  };
                  return updated;
                });
              }
              
              if (data.error) {
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    ...updated[updated.length - 1],
                    content: `Error: ${data.error}`
                  };
                  return updated;
                });
              }
            } catch (e) {
              // Ignore partial JSON chunks during streaming
            }
          }
        }
      }
    } catch (error) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content: t('chat.connectionError')
        };
        return updated;
      });
    } finally {
      setIsLoading(false);
    }
  };


  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const token = localStorage.getItem('token');
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `${t('chat.documentUploaded')} ${data.memories_created || 0} ${t('chat.memoriesExtracted')}.`,
          timestamp: new Date().toISOString()
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: t('chat.uploadFailed'),
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: t('chat.connectionError'),
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col lg:ml-64">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title={t('chat.title')} />
        
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-4xl mx-auto">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-20">
                  <div className="text-6xl mb-4">💬</div>
                  <h2 className="text-2xl font-semibold text-white mb-2">{t('chat.startConversation')}</h2>
                  <p className="text-gray-400 mb-6">{t('chat.description')}</p>
                  <div className="flex gap-4">
                    <button
                      onClick={() => setInput('What are my recent memories?')}
                      className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-gray-300 hover:border-purple-500/50 transition"
                    >
                      {t('chat.recentMemories')}
                    </button>
                    <button
                      onClick={() => setInput('Summarize my documents')}
                      className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-gray-300 hover:border-purple-500/50 transition"
                    >
                      {t('chat.summarizeDocuments')}
                    </button>
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
                    />
                  ))}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-slate-700 p-4 bg-slate-800">
            <div className="max-w-4xl mx-auto flex gap-4">
              <div className="flex-1 flex gap-3">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  disabled={uploading || isLoading}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className={`px-4 py-3 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition cursor-pointer flex items-center gap-2 ${
                    uploading || isLoading ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  <span className="text-xl">📎</span>
                  <span className="hidden sm:inline">{uploading ? t('chat.uploading') : t('chat.upload')}</span>
                </label>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder={t('chat.placeholder')}
                  disabled={isLoading}
                  className="flex-1 px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50"
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <span>{t('chat.send')}</span>
                <span className="text-xl">➤</span>
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Chat;
