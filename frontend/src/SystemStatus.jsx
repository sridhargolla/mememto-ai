import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'

function SystemStatus() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [lastRefreshed, setLastRefreshed] = useState(null)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    const token = localStorage.getItem('token')
    try {
      const response = await fetch('http://localhost:8000/system/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
        setError(null)
        setLastRefreshed(new Date().toLocaleTimeString())
      } else {
        setError(`Server returned ${response.status}`)
      }
    } catch (err) {
      setError('Cannot connect to backend at localhost:8000')
    } finally {
      setLoading(false)
    }
  }

  const statusCards = status ? [
    { icon: '🤖', label: 'AI Engine', value: status.ai_engine, style: 'text-purple-400' },
    { icon: '📦', label: 'Active Model', value: status.model || 'Not loaded', style: 'text-blue-400', mono: true },
    { icon: '💻', label: 'Inference Device', value: status.inference, style: 'text-emerald-400' },
    { icon: '🖥️', label: 'GPU Offloading', value: status.gpu || 'Disabled', style: 'text-gray-400' },
    { icon: '🗄️', label: 'Database', value: status.database, style: 'text-yellow-400' },
    { icon: '🌐', label: 'Internet', value: status.internet, style: 'text-red-400' },
    { icon: '📡', label: 'External API Calls', value: status.external_api_calls, style: 'text-green-400' },
    { icon: '📄', label: 'Documents Processed', value: status.documents_processed, style: 'text-white' },
    { icon: '🧠', label: 'Memories Created', value: status.memories_created, style: 'text-white' },
  ] : []

  return (
    <div className="min-h-screen bg-slate-900 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-gray-400 hover:text-white"
          >
            ☰
          </button>
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              🖥️ System Status
            </h1>
            {lastRefreshed && (
              <p className="text-xs text-gray-400 mt-0.5">Last refreshed: {lastRefreshed} · Auto-refreshing every 5s</p>
            )}
          </div>

          {/* Offline Badge */}
          <div className="ml-auto flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-full">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            <span className="text-red-400 text-sm font-semibold">Offline Mode</span>
          </div>
        </header>

        <main className="flex-1 p-6 overflow-y-auto">
          {loading && (
            <div className="flex items-center justify-center h-40">
              <div className="animate-spin text-3xl">⚙️</div>
              <p className="ml-3 text-gray-400">Loading system status...</p>
            </div>
          )}

          {error && !loading && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
              <p className="text-red-400 font-medium">⚠️ {error}</p>
              <p className="text-gray-500 text-sm mt-1">Make sure the backend server is running on port 8000.</p>
            </div>
          )}

          {status && !loading && (
            <>
              {/* Status Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {statusCards.map((card, i) => (
                  <div key={i} className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-slate-500 transition-colors">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-2xl">{card.icon}</span>
                      <h3 className="text-gray-400 text-sm font-medium">{card.label}</h3>
                    </div>
                    <p className={`text-lg font-semibold ${card.style} ${card.mono ? 'font-mono text-sm truncate' : ''}`}>
                      {card.value}
                    </p>
                  </div>
                ))}
              </div>

              {/* Architecture Overview */}
              <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                <h2 className="text-lg font-semibold text-white mb-5">🏗️ Architecture Overview</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    '100% Local Processing',
                    'No Cloud Dependencies',
                    'Privacy First',
                    'Zero Data Egress',
                    'CPU-Only Inference',
                    'SQLite Local Storage',
                    'Offline RAG Pipeline',
                    'Open Source Stack',
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-gray-300">
                      <span className="text-emerald-400 font-bold">✅</span>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default SystemStatus
