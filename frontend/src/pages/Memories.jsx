import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import MemoryCard from '../components/MemoryCard';

function Memories() {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchMemories();
  }, [filter]);

  const fetchMemories = async () => {
    const token = localStorage.getItem('token');
    
    try {
      let url = '/api/memories';
      if (filter !== 'all') {
        url += `/type/${filter}`;
      }
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (response.ok) {
        const data = await response.json();
        setMemories(data);
      }
    } catch (error) {
      console.error('Failed to fetch memories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (memoryId) => {
    const token = localStorage.getItem('token');
    
    if (!confirm(t('memories.deleteConfirm'))) return;

    try {
      const response = await fetch(`/api/memories/${memoryId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        await fetchMemories();
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`Delete failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Connection error. Please check your network.');
    }
  };

  const filteredMemories = memories.filter(memory => {
    if (!search) return true;
    const searchLower = search.toLowerCase();
    return (
      memory.title?.toLowerCase().includes(searchLower) ||
      memory.content?.toLowerCase().includes(searchLower) ||
      memory.tags?.toLowerCase().includes(searchLower)
    );
  });

  return (
    <div className="min-h-screen flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col lg:ml-64">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title={t('memories.title')} />
        
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Filters and Search */}
            <div className="glass-card-dark p-6 animate-fade-in">
              <div className="flex flex-col md:flex-row gap-4">
                {/* Search */}
                <div className="flex-1">
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder={t('memories.searchPlaceholder')}
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 backdrop-blur-sm"
                  />
                </div>
                
                {/* Filter */}
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="px-4 py-3 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 backdrop-blur-sm"
                >
                  <option value="all">{t('memories.filterAll')}</option>
                  <option value="person">{t('memories.filterPeople')}</option>
                  <option value="event">{t('memories.filterEvents')}</option>
                  <option value="experience">{t('memories.filterExperiences')}</option>
                  <option value="project">{t('memories.filterProjects')}</option>
                  <option value="education">{t('memories.filterEducation')}</option>
                  <option value="skill">{t('memories.filterSkills')}</option>
                  <option value="document">{t('memories.filterDocuments')}</option>
                </select>
              </div>
            </div>

            {/* Memories Grid */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-white animate-pulse">{t('common.loading')}</div>
              </div>
            ) : filteredMemories.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredMemories.map((memory) => (
                  <MemoryCard key={memory.id} memory={memory} onDelete={handleDelete} />
                ))}
              </div>
            ) : (
              <div className="glass-card-dark p-12 text-center animate-fade-in">
                <div className="text-6xl mb-4 animate-float">🧠</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {search ? t('memories.noMemoriesFound') : t('memories.noMemories')}
                </h3>
                <p className="text-gray-400 mb-6">
                  {search 
                    ? t('memories.tryDifferent') 
                    : t('memories.noMemoriesDesc')}
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default Memories;
