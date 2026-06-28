import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const PerformanceDashboard = () => {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState([]);
  const [aggregatedMetrics, setAggregatedMetrics] = useState(null);
  const [recentInference, setRecentInference] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedType, setSelectedType] = useState('all');

  const API_BASE = 'http://localhost:8000';

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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading performance metrics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Performance Dashboard</h1>
          <button
            onClick={handleCleanup}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            Cleanup Old Metrics
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Metric Type Filter */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Filter by Metric Type</h2>
          <div className="flex gap-2 flex-wrap">
            {['all', 'model_load', 'inference', 'document_process'].map((type) => (
              <button
                key={type}
                onClick={() => handleTypeChange(type)}
                className={`px-4 py-2 rounded-lg transition ${
                  selectedType === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {type.replace('_', ' ').toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Aggregated Metrics */}
        {aggregatedMetrics && selectedType !== 'all' && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Aggregated Statistics - {selectedType.replace('_', ' ').toUpperCase()}</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Count</div>
                <div className="text-2xl font-bold text-blue-600">{aggregatedMetrics.count}</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Avg Duration</div>
                <div className="text-2xl font-bold text-green-600">{aggregatedMetrics.avg_duration.toFixed(2)}s</div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Min Duration</div>
                <div className="text-2xl font-bold text-yellow-600">{aggregatedMetrics.min_duration.toFixed(2)}s</div>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Max Duration</div>
                <div className="text-2xl font-bold text-orange-600">{aggregatedMetrics.max_duration.toFixed(2)}s</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Avg Memory</div>
                <div className="text-2xl font-bold text-purple-600">{aggregatedMetrics.avg_memory_mb.toFixed(1)} MB</div>
              </div>
              <div className="bg-pink-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Avg CPU</div>
                <div className="text-2xl font-bold text-pink-600">{aggregatedMetrics.avg_cpu_percent.toFixed(1)}%</div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Inference Stats */}
        {recentInference.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Recent Inference Performance</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">Timestamp</th>
                    <th className="text-left py-3 px-4">Duration</th>
                    <th className="text-left py-3 px-4">Tokens</th>
                    <th className="text-left py-3 px-4">Tokens/Sec</th>
                    <th className="text-left py-3 px-4">Memory</th>
                    <th className="text-left py-3 px-4">CPU</th>
                  </tr>
                </thead>
                <tbody>
                  {recentInference.map((stat, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 text-sm">{formatTimestamp(stat.timestamp)}</td>
                      <td className="py-3 px-4 text-sm">{stat.duration_seconds.toFixed(2)}s</td>
                      <td className="py-3 px-4 text-sm">{stat.tokens_generated}</td>
                      <td className="py-3 px-4 text-sm font-semibold text-green-600">{stat.tokens_per_second.toFixed(1)}</td>
                      <td className="py-3 px-4 text-sm">{stat.memory_usage_mb.toFixed(1)} MB</td>
                      <td className="py-3 px-4 text-sm">{stat.cpu_usage_percent.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* All Metrics Table */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">All Metrics ({metrics.length})</h2>
          {metrics.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No metrics recorded yet</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">Type</th>
                    <th className="text-left py-3 px-4">Name</th>
                    <th className="text-left py-3 px-4">Duration</th>
                    <th className="text-left py-3 px-4">Memory</th>
                    <th className="text-left py-3 px-4">CPU</th>
                    <th className="text-left py-3 px-4">Tokens</th>
                    <th className="text-left py-3 px-4">Tokens/Sec</th>
                    <th className="text-left py-3 px-4">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {metrics.map((metric, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          metric.metric_type === 'inference' ? 'bg-blue-100 text-blue-800' :
                          metric.metric_type === 'model_load' ? 'bg-green-100 text-green-800' :
                          'bg-purple-100 text-purple-800'
                        }`}>
                          {metric.metric_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm">{metric.metric_name || '-'}</td>
                      <td className="py-3 px-4 text-sm">{metric.duration_seconds.toFixed(2)}s</td>
                      <td className="py-3 px-4 text-sm">{metric.memory_usage_mb?.toFixed(1) || '-'} MB</td>
                      <td className="py-3 px-4 text-sm">{metric.cpu_usage_percent?.toFixed(1) || '-'}%</td>
                      <td className="py-3 px-4 text-sm">{metric.tokens_generated || '-'}</td>
                      <td className="py-3 px-4 text-sm font-semibold text-green-600">
                        {metric.tokens_per_second?.toFixed(1) || '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{formatTimestamp(metric.timestamp)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard;
