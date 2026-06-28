import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import StatisticsCard from '../components/StatisticsCard';
import MemoryCard from '../components/MemoryCard';

function Dashboard() {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState({
    documents: 0,
    memories: 0,
    conversations: 0,
  });
  const [recentMemories, setRecentMemories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem('token');
    
    try {
      // Fetch statistics
      const statusResponse = await fetch('http://localhost:8000/system/status', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setStats({
          documents: statusData.documents_count || 0,
          memories: statusData.memories_count || 0,
          conversations: statusData.conversations_count || 0,
        });
      }

      // Fetch recent memories
      const memoriesResponse = await fetch('http://localhost:8000/memories?limit=5', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (memoriesResponse.ok) {
        const memoriesData = await memoriesResponse.json();
        setRecentMemories(memoriesData);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col lg:ml-64">
        <Navbar 
          onMenuClick={() => setSidebarOpen(true)} 
          title={t('dashboard.title')} 
        />
        
        <main className="flex-1 p-6 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-white">{t('common.loading')}</div>
            </div>
          ) : (
            <div className="max-w-7xl mx-auto space-y-8">
              {/* Statistics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <StatisticsCard
                  icon="📄"
                  title={t('dashboard.documents')}
                  value={stats.documents}
                  subtitle={t('dashboard.totalUploaded')}
                  color="blue"
                />
                <StatisticsCard
                  icon="🧠"
                  title={t('dashboard.memories')}
                  value={stats.memories}
                  subtitle={t('dashboard.extracted')}
                  color="purple"
                />
                <StatisticsCard
                  icon="💬"
                  title={t('dashboard.conversations')}
                  value={stats.conversations}
                  subtitle={t('dashboard.interactions')}
                  color="green"
                />
              </div>

              {/* Quick Actions */}
              <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">{t('dashboard.quickActions')}</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <button className="p-4 bg-purple-600/20 border border-purple-500/30 rounded-lg text-purple-400 hover:bg-purple-600/30 transition flex items-center gap-3">
                    <span className="text-2xl">📄</span>
                    <span className="font-medium">{t('dashboard.uploadDocument')}</span>
                  </button>
                  <button className="p-4 bg-blue-600/20 border border-blue-500/30 rounded-lg text-blue-400 hover:bg-blue-600/30 transition flex items-center gap-3">
                    <span className="text-2xl">💬</span>
                    <span className="font-medium">{t('dashboard.startChat')}</span>
                  </button>
                  <button className="p-4 bg-green-600/20 border border-green-500/30 rounded-lg text-green-400 hover:bg-green-600/30 transition flex items-center gap-3">
                    <span className="text-2xl">🧠</span>
                    <span className="font-medium">{t('dashboard.addMemory')}</span>
                  </button>
                  <button className="p-4 bg-orange-600/20 border border-orange-500/30 rounded-lg text-orange-400 hover:bg-orange-600/30 transition flex items-center gap-3">
                    <span className="text-2xl">📅</span>
                    <span className="font-medium">{t('dashboard.viewTimeline')}</span>
                  </button>
                </div>
              </div>

              {/* Recent Memories */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">{t('dashboard.recentMemories')}</h3>
                {recentMemories.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {recentMemories.map((memory) => (
                      <MemoryCard key={memory.id} memory={memory} />
                    ))}
                  </div>
                ) : (
                  <div className="bg-slate-800 rounded-xl p-8 border border-slate-700 text-center">
                    <p className="text-gray-400">{t('dashboard.noMemories')}</p>
                  </div>
                )}
              </div>

              {/* System Status Preview */}
              <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">{t('dashboard.systemStatus')}</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-gray-300">{t('dashboard.aiModelReady')}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-gray-300">{t('dashboard.databaseConnected')}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-gray-300">{t('dashboard.statusOffline')}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-gray-300">{t('dashboard.privacyLocal')}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default Dashboard;
