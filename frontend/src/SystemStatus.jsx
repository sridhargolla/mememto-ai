import { useState, useEffect } from 'react';
import {
  Cpu, Brain, WifiOff, Database, Activity, Shield,
  Server, Clock, FileText, Zap, HardDrive, RefreshCw,
  CheckCircle, XCircle, AlertTriangle
} from 'lucide-react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

const API_BASE = 'http://localhost:8000';

function StatusIndicator({ ok, label }) {
  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold ${
      ok
        ? 'bg-emerald-500/10 border border-emerald-500/25 text-emerald-400'
        : 'bg-rose-500/10 border border-rose-500/25 text-rose-400'
    }`}>
      {ok ? <CheckCircle size={12} /> : <XCircle size={12} />}
      {label}
    </div>
  );
}

function StatusCard({ icon: Icon, label, value, subtext, color = 'purple', delay = 0 }) {
  const colorMap = {
    purple:  { icon: 'text-purple-400',  bg: 'from-purple-500/15 to-violet-600/5',  border: 'border-purple-500/20' },
    cyan:    { icon: 'text-cyan-400',    bg: 'from-cyan-500/15 to-blue-600/5',       border: 'border-cyan-500/20' },
    emerald: { icon: 'text-emerald-400', bg: 'from-emerald-500/15 to-green-600/5',   border: 'border-emerald-500/20' },
    amber:   { icon: 'text-amber-400',   bg: 'from-amber-500/15 to-orange-600/5',    border: 'border-amber-500/20' },
    rose:    { icon: 'text-rose-400',    bg: 'from-rose-500/15 to-pink-600/5',       border: 'border-rose-500/20' },
    blue:    { icon: 'text-blue-400',    bg: 'from-blue-500/15 to-indigo-600/5',     border: 'border-blue-500/20' },
    slate:   { icon: 'text-slate-400',   bg: 'from-slate-500/10 to-slate-600/5',     border: 'border-slate-500/20' },
  };
  const c = colorMap[color] || colorMap.purple;

  return (
    <div
      className={`glass-card p-5 border ${c.border} bg-gradient-to-br ${c.bg} animate-fade-in`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className={`inline-flex p-2.5 rounded-xl bg-black/20 mb-3`}>
        <Icon size={18} className={c.icon} />
      </div>
      <p className="text-xs text-slate-500 font-medium mb-1">{label}</p>
      <p className={`text-base font-bold ${c.icon} font-mono truncate`} title={value}>
        {value}
      </p>
      {subtext && <p className="text-xs text-slate-600 mt-1">{subtext}</p>}
    </div>
  );
}

function ProgressBar({ label, value, max, unit = '%', color = 'purple' }) {
  const pct = Math.min(100, max > 0 ? (value / max) * 100 : value);
  const colorMap = {
    purple:  'from-purple-500 to-violet-600',
    cyan:    'from-cyan-500 to-blue-600',
    emerald: 'from-emerald-500 to-green-600',
    amber:   'from-amber-500 to-orange-500',
    rose:    'from-rose-500 to-pink-600',
  };

  return (
    <div className="py-3 border-b border-white/5 last:border-0">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-slate-400">{label}</span>
        <span className="text-sm font-semibold text-white">
          {typeof value === 'number' ? value.toFixed(1) : value}{unit}
        </span>
      </div>
      <div className="progress-bar">
        <div
          className={`progress-bar-fill bg-gradient-to-r ${colorMap[color]}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function SystemStatus() {
  const [status, setStatus]           = useState(null);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 8000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_BASE}/system/status`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setStatus(await res.json());
        setError(null);
        setLastRefreshed(new Date().toLocaleTimeString());
      } else {
        setError(`Server returned ${res.status}`);
      }
    } catch {
      setError('Cannot connect to backend at localhost:8000');
    } finally {
      setLoading(false);
    }
  };

  const cards = status ? [
    { icon: Brain,    label: 'AI Runtime',         value: status.ai_engine || 'llama.cpp',  color: 'purple',  delay: 0 },
    { icon: Cpu,      label: 'Inference Device',   value: status.inference || 'Local CPU',  color: 'emerald', delay: 50 },
    { icon: Server,   label: 'Active Model',       value: status.model || 'Not loaded',     color: 'cyan',    delay: 100, subtext: 'GGUF format' },
    { icon: Shield,   label: 'GPU Offloading',     value: status.gpu || 'Disabled',         color: 'slate',   delay: 150 },
    { icon: Database, label: 'Database',           value: status.database || 'SQLite',      color: 'blue',    delay: 200 },
    { icon: WifiOff,  label: 'Internet',           value: status.internet || 'Offline',     color: 'rose',    delay: 250 },
    { icon: Activity, label: 'External API Calls', value: `${status.external_api_calls}`,  color: 'emerald', delay: 300, subtext: 'Always zero — fully offline' },
    { icon: FileText, label: 'Documents Processed',value: `${status.documents_processed}`, color: 'amber',   delay: 350 },
    { icon: Brain,    label: 'Memories Created',   value: `${status.memories_created}`,    color: 'purple',  delay: 400 },
  ] : [];

  const features = [
    '100% Local Processing',
    'No Cloud Dependencies',
    'Privacy First by Design',
    'Zero Data Egress',
    'CPU-Only Inference',
    'SQLite Local Storage',
    'Offline RAG Pipeline',
    'Open Source Stack',
    'No Telemetry',
    'Air-Gap Ready',
    'GDPR Compliant',
    'Self-Hosted',
  ];

  return (
    <div className="min-h-screen flex">
      <div className="app-bg" />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col lg:ml-64 min-h-screen">
        <Navbar
          onMenuClick={() => setSidebarOpen(true)}
          title="System Status"
          subtitle={lastRefreshed ? `Last refreshed: ${lastRefreshed} · Auto-refresh every 8s` : 'Loading...'}
        />

        <main className="flex-1 p-5 md:p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">

            {/* Status Pills */}
            <div className="flex flex-wrap gap-3 animate-fade-in">
              <StatusIndicator ok={false} label="Internet: Offline Mode" />
              <StatusIndicator ok={true}  label="AI Engine: llama.cpp" />
              <StatusIndicator ok={true}  label="CPU Inference" />
              <StatusIndicator ok={status?.ai_engine != null} label={status ? 'Backend Connected' : 'Backend Offline'} />
            </div>

            {/* Error banner */}
            {error && (
              <div className="glass-card p-4 border border-rose-500/30 bg-rose-500/5 flex items-start gap-3 animate-fade-in">
                <AlertTriangle size={18} className="text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-rose-400 font-semibold text-sm">{error}</p>
                  <p className="text-slate-500 text-xs mt-0.5">Make sure the backend server is running on port 8000.</p>
                </div>
                <button onClick={fetchStatus} className="ml-auto flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg glass border border-white/10 transition">
                  <RefreshCw size={12} /> Retry
                </button>
              </div>
            )}

            {/* Loading */}
            {loading && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array(9).fill(0).map((_, i) => (
                  <div key={i} className="glass-card p-5">
                    <div className="skeleton w-8 h-8 rounded-xl mb-3" />
                    <div className="skeleton h-3 w-20 mb-2 rounded" />
                    <div className="skeleton h-5 w-24 rounded" />
                  </div>
                ))}
              </div>
            )}

            {/* Status Cards */}
            {status && !loading && (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {cards.map((card, i) => (
                    <StatusCard key={i} {...card} />
                  ))}
                </div>

                {/* Resource Usage */}
                <div className="glass-card p-6">
                  <h2 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
                    <Activity size={16} className="text-cyan-400" /> Live Resource Usage
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
                    <div>
                      <ProgressBar label="CPU Usage"       value={status.cpu_usage_percent}    max={100}  unit="%" color="purple" />
                      <ProgressBar label="RAM Used"        value={status.memory_usage_mb}      max={status.memory_usage_mb + status.memory_available_mb} unit=" MB" color="cyan" />
                    </div>
                    <div>
                      <ProgressBar label="Disk Used"       value={status.disk_usage_gb}        max={status.disk_usage_gb + status.disk_free_gb} unit=" GB" color="amber" />
                      <ProgressBar label="RAM Available"   value={status.memory_available_mb}  max={status.memory_usage_mb + status.memory_available_mb} unit=" MB" color="emerald" />
                    </div>
                  </div>
                </div>

                {/* Privacy features */}
                <div className="glass-card p-6">
                  <h2 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
                    <Shield size={16} className="text-emerald-400" /> Privacy Architecture
                  </h2>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                    {features.map(f => (
                      <div key={f} className="flex items-center gap-2 text-sm text-slate-300 p-2.5 rounded-lg glass border border-white/5">
                        <CheckCircle size={13} className="text-emerald-400 shrink-0" />
                        <span className="text-xs">{f}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default SystemStatus;
