import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

const PerformanceDashboard = () => {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState([]);
  const [aggregatedMetrics, setAggregatedMetrics] = useState(null);
  const [recentInference, setRecentInference] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedType, setSelectedType] = useState('all');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const API_BASE = '/api';

  useEffect(() => {
    fetchMetrics();
    fetchAggregatedMetrics('inference');
    fetchRecentInference();
  }, []);

  const fetchMetrics = async (type = 'all') => {
    try {
      const url = type === 'all' 
        ? `${API_BASE}/metrics?limit=50`
        : `${API_BASE}/metrics?metric_type=${type}&limit=50`;
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('Failed to fetch metrics');
      
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchAggregatedMetrics = async (type) => {
    try {
      const response = await fetch(`${API_BASE}/metrics/aggregated/${type}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('Failed to fetch aggregated metrics');
      
      const data = await response.json();
      setAggregatedMetrics(data);
    } catch (err) {
      console.error('Failed to fetch aggregated metrics:', err);
    }
  };

  const fetchRecentInference = async () => {
    try {
      const response = await fetch(`${API_BASE}/metrics/inference/recent?limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('Failed to fetch recent inference');
      
      const data = await response.json();
      setRecentInference(data);
    } catch (err) {
      console.error('Failed to fetch recent inference:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTypeChange = (type) => {
    setSelectedType(type);
    fetchMetrics(type);
    if (type !== 'all') {
      fetchAggregatedMetrics(type);
    }
  };

  const handleCleanup = async () => {
    if (!confirm('Delete metrics older than 30 days?')) return;
    
    try {
      const response = await fetch(`${API_BASE}/metrics/cleanup`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('Failed to cleanup metrics');
      
      const data = await response.json();
      alert(data.message);
      fetchMetrics(selectedType);
    } catch (err) {
      alert('Failed to cleanup metrics: ' + err.message);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div className="flex-1 flex flex-col lg:ml-64">
          <Navbar onMenuClick={() => setSidebarOpen(true)} title="Performance Dashboard" />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-gray-400">Loading performance metrics...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col lg:ml-64">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title="Performance Dashboard" />
        
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-3xl font-bold text-white">Performance Dashboard</h1>
              <button
                onClick={handleCleanup}
                className="premium-card px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition btn-premium"
              >
                Cleanup Old Metrics
              </button>
            </div>

            {error && (
              <div className="glass-card-dark bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-6 animate-fade-in">
                {error}
              </div>
            )}

            {/* Metric Type Filter */}
            <div className="glass-card-dark p-6 mb-6 animate-fade-in">
              <h2 className="text-lg font-semibold mb-4 text-white">Filter by Metric Type</h2>
              <div className="flex gap-2 flex-wrap">
                {['all', 'model_load', 'inference', 'document_process'].map((type) => (
                  <button
                    key={type}
                    onClick={() => handleTypeChange(type)}
                    className={`premium-card px-4 py-2 rounded-lg transition ${
                      selectedType === type
                        ? 'bg-purple-600 text-white'
                        : 'bg-slate-700/50 text-gray-300 hover:bg-slate-600/50'
                    }`}
                  >
                    {type.replace('_', ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* Aggregated Metrics */}
            {aggregatedMetrics && selectedType !== 'all' && (
              <div className="glass-card-dark p-6 mb-6 animate-fade-in">
                <h2 className="text-lg font-semibold mb-4 text-white">Aggregated Statistics - {selectedType.replace('_', ' ').toUpperCase()}</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  <div className="bg-blue-500/10 p-4 rounded-lg border border-blue-500/20">
                    <div className="text-sm text-gray-400">Count</div>
                    <div className="text-2xl font-bold text-blue-400">{aggregatedMetrics.count}</div>
                  </div>
                  <div className="bg-green-500/10 p-4 rounded-lg border border-green-500/20">
                    <div className="text-sm text-gray-400">Avg Duration</div>
                    <div className="text-2xl font-bold text-green-400">{aggregatedMetrics.avg_duration.toFixed(2)}s</div>
                  </div>
                  <div className="bg-yellow-500/10 p-4 rounded-lg border border-yellow-500/20">
                    <div className="text-sm text-gray-400">Min Duration</div>
                    <div className="text-2xl font-bold text-yellow-400">{aggregatedMetrics.min_duration.toFixed(2)}s</div>
                  </div>
                  <div className="bg-orange-500/10 p-4 rounded-lg border border-orange-500/20">
                    <div className="text-sm text-gray-400">Max Duration</div>
                    <div className="text-2xl font-bold text-orange-400">{aggregatedMetrics.max_duration.toFixed(2)}s</div>
                  </div>
                  <div className="bg-purple-500/10 p-4 rounded-lg border border-purple-500/20">
                    <div className="text-sm text-gray-400">Avg Memory</div>
                    <div className="text-2xl font-bold text-purple-400">{aggregatedMetrics.avg_memory_mb.toFixed(1)} MB</div>
                  </div>
                  <div className="bg-pink-500/10 p-4 rounded-lg border border-pink-500/20">
                    <div className="text-sm text-gray-400">Avg CPU</div>
                    <div className="text-2xl font-bold text-pink-400">{aggregatedMetrics.avg_cpu_percent.toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            )}

            {/* Recent Inference Stats */}
            {recentInference.length > 0 && (
              <div className="glass-card-dark p-6 mb-6 animate-fade-in">
                <h2 className="text-lg font-semibold mb-4 text-white">Recent Inference Performance</h2>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700/50">
                        <th className="text-left py-3 px-4 text-gray-400">Timestamp</th>
                        <th className="text-left py-3 px-4 text-gray-400">Duration</th>
                        <th className="text-left py-3 px-4 text-gray-400">Tokens</th>
                        <th className="text-left py-3 px-4 text-gray-400">Tokens/Sec</th>
                        <th className="text-left py-3 px-4 text-gray-400">Memory</th>
                        <th className="text-left py-3 px-4 text-gray-400">CPU</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentInference.map((stat, index) => (
                        <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                          <td className="py-3 px-4 text-sm text-gray-300">{formatTimestamp(stat.timestamp)}</td>
                          <td className="py-3 px-4 text-sm text-gray-300">{stat.duration_seconds.toFixed(2)}s</td>
                          <td className="py-3 px-4 text-sm text-gray-300">{stat.tokens_generated}</td>
                          <td className="py-3 px-4 text-sm font-semibold text-green-400">{stat.tokens_per_second.toFixed(1)}</td>
                          <td className="py-3 px-4 text-sm text-gray-300">{stat.memory_usage_mb.toFixed(1)} MB</td>
                          <td className="py-3 px-4 text-sm text-gray-300">{stat.cpu_usage_percent.toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* All Metrics Table */}
            <div className="glass-card-dark p-6 animate-fade-in">
              <h2 className="text-lg font-semibold mb-4 text-white">All Metrics ({metrics.length})</h2>
              {metrics.length === 0 ? (
                <div className="text-gray-500 text-center py-8">No metrics recorded yet</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700/50">
                        <th className="text-left py-3 px-4 text-gray-400">Type</th>
                        <th className="text-left py-3 px-4 text-gray-400">Name</th>
                        <th className="text-left py-3 px-4 text-gray-400">Duration</th>
                        <th className="text-left py-3 px-4 text-gray-400">Memory</th>
                        <th className="text-left py-3 px-4 text-gray-400">CPU</th>
                        <th className="text-left py-3 px-4 text-gray-400">Tokens</th>
                        <th className="text-left py-3 px-4 text-gray-400">Tokens/Sec</th>
                        <th className="text-left py-3 px-4 text-gray-400">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metrics.map((metric, index) => (
                        <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${
                              metric.metric_type === 'inference' ? 'bg-blue-500/20 text-blue-400' :
                              metric.metric_type === 'model_load' ? 'bg-green-500/20 text-green-400' :
                              'bg-purple-500/20 text-purple-400'
                            }`}>
                              {metric.metric_type}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-300">{metric.metric_name || '-'}</td>
                          <td className="py-3 px-4 text-sm text-gray-300">{metric.duration_seconds.toFixed(2)}s</td>
                          <td className="py-3 px-4 text-sm text-gray-300">{metric.memory_usage_mb?.toFixed(1) || '-'} MB</td>
                          <td className="py-3 px-4 text-sm text-gray-300">{metric.cpu_usage_percent?.toFixed(1) || '-'}%</td>
                          <td className="py-3 px-4 text-sm text-gray-300">{metric.tokens_generated || '-'}</td>
                          <td className="py-3 px-4 text-sm font-semibold text-green-400">
                            {metric.tokens_per_second?.toFixed(1) || '-'}
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-400">{formatTimestamp(metric.timestamp)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default PerformanceDashboard;
