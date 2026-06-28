import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Timeline from './Timeline';
import SystemStatus from './SystemStatus';

function Dashboard() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const token = localStorage.getItem('token');
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setIsLoading(true);

    const assistantMessage = { role: 'assistant', content: '', sources: [] };
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
            } else if (data.sources) {
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  sources: data.sources
                };
                return updated;
              });
            } else if (data.error) {
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  content: `Error: ${data.error}`
                };
                return updated;
              });
            }
          }
        }
      }
    } catch (error) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content: 'Failed to connect to server'
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
          content: `Document uploaded successfully! ${data.memories_created} memories extracted.`
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Failed to upload document'
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Failed to connect to server'
      }]);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Navigation */}
      <nav className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <h1 className="text-2xl font-bold text-white">Memento AI</h1>
            <div className="flex gap-4">
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'chat'
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:bg-slate-700'
                }`}
              >
                Chat
              </button>
              <button
                onClick={() => setActiveTab('timeline')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'timeline'
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:bg-slate-700'
                }`}
              >
                Timeline
              </button>
              <button
                onClick={() => setActiveTab('status')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'status'
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:bg-slate-700'
                }`}
              >
                System Status
              </button>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-300">{user.name || 'User'}</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'chat' && (
          <div className="max-w-4xl mx-auto">
            {/* Chat Messages */}
            <div className="bg-slate-800 rounded-xl p-6 mb-4 h-[500px] overflow-y-auto">
              {messages.length === 0 ? (
                <div className="text-center text-gray-400 py-20">
                  <p className="text-xl mb-2">Welcome to Memento AI</p>
                  <p>Start a conversation to interact with your memories</p>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <div key={idx} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                    <div className={`inline-block max-w-[80%] p-4 rounded-lg ${
                      msg.role === 'user' 
                        ? 'bg-purple-600 text-white' 
                        : 'bg-slate-700 text-gray-200'
                    }`}>
                      {msg.content || (isLoading && idx === messages.length - 1 ? 'Thinking...' : '')}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-600">
                          <p className="text-xs text-gray-400 mb-1">Sources:</p>
                          <ul className="text-xs">
                            {msg.sources.map((source, sidx) => (
                              <li key={sidx} className="text-purple-400">
                                {source.document || source.memory}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Input */}
            <div className="flex gap-4">
              <input
                type="file"
                onChange={handleFileUpload}
                disabled={uploading || isLoading}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className={`px-6 py-3 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition cursor-pointer ${
                  uploading || isLoading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {uploading ? 'Uploading...' : 'Upload Document'}
              </label>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </div>
        )}

        {activeTab === 'timeline' && <Timeline />}
        {activeTab === 'status' && <SystemStatus />}
      </div>
    </div>
  );
}

export default Dashboard;
