import { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import {
  Activity, Cpu, HardDrive, Zap, Clock, TrendingUp,
  RefreshCw, Trash2, AlertTriangle, BarChart2, Database
} from 'lucide-react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

const API_BASE = 'http://localhost:8000';

function MetricBadge({ type }) {
  const map = {
    inference:        'badge-purple',
    model_load:       'badge-emerald',
    document_process: 'badge-amber',
  };
  return <span className={`badge ${map[type] || 'badge-slate'}`}>{type.replace('_', ' ')}</span>;
}

function SummaryCard({ icon: Icon, label, value, unit, color = 'purple', delay = 0 }) {
  const colorMap = {
    purple:  { icon: 'text-purple-400',  border: 'border-purple-500/20',  bg: 'bg-purple-500/10' },
    cyan:    { icon: 'text-cyan-400',    border: 'border-cyan-500/20',    bg: 'bg-cyan-500/10' },
    emerald: { icon: 'text-emerald-400', border: 'border-emerald-500/20', bg: 'bg-emerald-500/10' },
    amber:   { icon: 'text-amber-400',   border: 'border-amber-500/20',   bg: 'bg-amber-500/10' },
  };
  const c = colorMap[color] || colorMap.purple;

  return (
    <div
      className={`glass-card p-5 border ${c.border} animate-fade-in`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className={`inline-flex p-2.5 rounded-xl ${c.bg} mb-3`}>
        <Icon size={18} className={c.icon} />
      </div>
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${c.icon} font-mono`}>
        {typeof value === 'number' ? value.toFixed(value >= 100 ? 0 : 2) : value}
        <span className="text-sm font-normal text-slate-500 ml-1">{unit}</span>
      </p>
    </div>
  );
}

function MiniSparkline({ data, color = 'purple' }) {
  if (!data || data.length < 2) return <div className="h-8 text-xs text-slate-600 flex items-center">No data</div>;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const w = 100, h = 32;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / range) * (h - 4) - 2;
    return `${x},${y}`;
  }).join(' ');

  const colorMap = { purple: '#8b5cf6', cyan: '#22d3ee', emerald: '#10b981', amber: '#f59e0b' };

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-8" preserveAspectRatio="none">
      <polyline
        points={pts}
        fill="none"
        stroke={colorMap[color] || colorMap.purple}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

const PerformanceDashboard = () => {
  const { token } = useAuth();
  const [metrics, setMetrics]                   = useState([]);
  const [aggregatedMetrics, setAggregatedMetrics] = useState(null);
  const [recentInference, setRecentInference]   = useState([]);
  const [loading, setLoading]                   = useState(true);
  const [error, setError]                       = useState(null);
  const [selectedType, setSelectedType]         = useState('all');
  const [sidebarOpen, setSidebarOpen]           = useState(false);
  const [showConfirmClean, setShowConfirmClean] = useState(false);

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    setLoading(true);
    await Promise.all([
      fetchMetrics('all'),
      fetchAggregatedMetrics('inference'),
      fetchRecentInference(),
    ]);
    setLoading(false);
  };

  const fetchMetrics = async (type = 'all') => {
    try {
      const url = type === 'all'
        ? `${API_BASE}/metrics?limit=50`
        : `${API_BASE}/metrics?metric_type=${type}&limit=50`;
      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) throw new Error('Failed to fetch metrics');
      setMetrics(await res.json());
    } catch (e) {
      setError(e.message);
    }
  };

  const fetchAggregatedMetrics = async (type) => {
    try {
      const res = await fetch(`${API_BASE}/metrics/aggregated/${type}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setAggregatedMetrics(await res.json());
    } catch { /* silent */ }
  };

  const fetchRecentInference = async () => {
    try {
      const res = await fetch(`${API_BASE}/metrics/inference/recent?limit=10`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setRecentInference(await res.json());
    } catch { /* silent */ }
  };

  const handleTypeChange = (type) => {
    setSelectedType(type);
    fetchMetrics(type);
    if (type !== 'all') fetchAggregatedMetrics(type);
  };

  const handleCleanup = async () => {
    try {
      const res = await fetch(`${API_BASE}/metrics/cleanup`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setShowConfirmClean(false);
        await fetchAll();
      }
    } catch (e) {
      console.error('Cleanup failed:', e);
    }
  };

  const formatTime = (ts) => new Date(ts).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  // Derive summary stats from recent inference
  const avgDuration = recentInference.length > 0
    ? recentInference.reduce((s, m) => s + m.duration_seconds, 0) / recentInference.length : 0;
  const avgTokens = recentInference.length > 0
    ? recentInference.reduce((s, m) => s + (m.tokens_per_second || 0), 0) / recentInference.length : 0;
  const avgMemory = recentInference.length > 0
    ? recentInference.reduce((s, m) => s + (m.memory_usage_mb || 0), 0) / recentInference.length : 0;

  const sparklineData = recentInference.map(m => m.tokens_per_second || 0).reverse();

  const TYPES = ['all', 'model_load', 'inference', 'document_process'];

  return (
    <div className="min-h-screen flex">
      <div className="app-bg" />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col lg:ml-64 min-h-screen">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title="Performance" subtitle="Live metrics & inference statistics" />

        <main className="flex-1 p-5 md:p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">

            {error && (
              <div className="glass-card p-4 border border-rose-500/30 bg-rose-500/5 flex items-center gap-3">
                <AlertTriangle size={16} className="text-rose-400" />
                <span className="text-rose-400 text-sm">{error}</span>
              </div>
            )}

            {/* Summary Cards */}
            {loading ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Array(4).fill(0).map((_, i) => (
                  <div key={i} className="glass-card p-5">
                    <div className="skeleton w-8 h-8 rounded-xl mb-3" />
                    <div className="skeleton h-3 w-20 mb-2 rounded" />
                    <div className="skeleton h-7 w-16 rounded" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <SummaryCard icon={Clock}    label="Avg Inference Time" value={avgDuration}  unit="s"   color="purple"  delay={0}   />
                <SummaryCard icon={Zap}      label="Avg Tokens/Sec"     value={avgTokens}    unit="t/s" color="cyan"    delay={60}  />
                <SummaryCard icon={HardDrive}label="Avg RAM Usage"      value={avgMemory}    unit="MB"  color="amber"   delay={120} />
                <SummaryCard icon={BarChart2}label="Total Metrics"      value={metrics.length} unit=""  color="emerald" delay={180} />
              </div>
            )}

            {/* Sparkline panel */}
            {recentInference.length > 0 && (
              <div className="glass-card p-5">
                <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  <TrendingUp size={15} className="text-purple-400" /> Tokens/Second — Recent Inferences
                </h3>
                <MiniSparkline data={sparklineData} color="purple" />
                <div className="flex justify-between text-[10px] text-slate-600 mt-1">
                  <span>Oldest</span>
                  <span>Most recent</span>
                </div>
              </div>
            )}

            {/* Aggregated stats */}
            {aggregatedMetrics && selectedType !== 'all' && (
              <div className="glass-card p-5">
                <h3 className="text-sm font-semibold text-white mb-4">
                  Aggregated — <span className="text-purple-400">{selectedType.replace('_', ' ').toUpperCase()}</span>
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                  {[
                    { label: 'Count',       value: aggregatedMetrics.count,           unit: '',   color: 'text-white' },
                    { label: 'Avg Duration',value: aggregatedMetrics.avg_duration,    unit: 's',  color: 'text-purple-400' },
                    { label: 'Min',         value: aggregatedMetrics.min_duration,    unit: 's',  color: 'text-emerald-400' },
                    { label: 'Max',         value: aggregatedMetrics.max_duration,    unit: 's',  color: 'text-amber-400' },
                    { label: 'Avg Memory',  value: aggregatedMetrics.avg_memory_mb,   unit: 'MB', color: 'text-cyan-400' },
                    { label: 'Avg CPU',     value: aggregatedMetrics.avg_cpu_percent, unit: '%',  color: 'text-rose-400' },
                  ].map(s => (
                    <div key={s.label} className="glass p-3 rounded-xl border border-white/5 text-center">
                      <p className="text-xs text-slate-500 mb-1">{s.label}</p>
                      <p className={`text-lg font-bold font-mono ${s.color}`}>
                        {typeof s.value === 'number' ? s.value.toFixed(s.value >= 100 ? 0 : 2) : s.value}{s.unit}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Filter + cleanup */}
            <div className="glass-card p-5">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-4">
                <h3 className="text-sm font-semibold text-white flex-1">Metrics Log</h3>
                <div className="flex gap-2">
                  {TYPES.map(t => (
                    <button
                      key={t}
                      onClick={() => handleTypeChange(t)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-medium transition ${
                        selectedType === t
                          ? 'bg-purple-600/30 border border-purple-500/50 text-purple-300'
                          : 'bg-white/5 border border-white/10 text-slate-400 hover:text-white'
                      }`}
                    >
                      {t.replace('_', ' ')}
                    </button>
                  ))}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={fetchAll}
                    className="flex items-center gap-1.5 px-3 py-1.5 glass border border-white/10 rounded-xl text-xs text-slate-400 hover:text-white transition"
                  >
                    <RefreshCw size={12} /> Refresh
                  </button>
                  {showConfirmClean ? (
                    <>
                      <button onClick={handleCleanup} className="px-3 py-1.5 rounded-xl text-xs bg-rose-500/20 border border-rose-500/30 text-rose-400 hover:bg-rose-500/30 transition">
                        Confirm Delete
                      </button>
                      <button onClick={() => setShowConfirmClean(false)} className="px-3 py-1.5 rounded-xl text-xs glass border border-white/10 text-slate-400 transition">
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => setShowConfirmClean(true)}
                      className="flex items-center gap-1.5 px-3 py-1.5 glass border border-rose-500/20 rounded-xl text-xs text-rose-400 hover:bg-rose-500/10 transition"
                    >
                      <Trash2 size={12} /> Cleanup
                    </button>
                  )}
                </div>
              </div>

              {/* Recent inference table */}
              {recentInference.length > 0 && (
                <div className="overflow-x-auto rounded-xl border border-white/5">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/5 bg-white/2">
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">Time</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">Duration</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">Tokens</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">T/s</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">RAM</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">CPU</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentInference.map((s, i) => (
                        <tr key={i} className="border-b border-white/5 hover:bg-white/3 transition">
                          <td className="py-3 px-4 text-xs text-slate-400">{formatTime(s.timestamp)}</td>
                          <td className="py-3 px-4 text-xs font-mono text-white">{s.duration_seconds.toFixed(2)}s</td>
                          <td className="py-3 px-4 text-xs font-mono text-slate-300">{s.tokens_generated || '-'}</td>
                          <td className="py-3 px-4 text-xs font-mono font-bold text-purple-400">{(s.tokens_per_second || 0).toFixed(1)}</td>
                          <td className="py-3 px-4 text-xs font-mono text-slate-300">{(s.memory_usage_mb || 0).toFixed(0)} MB</td>
                          <td className="py-3 px-4 text-xs font-mono text-slate-300">{(s.cpu_usage_percent || 0).toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* All metrics table */}
              {metrics.length > 0 && (
                <div className="overflow-x-auto rounded-xl border border-white/5 mt-4">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/5">
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">Type</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">Name</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">Duration</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">RAM</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">T/s</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wide">Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metrics.slice(0, 20).map((m, i) => (
                        <tr key={i} className="border-b border-white/5 hover:bg-white/3 transition">
                          <td className="py-3 px-4"><MetricBadge type={m.metric_type} /></td>
                          <td className="py-3 px-4 text-xs text-slate-400 font-mono truncate max-w-[120px]">{m.metric_name || '-'}</td>
                          <td className="py-3 px-4 text-xs font-mono text-white">{m.duration_seconds.toFixed(2)}s</td>
                          <td className="py-3 px-4 text-xs font-mono text-slate-300">{m.memory_usage_mb?.toFixed(0) || '-'} MB</td>
                          <td className="py-3 px-4 text-xs font-mono font-bold text-purple-400">{m.tokens_per_second?.toFixed(1) || '-'}</td>
                          <td className="py-3 px-4 text-xs text-slate-500">{formatTime(m.timestamp)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {metrics.length > 20 && (
                    <p className="text-xs text-slate-600 text-center py-3">
                      Showing 20 of {metrics.length} metrics
                    </p>
                  )}
                </div>
              )}

              {metrics.length === 0 && !loading && (
                <div className="text-center py-8">
                  <Activity size={28} className="text-slate-600 mx-auto mb-2" />
                  <p className="text-slate-500 text-sm">No metrics recorded yet. Use the chat to generate some!</p>
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
