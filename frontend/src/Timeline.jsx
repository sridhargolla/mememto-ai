import { useState, useEffect } from 'react'
import './Timeline.css'

function Timeline() {
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTimeline()
  }, [])

  const fetchTimeline = async () => {
    try {
      const response = await fetch('/api/timeline')
      const data = await response.json()
      setMemories(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching timeline:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="timeline loading">
        <p>Loading timeline...</p>
      </div>
    )
  }

  if (memories.length === 0) {
    return (
      <div className="timeline empty">
        <div className="empty-state">
          <h1>📅 Memory Timeline</h1>
          <p>No memories yet. Upload documents to build your timeline.</p>
        </div>
      </div>
    )
  }

  // Group memories by year
  const groupedByYear = memories.reduce((acc, memory) => {
    const year = new Date(memory.date || memory.created_at).getFullYear()
    if (!acc[year]) {
      acc[year] = []
    }
    acc[year].push(memory)
    return acc
  }, {})

  const sortedYears = Object.keys(groupedByYear).sort()

  const getTypeIcon = (type) => {
    const icons = {
      person: '👤',
      event: '📅',
      experience: '⭐',
      project: '🚀',
      education: '🎓',
      skill: '💡',
      document: '📄'
    }
    return icons[type] || '📌'
  }

  const getTypeColor = (type) => {
    const colors = {
      person: '#667eea',
      event: '#f093fb',
      experience: '#4facfe',
      project: '#43e97b',
      education: '#fa709a',
      skill: '#fee140',
      document: '#89f7fe'
    }
    return colors[type] || '#667eea'
  }

  return (
    <div className="timeline">
      <div className="timeline-header">
        <h1>📅 Memory Timeline</h1>
        <p>Your journey through time</p>
      </div>

      <div className="timeline-container">
        {sortedYears.map((year) => (
          <div key={year} className="timeline-year">
            <div className="year-marker">
              <span className="year-label">{year}</span>
            </div>
            
            <div className="year-memories">
              {groupedByYear[year].map((memory) => (
                <div key={memory.id} className="timeline-item">
                  <div 
                    className="timeline-dot"
                    style={{ backgroundColor: getTypeColor(memory.type) }}
                  >
                    <span className="dot-icon">{getTypeIcon(memory.type)}</span>
                  </div>
                  
                  <div className="timeline-content">
                    <div className="timeline-header-row">
                      <span className="timeline-type">{memory.type || 'memory'}</span>
                      <span className="timeline-date">
                        {new Date(memory.date || memory.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    
                    <h3 className="timeline-title">{memory.title}</h3>
                    <p className="timeline-description">{memory.content}</p>
                    
                    {memory.entities && (
                      <div className="timeline-entities">
                        {memory.entities.people && memory.entities.people.length > 0 && (
                          <div className="entity-group">
                            <span className="entity-label">👤</span>
                            <span className="entity-values">{memory.entities.people.join(', ')}</span>
                          </div>
                        )}
                        {memory.entities.organizations && memory.entities.organizations.length > 0 && (
                          <div className="entity-group">
                            <span className="entity-label">🏢</span>
                            <span className="entity-values">{memory.entities.organizations.join(', ')}</span>
                          </div>
                        )}
                        {memory.entities.locations && memory.entities.locations.length > 0 && (
                          <div className="entity-group">
                            <span className="entity-label">📍</span>
                            <span className="entity-values">{memory.entities.locations.join(', ')}</span>
                          </div>
                        )}
                        {memory.entities.skills && memory.entities.skills.length > 0 && (
                          <div className="entity-group">
                            <span className="entity-label">💡</span>
                            <span className="entity-values">{memory.entities.skills.join(', ')}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Timeline
