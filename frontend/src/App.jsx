import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { AuthProvider } from './AuthContext'
import ProtectedRoute from './ProtectedRoute'
import Landing from './Landing'
import Login from './Login'
import Signup from './Signup'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Documents from './pages/Documents'
import Memories from './pages/Memories'
import Timeline from './Timeline'
import Privacy from './pages/Privacy'
import Settings from './pages/Settings'
import SystemStatus from './SystemStatus'
import PerformanceDashboard from './PerformanceDashboard'
import './i18n'
import './App.css'


function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    const userInput = input
    setInput('')
    setIsLoading(true)

    // Create empty assistant message for streaming
    const assistantMessage = { role: 'assistant', content: '', sources: [] }
    setMessages(prev => [...prev, assistantMessage])

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),
      })

      if (!response.ok) {
        throw new Error('Network response was not ok')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let fullContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            try {
              const parsed = JSON.parse(data)
              
              if (parsed.error) {
                setMessages(prev => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    content: parsed.error
                  }
                  return newMessages
                })
                break
              }
              
              if (parsed.token) {
                fullContent += parsed.token
                setMessages(prev => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    content: fullContent
                  }
                  return newMessages
                })
              }
              
              if (parsed.sources) {
                setMessages(prev => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    sources: parsed.sources
                  }
                  return newMessages
                })
              }
              
              if (parsed.done) {
                setIsLoading(false)
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => {
        const newMessages = [...prev]
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          content: 'Sorry, something went wrong.'
        }
        return newMessages
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()
      
      if (response.ok) {
        const systemMessage = { 
          role: 'assistant', 
          content: `Successfully processed ${file.filename}. Extracted ${data.memories_created} memories.`,
          sources: []
        }
        setMessages(prev => [...prev, systemMessage])
      } else {
        throw new Error(data.detail || 'Upload failed')
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      const errorMessage = { 
        role: 'assistant', 
        content: `Failed to upload file: ${error.message}`,
        sources: []
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setUploading(false)
      e.target.value = '' // Reset file input
    }
  }

  return (
    <div className="app">
      <div className="chat-container">
        <div className="header">
          <h1>Memento AI</h1>
        </div>
        
        <div className="messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>Start a conversation with Memento AI</p>
            </div>
          )}
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <strong>{message.role === 'user' ? 'You' : 'Memento'}:</strong>
                <p>{message.content || (isLoading && index === messages.length - 1 ? 'Thinking...' : '')}</p>
                {message.sources && message.sources.length > 0 && (
                  <div className="sources">
                    <strong>Sources:</strong>
                    <ul>
                      {message.sources.map((source, idx) => (
                        <li key={idx}>
                          {source.document && <span className="source-icon">📄</span>}
                          <span className="source-text">
                            {source.document && `${source.document} - `}
                            {source.memory}
                          </span>
                          {source.relevance_score !== undefined && (
                            <span className="relevance-score">
                              ({(source.relevance_score * 100).toFixed(0)}%)
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="input-container">
          <input
            type="file"
            id="file-upload"
            accept=".pdf,.txt,.png,.jpg,.jpeg,.gif,.bmp,.tiff,.wav,.mp3"
            onChange={handleFileUpload}
            disabled={uploading || isLoading}
            style={{ display: 'none' }}
          />
          <button
            onClick={() => document.getElementById('file-upload').click()}
            disabled={uploading || isLoading}
            className="upload-button"
            title="Upload file (PDF, TXT, Images, Audio)"
          >
            📎
          </button>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            rows={1}
            disabled={isLoading}
          />
          <button 
            onClick={sendMessage} 
            disabled={isLoading || !input.trim()}
          >
            {uploading ? 'Uploading...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  )
}

function Navigation() {
  const location = useLocation()
  
  return (
    <nav className="nav-bar">
      <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
        💬 Chat
      </Link>
      <Link to="/timeline" className={`nav-link ${location.pathname === '/timeline' ? 'active' : ''}`}>
        📅 Timeline
      </Link>
      <Link to="/status" className={`nav-link ${location.pathname === '/status' ? 'active' : ''}`}>
        🖥️ System Status
      </Link>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/chat" 
            element={
              <ProtectedRoute>
                <Chat />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/documents" 
            element={
              <ProtectedRoute>
                <Documents />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/memories" 
            element={
              <ProtectedRoute>
                <Memories />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/timeline" 
            element={
              <ProtectedRoute>
                <Timeline />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/privacy" 
            element={
              <ProtectedRoute>
                <Privacy />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/settings" 
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/status" 
            element={
              <ProtectedRoute>
                <SystemStatus />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/performance" 
            element={
              <ProtectedRoute>
                <PerformanceDashboard />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </AuthProvider>
    </Router>
  )
}


export default App
