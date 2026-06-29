import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  FileText, Brain, MessageSquare, Cpu, HardDrive,
  Zap, Upload, ArrowRight, Activity, Wifi, Server,
  Database, Shield, Clock, TrendingUp
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';

const API_BASE = 'http://localhost:8000';

function AnimatedNumber({ value, duration = 1000 }) {
  const [display, setDisplay] = useState(0);
  const start = useRef(0);
  const frame = useRef(null);

  useEffect(() => {
    const target = Number(value) || 0;
    const startTime = performance.now();
    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(start.current + (target - start.current) * eased));
      if (progress < 1) frame.current = requestAnimationFrame(animate);
      else start.current = target;
    };
    frame.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame.current);
  }, [value, duration]);

  return <span>{display}</span>;
}

function SkeletonCard() {
  return (
    <div className="glass-card p-5">
      <div className="skeleton h-4 w-24 mb-3 rounded" />
      <div className="skeleton h-8 w-16 mb-2 rounded" />
      <div className="skeleton h-3 w-32 rounded" />
    </div>
  );
}

function StatCard({ icon: Icon, label, value, subtitle, color, delay = 0 }) {
  const colorMap = {
    purple:  { bg: 'from-purple-500/20 to-violet-600/10', border: 'border-purple-500/20', icon: 'text-purple-400', glow: 'shadow-purple-900/20' },
    cyan:    { bg: 'from-cyan-500/20 to-blue-600/10',     border: 'border-cyan-500/20',   icon: 'text-cyan-400',   glow: 'shadow-cyan-900/20' },
    emerald: { bg: 'from-emerald-500/20 to-green-600/10', border: 'border-emerald-500/20',icon: 'text-emerald-400',glow: 'shadow-emerald-900/20' },
    amber:   { bg: 'from-amber-500/20 to-orange-600/10',  border: 'border-amber-500/20',  icon: 'text-amber-400',  glow: 'shadow-amber-900/20' },
    rose:    { bg: 'from-rose-500/20 to-pink-600/10',     border: 'border-rose-500/20',   icon: 'text-rose-400',   glow: 'shadow-rose-900/20' },
    blue:    { bg: 'from-blue-500/20 to-indigo-600/10',   border: 'border-blue-500/20',   icon: 'text-blue-400',   glow: 'shadow-blue-900/20' },
  };
  const c = colorMap[color] || colorMap.purple;

  return (
    <div
      className={`glass-card p-5 border ${c.border} animate-fade-in`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className={`inline-flex p-2.5 rounded-xl bg-gradient-to-br ${c.bg} mb-3`}>
        <Icon size={20} className={c.icon} />
      </div>
      <div className="stat-value text-3xl font-bold mb-1">
        <AnimatedNumber value={value} />
      </div>
      <p className="text-sm font-medium text-slate-300">{label}</p>
      <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
    </div>
  );
}

function QuickActionCard({ icon: Icon, label, desc, to, color, delay = 0 }) {
  const colorMap = {
    purple:  'from-purple-600/20 to-violet-600/10  border-purple-500/25  hover:border-purple-500/50  text-purple-400',
    cyan:    'from-cyan-600/20   to-blue-600/10    border-cyan-500/25    hover:border-cyan-500/50    text-cyan-400',
    emerald: 'from-emerald-600/20 to-green-600/10  border-emerald-500/25 hover:border-emerald-500/50 text-emerald-400',
    amber:   'from-amber-600/20  to-orange-600/10  border-amber-500/25   hover:border-amber-500/50   text-amber-400',
  };
  const c = colorMap[color] || colorMap.purple;

  return (
    <Link
      to={to}
      className={`glass-card p-4 border bg-gradient-to-br ${c} group animate-fade-in flex flex-col gap-2`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-center gap-3">
        <Icon size={20} />
        <span className="font-semibold text-white text-sm">{label}</span>
        <ArrowRight size={14} className="ml-auto opacity-0 group-hover:opacity-100 transition" />
      </div>
      <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
    </Link>
  );
}

function RecentMemoryCard({ memory }) {
  const typeColors = {
    person:     'badge-cyan',
    event:      'badge-purple',
    experience: 'badge-emerald',
    project:    'badge-amber',
    education:  'badge-blue',
    skill:      'badge-rose',
    document:   'badge-slate',
  };

  return (
    <div className="glass-card p-4 animate-fade-in">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h4 className="text-sm font-semibold text-white line-clamp-1">{memory.title}</h4>
        {memory.memory_type && (
          <span className={`badge ${typeColors[memory.memory_type] || 'badge-slate'} shrink-0`}>
            {memory.memory_type}
          </span>
        )}
      </div>
      <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{memory.content}</p>
      {memory.tags && (
        <div className="flex flex-wrap gap-1 mt-2">
          {memory.tags.split(',').slice(0, 3).map(tag => (
            <span key={tag} className="badge badge-purple">{tag.trim()}</span>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusRow({ icon: Icon, label, value, valueClass = 'text-white' }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-white/5 last:border-0">
      <div className="flex items-center gap-2.5 text-slate-400">
        <Icon size={14} />
        <span className="text-sm">{label}</span>
      </div>
      <span className={`text-sm font-semibold ${valueClass}`}>{value}</span>
    </div>
  );
}

function Dashboard() {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [recentMemories, setRecentMemories] = useState([]);
  const [recentConvs, setRecentConvs] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const getGreeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 18) return 'Good afternoon';
    return 'Good evening';
  };

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };
    try {
      const [statusRes, memoriesRes, convsRes] = await Promise.all([
        fetch(`${API_BASE}/system/status`, { headers }),
        fetch(`${API_BASE}/memories?limit=6`, { headers }),
        fetch(`${API_BASE}/conversations?limit=5`, { headers }),
      ]);
      if (statusRes.ok)   setSystemStatus(await statusRes.json());
      if (memoriesRes.ok) setRecentMemories(await memoriesRes.json());
      if (convsRes.ok)    setRecentConvs(await convsRes.json());
    } catch (e) {
      console.error('Dashboard fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    { icon: FileText,    label: 'Documents',    value: systemStatus?.documents_processed || 0, subtitle: 'Total uploaded',    color: 'blue',    delay: 0 },
    { icon: Brain,       label: 'Memories',     value: systemStatus?.memories_created || 0,    subtitle: 'Extracted & saved', color: 'purple',  delay: 80 },
    { icon: MessageSquare, label: 'Conversations', value: recentConvs.length || 0,             subtitle: 'AI interactions',   color: 'cyan',    delay: 160 },
    { icon: Cpu,         label: 'CPU Usage',    value: Math.round(systemStatus?.cpu_usage_percent || 0), subtitle: 'Current utilization %', color: 'emerald', delay: 240 },
    { icon: HardDrive,   label: 'Storage Used', value: Math.round(systemStatus?.disk_usage_gb || 0),     subtitle: 'GB on disk',        color: 'amber',   delay: 320 },
    { icon: Shield,      label: 'Privacy',      value: '100',                                  subtitle: '% local processing',color: 'rose',    delay: 400 },
  ];

  return (
    <div className="min-h-screen flex">
      <div className="app-bg" />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col lg:ml-64 min-h-screen">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title="Dashboard" subtitle={`${getGreeting()}, ${user.name || 'there'}`} />

        <main className="flex-1 p-5 md:p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-8">

            {/* Welcome Banner */}
            <div className="glass-card p-6 border border-purple-500/20 bg-gradient-to-r from-purple-600/10 via-violet-600/5 to-transparent animate-fade-in">
              <div className="flex flex-col md:flex-row md:items-center gap-4">
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-white mb-1">
                    {getGreeting()}, <span className="text-glow-purple text-purple-400">{user.name || 'there'}</span> 👋
                  </h2>
                  <p className="text-slate-400 text-sm">
                    Your personal AI memory system is running offline. All data stays on your device.
                  </p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/25">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-emerald-400 text-sm font-semibold">System Online</span>
                </div>
              </div>
            </div>

            {/* Stats Grid */}
            {loading ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {Array(6).fill(0).map((_, i) => <SkeletonCard key={i} />)}
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {stats.map(s => <StatCard key={s.label} {...s} />)}
              </div>
            )}

            {/* Quick Actions */}
            <div>
              <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
                <Zap size={16} className="text-amber-400" /> Quick Actions
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <QuickActionCard icon={Upload}       label="Upload Document" desc="Add PDFs, images, or text files" to="/dashboard/documents" color="purple" delay={0}   />
                <QuickActionCard icon={MessageSquare} label="Start Chat"     desc="Ask questions about your memories" to="/dashboard/chat"      color="cyan"   delay={60}  />
                <QuickActionCard icon={Brain}        label="Browse Memories" desc="Explore your extracted knowledge" to="/dashboard/memories"   color="emerald" delay={120} />
                <QuickActionCard icon={Clock}        label="View Timeline"   desc="See your memories chronologically" to="/dashboard/timeline"  color="amber"  delay={180} />
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Memories */}
              <div className="lg:col-span-2">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-semibold text-white flex items-center gap-2">
                    <Brain size={16} className="text-purple-400" /> Recent Memories
                  </h3>
                  <Link to="/dashboard/memories" className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1">
                    View all <ArrowRight size={12} />
                  </Link>
                </div>
                {loading ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Array(4).fill(0).map((_, i) => (
                      <div key={i} className="glass-card p-4">
                        <div className="skeleton h-4 w-3/4 mb-2 rounded" />
                        <div className="skeleton h-3 w-full mb-1 rounded" />
                        <div className="skeleton h-3 w-2/3 rounded" />
                      </div>
                    ))}
                  </div>
                ) : recentMemories.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {recentMemories.slice(0, 6).map(m => <RecentMemoryCard key={m.id} memory={m} />)}
                  </div>
                ) : (
                  <div className="glass-card p-8 text-center border-dashed">
                    <Brain size={32} className="text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-400 text-sm">No memories yet. Upload a document to get started.</p>
                    <Link to="/dashboard/documents" className="inline-block mt-3 px-4 py-2 rounded-lg bg-purple-600/20 border border-purple-500/30 text-purple-400 text-sm hover:bg-purple-600/30 transition">
                      Upload Document
                    </Link>
                  </div>
                )}
              </div>

              {/* System Panel */}
              <div className="space-y-4">
                {/* Offline Status */}
                <div className="glass-card p-5">
                  <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                    <Server size={14} className="text-emerald-400" /> System Status
                  </h3>
                  <div className="space-y-0">
                    <StatusRow icon={Wifi}     label="Internet"     value="Offline"           valueClass="text-red-400" />
                    <StatusRow icon={Cpu}      label="AI Runtime"   value={systemStatus?.ai_engine || 'llama.cpp'} valueClass="text-purple-400" />
                    <StatusRow icon={Shield}   label="Device"       value={systemStatus?.inference || 'Local CPU'} valueClass="text-emerald-400" />
                    <StatusRow icon={Database} label="Database"     value={systemStatus?.database || 'SQLite'} valueClass="text-blue-400" />
                    <StatusRow icon={Activity} label="API Calls"    value={`${systemStatus?.external_api_calls || 0} external`} />
                  </div>
                </div>

                {/* Model Info */}
                <div className="glass-card p-5">
                  <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                    <Brain size={14} className="text-purple-400" /> Active Model
                  </h3>
                  <p className="text-xs font-mono text-purple-400 break-all leading-relaxed">
                    {systemStatus?.model || 'Model not loaded'}
                  </p>
                  <div className="mt-3 space-y-0">
                    <StatusRow icon={TrendingUp} label="GPU" value={systemStatus?.gpu || 'Disabled'} valueClass="text-slate-400" />
                    <StatusRow icon={HardDrive}  label="RAM Used" value={`${Math.round(systemStatus?.memory_usage_mb || 0)} MB`} />
                  </div>
                </div>

                {/* Recent Conversations */}
                {recentConvs.length > 0 && (
                  <div className="glass-card p-5">
                    <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <MessageSquare size={14} className="text-cyan-400" /> Recent Chats
                    </h3>
                    <div className="space-y-2">
                      {recentConvs.slice(0, 3).map((c, i) => (
                        <div key={i} className="text-xs text-slate-400 line-clamp-1 py-1 border-b border-white/5 last:border-0">
                          💬 {c.question}
                        </div>
                      ))}
                    </div>
                    <Link to="/dashboard/chat" className="mt-3 flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300">
                      Continue chatting <ArrowRight size={11} />
                    </Link>
                  </div>
                )}
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}

export default Dashboard;
