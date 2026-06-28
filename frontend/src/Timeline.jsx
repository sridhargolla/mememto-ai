import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'

const TYPE_ICONS = {
  person: '👤',
  event: '📅',
  experience: '⭐',
  project: '🚀',
  education: '🎓',
  skill: '💡',
  document: '📄',
  organization: '🏢',
}

const TYPE_COLORS = {
  person: 'bg-purple-500/20 border-purple-500/40 text-purple-300',
  event: 'bg-pink-500/20 border-pink-500/40 text-pink-300',
  experience: 'bg-blue-500/20 border-blue-500/40 text-blue-300',
  project: 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300',
  education: 'bg-rose-500/20 border-rose-500/40 text-rose-300',
  skill: 'bg-yellow-500/20 border-yellow-500/40 text-yellow-300',
  document: 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300',
  organization: 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300',
}

const DOT_COLORS = {
  person: 'bg-purple-500',
  event: 'bg-pink-500',
  experience: 'bg-blue-500',
  project: 'bg-emerald-500',
  education: 'bg-rose-500',
  skill: 'bg-yellow-500',
  document: 'bg-cyan-500',
  organization: 'bg-indigo-500',
}

function Timeline() {
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchMemories()
  }, [])

  const fetchMemories = async () => {
    const token = localStorage.getItem('token')
    try {
      const response = await fetch('/api/memories?limit=100', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setMemories(data)
        setError(null)
      } else {
        setError(`Backend returned ${response.status}`)
      }
    } catch (err) {
      setError('Cannot connect to backend. Make sure the server is running.')
    } finally {
      setLoading(false)
    }
  }

  // Get unique types for filter tabs
  const types = ['all', ...new Set(memories.map(m => m.type).filter(Boolean))]

  // Filter and group by year
  const filtered = filter === 'all' ? memories : memories.filter(m => m.type === filter)

  const groupedByYear = filtered.reduce((acc, memory) => {
    // Use time_start year if available, otherwise fall back to created_at
    const dateStr = memory.time_start || memory.created_at
    let year = 'Unknown'
    if (dateStr) {
      const parsed = new Date(dateStr)
      if (!isNaN(parsed.getFullYear())) {
        year = parsed.getFullYear()
      } else if (/^\d{4}$/.test(dateStr)) {
        year = parseInt(dateStr)
      }
    }
    if (!acc[year]) acc[year] = []
    acc[year].push(memory)
    return acc
  }, {})

  const sortedYears = Object.keys(groupedByYear).sort((a, b) => b - a)

  return (
    <div className="min-h-screen flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0 lg:ml-64">
        {/* Header */}
        <header className="glass-card-dark border-b border-slate-700/50 px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-gray-400 hover:text-white"
          >
            ☰
          </button>
          <div>
            <h1 className="text-xl font-bold text-white">📅 Memory Timeline</h1>
            <p className="text-gray-400 text-sm mt-0.5">
              {memories.length} memories across your personal history
            </p>
          </div>
          <button
            onClick={fetchMemories}
            className="ml-auto text-sm px-3 py-1.5 bg-slate-700/50 hover:bg-slate-600/50 text-gray-300 rounded-lg transition-colors btn-premium"
          >
            🔄 Refresh
          </button>
        </header>

        <main className="flex-1 p-6 overflow-y-auto">
          {/* Loading */}
          {loading && (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin text-4xl">⏳</div>
              <p className="ml-4 text-gray-400 text-lg">Loading your timeline…</p>
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div className="glass-card-dark border border-red-500/30 rounded-xl p-6 text-center animate-fade-in">
              <p className="text-red-400 font-semibold text-lg">⚠️ {error}</p>
              <button
                onClick={fetchMemories}
                className="mt-3 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg text-sm transition-colors btn-premium"
              >
                Try again
              </button>
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && memories.length === 0 && (
            <div className="flex flex-col items-center justify-center h-64 text-center animate-fade-in">
              <div className="text-6xl mb-4 animate-float">📅</div>
              <h2 className="text-xl font-semibold text-white mb-2">No memories yet</h2>
              <p className="text-gray-400 max-w-sm">
                Upload documents in the Documents section and Memento AI will extract memories to build your timeline.
              </p>
            </div>
          )}

          {/* Filter tabs */}
          {!loading && !error && memories.length > 0 && (
            <>
              <div className="flex flex-wrap gap-2 mb-8 animate-fade-in">
                {types.map(type => (
                  <button
                    key={type}
                    onClick={() => setFilter(type)}
                    className={`premium-card px-3 py-1.5 rounded-full text-sm font-medium capitalize transition-colors border ${
                      filter === type
                        ? 'bg-purple-600 border-purple-500 text-white'
                        : 'glass-card-dark border-slate-600 text-gray-400 hover:text-white hover:border-slate-500'
                    }`}
                  >
                    {TYPE_ICONS[type] || '📌'} {type}
                  </button>
                ))}
              </div>

              {/* Empty filter result */}
              {filtered.length === 0 && (
                <div className="text-center text-gray-500 py-16">
                  No memories of type "{filter}" found.
                </div>
              )}

              {/* Timeline */}
              <div className="relative animate-fade-in">
                {/* Vertical line */}
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-700/50" />

                <div className="space-y-12">
                  {sortedYears.map(year => (
                    <div key={year}>
                      {/* Year marker */}
                      <div className="relative flex items-center mb-6">
                        <div className="absolute left-0 w-12 h-12 flex items-center justify-center glass-card-dark border-2 border-purple-500 rounded-full z-10">
                          <span className="text-purple-300 text-xs font-bold">{year}</span>
                        </div>
                        <div className="ml-16 h-0.5 flex-1 bg-slate-700/50" />
                      </div>

                      {/* Items for this year */}
                      <div className="space-y-4 ml-16">
                        {groupedByYear[year].map(memory => {
                          const typeColor = TYPE_COLORS[memory.type] || 'bg-slate-700/50 border-slate-600 text-gray-400'
                          const dotColor = DOT_COLORS[memory.type] || 'bg-slate-500'
                          const icon = TYPE_ICONS[memory.type] || '📌'

                          return (
                            <div key={memory.id} className="relative flex items-start gap-4">
                              {/* Dot */}
                              <div className={`absolute -left-10 mt-1 w-4 h-4 rounded-full ${dotColor} border-2 border-slate-900 z-10 flex-shrink-0`} />

                              {/* Card */}
                              <div className="flex-1 glass-card-dark rounded-xl p-5 border border-slate-700/50 hover:border-slate-500 transition-colors group premium-card">
                                <div className="flex items-start justify-between gap-3 mb-2">
                                  <div className="flex items-center gap-2">
                                    <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${typeColor}`}>
                                      {icon} {memory.type || 'memory'}
                                    </span>
                                    {memory.time_start && (
                                      <span className="text-gray-500 text-xs">{memory.time_start}</span>
                                    )}
                                  </div>
                                  <span className="text-gray-600 text-xs flex-shrink-0">
                                    {memory.created_at
                                      ? new Date(memory.created_at).toLocaleDateString()
                                      : ''}
                                  </span>
                                </div>

                                <h3 className="text-white font-semibold mb-1 group-hover:text-purple-300 transition-colors">
                                  {memory.title}
                                </h3>
                                <p className="text-gray-400 text-sm leading-relaxed line-clamp-2">
                                  {memory.content}
                                </p>

                                {/* Tags */}
                                {(memory.entities_skills || memory.entities_organizations) && (
                                  <div className="flex flex-wrap gap-1.5 mt-3">
                                    {memory.entities_organizations && JSON.parse(memory.entities_organizations || '[]').slice(0, 2).map((org, i) => (
                                      <span key={i} className="text-xs px-2 py-0.5 bg-slate-700/50 text-gray-300 rounded-full">
                                        🏢 {org}
                                      </span>
                                    ))}
                                    {memory.entities_skills && JSON.parse(memory.entities_skills || '[]').slice(0, 3).map((skill, i) => (
                                      <span key={i} className="text-xs px-2 py-0.5 bg-slate-700/50 text-yellow-300 rounded-full">
                                        💡 {skill}
                                      </span>
                                    ))}
                                  </div>
                                )}

                                {/* Source */}
                                {memory.source_file && (
                                  <p className="text-xs text-gray-600 mt-2">📄 {memory.source_file}</p>
                                )}
                              </div>
                            </div>
                          )
                        })}
                      </div>
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

export default Timeline
