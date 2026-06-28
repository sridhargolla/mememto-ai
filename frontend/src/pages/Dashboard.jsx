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
  const [systemStatus, setSystemStatus] = useState(null);
  const [recentMemories, setRecentMemories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem('token');
    
    try {
      // Fetch statistics
      const statusResponse = await fetch('/api/system/status', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setSystemStatus(statusData);
        setStats({
          documents: statusData.documents_processed || 0,
          memories: statusData.memories_created || 0,
          conversations: statusData.conversations_count || 0,
        });
      }

      // Fetch recent memories
      const memoriesResponse = await fetch('/api/memories?limit=5', {
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
    <div className="min-h-screen flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col lg:ml-64">
        <Navbar 
          onMenuClick={() => setSidebarOpen(true)} 
          title={t('dashboard.title')} 
        />
        
        <main className="flex-1 p-6 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-white animate-pulse">{t('common.loading')}</div>
            </div>
          ) : (
            <div className="max-w-7xl mx-auto space-y-8">
              {/* Welcome Message */}
              <div className="glass-card-dark p-6 animate-fade-in">
                <h1 className="text-3xl font-bold text-white mb-2">Welcome back!</h1>
                <p className="text-gray-400">Your personal AI memory assistant is ready to help.</p>
              </div>

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
              <div className="glass-card-dark p-6 animate-fade-in">
                <h3 className="text-lg font-semibold text-white mb-4">{t('dashboard.quickActions')}</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <button className="premium-card p-4 bg-purple-600/20 border border-purple-500/30 rounded-lg text-purple-400 hover:bg-purple-600/30 transition flex items-center gap-3 btn-premium">
                    <span className="text-2xl">📄</span>
                    <span className="font-medium">{t('dashboard.uploadDocument')}</span>
                  </button>
                  <button className="premium-card p-4 bg-blue-600/20 border border-blue-500/30 rounded-lg text-blue-400 hover:bg-blue-600/30 transition flex items-center gap-3 btn-premium">
                    <span className="text-2xl">💬</span>
                    <span className="font-medium">{t('dashboard.startChat')}</span>
                  </button>
                  <button className="premium-card p-4 bg-green-600/20 border border-green-500/30 rounded-lg text-green-400 hover:bg-green-600/30 transition flex items-center gap-3 btn-premium">
                    <span className="text-2xl">🧠</span>
                    <span className="font-medium">{t('dashboard.addMemory')}</span>
                  </button>
                  <button className="premium-card p-4 bg-orange-600/20 border border-orange-500/30 rounded-lg text-orange-400 hover:bg-orange-600/30 transition flex items-center gap-3 btn-premium">
                    <span className="text-2xl">📅</span>
                    <span className="font-medium">{t('dashboard.viewTimeline')}</span>
                  </button>
                </div>
              </div>

              {/* Recent Memories */}
              <div className="animate-fade-in">
                <h3 className="text-lg font-semibold text-white mb-4">{t('dashboard.recentMemories')}</h3>
                {recentMemories.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {recentMemories.map((memory) => (
                      <MemoryCard key={memory.id} memory={memory} />
                    ))}
                  </div>
                ) : (
                  <div className="glass-card-dark p-8 text-center">
                    <p className="text-gray-400">{t('dashboard.noMemories')}</p>
                  </div>
                )}
              </div>

              {/* System Telemetry & Offline Status Panels */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in">
                {/* Offline Status Panel */}
                <div className="glass-card-dark p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    🔒 Memento AI Offline Status
                  </h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                      <span className="text-gray-400">Internet Connection</span>
                      <span className="px-3 py-1 bg-red-500/10 border border-red-500/20 text-red-400 rounded-full text-xs font-semibold">
                        OFFLINE
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                      <span className="text-gray-400">AI Runtime</span>
                      <span className="text-white font-medium">{systemStatus?.ai_engine || 'llama.cpp'}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                      <span className="text-gray-400">Device</span>
                      <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full text-xs font-semibold">
                        {systemStatus?.inference || 'Local (CPU)'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                      <span className="text-gray-400">External Cloud API Calls</span>
                      <span className="text-white font-semibold">0</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-400">Database</span>
                      <span className="text-white font-medium">{systemStatus?.database || 'SQLite'}</span>
                    </div>
                  </div>
                </div>

                {/* Performance Monitoring Panel */}
                <div className="glass-card-dark p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    📊 CPU Performance Metrics
                  </h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                      <span className="text-gray-400">Active Model</span>
                      <span className="text-purple-400 font-medium truncate max-w-[200px]" title={systemStatus?.model}>
                        {systemStatus?.model || 'Qwen2.5 GGUF'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                      <span className="text-gray-400">GPU Offloading</span>
                      <span className="text-gray-400 font-medium">{systemStatus?.gpu || 'Disabled'}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                      <span className="text-gray-400">Documents Processed</span>
                      <span className="text-white font-semibold">{systemStatus?.documents_processed || 0}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-400">Memories Created</span>
                      <span className="text-white font-semibold">{systemStatus?.memories_created || 0}</span>
                    </div>
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
