import { useState, useEffect } from 'react'
import './SystemStatus.css'

function SystemStatus() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
     const response = await fetch('/api/system/status')
      const data = await response.json()
      setStatus(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching system status:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="system-status loading">
        <p>Loading system status...</p>
      </div>
    )
  }

  if (!status) {
    return (
      <div className="system-status error">
        <p>Failed to load system status</p>
      </div>
    )
  }

  return (
    <div className="system-status">
      <div className="status-header">
        <h1>🖥️ System Status</h1>
        <div className="offline-badge">
          <span className="offline-icon">🔒</span>
          <span>Offline Mode</span>
        </div>
      </div>

      <div className="status-grid">
        <div className="status-card">
          <div className="card-icon">🤖</div>
          <div className="card-content">
            <h3>AI Engine</h3>
            <p className="card-value">{status.ai_engine}</p>
          </div>
        </div>

        <div className="status-card">
          <div className="card-icon">📦</div>
          <div className="card-content">
            <h3>Model</h3>
            <p className="card-value">{status.model}</p>
          </div>
        </div>

        <div className="status-card">
          <div className="card-icon">💻</div>
          <div className="card-content">
            <h3>Inference</h3>
            <p className="card-value local">{status.inference}</p>
          </div>
        </div>

        <div className="status-card">
          <div className="card-icon">🗄️</div>
          <div className="card-content">
            <h3>Database</h3>
            <p className="card-value">{status.database}</p>
          </div>
        </div>

        <div className="status-card">
          <div className="card-icon">🌐</div>
          <div className="card-content">
            <h3>Internet</h3>
            <p className="card-value offline">{status.internet}</p>
          </div>
        </div>

        <div className="status-card">
          <div className="card-icon">📡</div>
          <div className="card-content">
            <h3>External API Calls</h3>
            <p className="card-value success">{status.external_api_calls}</p>
          </div>
        </div>

        <div className="status-card">
          <div className="card-icon">📄</div>
          <div className="card-content">
            <h3>Documents Processed</h3>
            <p className="card-value">{status.documents_processed}</p>
          </div>
        </div>

        <div className="status-card">
          <div className="card-icon">🧠</div>
          <div className="card-content">
            <h3>Memories Created</h3>
            <p className="card-value">{status.memories_created}</p>
          </div>
        </div>
      </div>

      <div className="architecture-info">
        <h2>🏗️ Architecture Overview</h2>
        <div className="architecture-grid">
          <div className="arch-item">
            <span className="arch-icon">✅</span>
            <span>100% Local Processing</span>
          </div>
          <div className="arch-item">
            <span className="arch-icon">✅</span>
            <span>No Cloud Dependencies</span>
          </div>
          <div className="arch-item">
            <span className="arch-icon">✅</span>
            <span>Privacy First</span>
          </div>
          <div className="arch-item">
            <span className="arch-icon">✅</span>
            <span>Zero Data Egress</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SystemStatus
