import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Brain, Search, Filter, Trash2, ChevronDown, ChevronUp,
  Calendar, Tag, FileText, Users, MapPin, Building2,
  Code, Star, SortAsc, RefreshCw, X
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';

const API_BASE = 'http://localhost:8000';

const TYPE_CONFIG = {
  person:     { label: 'Person',     badge: 'badge-cyan',    icon: Users },
  event:      { label: 'Event',      badge: 'badge-purple',  icon: Calendar },
  experience: { label: 'Experience', badge: 'badge-emerald', icon: Star },
  project:    { label: 'Project',    badge: 'badge-amber',   icon: Code },
  education:  { label: 'Education',  badge: 'badge-blue',    icon: FileText },
  skill:      { label: 'Skill',      badge: 'badge-rose',    icon: Code },
  document:   { label: 'Document',   badge: 'badge-slate',   icon: FileText },
};

const IMPORTANCE_CONFIG = {
  high:   { badge: 'badge-rose',   dot: 'bg-rose-400',   label: 'High' },
  medium: { badge: 'badge-amber',  dot: 'bg-amber-400',  label: 'Medium' },
  low:    { badge: 'badge-emerald',dot: 'bg-emerald-400',label: 'Low' },
};

function MemoryCard({ memory, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const typeCfg = TYPE_CONFIG[memory.memory_type] || { label: memory.memory_type || 'Memory', badge: 'badge-slate', icon: Brain };
  const impCfg  = IMPORTANCE_CONFIG[memory.importance] || null;
  const TypeIcon = typeCfg.icon;

  const tags    = memory.tags ? memory.tags.split(',').map(t => t.trim()).filter(Boolean) : [];
  const people  = memory.entities_people ? memory.entities_people.split(',').filter(Boolean) : [];
  const orgs    = memory.entities_organizations ? memory.entities_organizations.split(',').filter(Boolean) : [];
  const locs    = memory.entities_locations ? memory.entities_locations.split(',').filter(Boolean) : [];
  const skills  = memory.entities_skills ? memory.entities_skills.split(',').filter(Boolean) : [];

  const date = memory.created_at
    ? new Date(memory.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
    : '';

  const isLong = memory.content?.length > 200;

  const handleDelete = async () => {
    setDeleting(true);
    await onDelete(memory.id);
    setDeleting(false);
    setShowConfirm(false);
  };

  return (
    <div className="glass-card p-4 group animate-fade-in border border-transparent hover:border-purple-500/20">
      {/* Header */}
      <div className="flex items-start gap-2 mb-2">
        <div className="w-8 h-8 rounded-lg bg-purple-500/15 flex items-center justify-center shrink-0 mt-0.5">
          <TypeIcon size={14} className="text-purple-400" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-white line-clamp-2 leading-snug">{memory.title}</h4>
          <div className="flex flex-wrap items-center gap-1.5 mt-1.5">
            <span className={`badge ${typeCfg.badge}`}>{typeCfg.label}</span>
            {impCfg && (
              <span className={`badge ${impCfg.badge} flex items-center gap-1`}>
                <span className={`w-1 h-1 rounded-full ${impCfg.dot}`} />
                {impCfg.label}
              </span>
            )}
          </div>
        </div>
        <button
          onClick={() => setShowConfirm(true)}
          className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-600 hover:text-rose-400 hover:bg-rose-500/10 transition shrink-0"
          aria-label="Delete memory"
        >
          <Trash2 size={13} />
        </button>
      </div>

      {/* Content */}
      <div className="relative">
        <p className={`text-xs text-slate-400 leading-relaxed ${!expanded && isLong ? 'line-clamp-3' : ''}`}>
          {memory.content}
        </p>
        {isLong && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-[11px] text-purple-400 hover:text-purple-300 mt-1 transition"
          >
            {expanded ? <><ChevronUp size={11} /> Show less</> : <><ChevronDown size={11} /> Show more</>}
          </button>
        )}
      </div>

      {/* Entities */}
      {(people.length > 0 || orgs.length > 0 || locs.length > 0 || skills.length > 0) && (
        <div className="mt-3 space-y-1.5">
          {people.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Users size={11} className="text-slate-500 shrink-0" />
              {people.slice(0, 3).map(p => <span key={p} className="badge badge-cyan">{p}</span>)}
            </div>
          )}
          {orgs.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Building2 size={11} className="text-slate-500 shrink-0" />
              {orgs.slice(0, 2).map(o => <span key={o} className="badge badge-amber">{o}</span>)}
            </div>
          )}
          {locs.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <MapPin size={11} className="text-slate-500 shrink-0" />
              {locs.slice(0, 2).map(l => <span key={l} className="badge badge-emerald">{l}</span>)}
            </div>
          )}
        </div>
      )}

      {/* Tags */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {tags.slice(0, 4).map(tag => (
            <span key={tag} className="badge badge-purple">
              <Tag size={9} className="mr-0.5" />{tag}
            </span>
          ))}
          {tags.length > 4 && <span className="badge badge-slate">+{tags.length - 4}</span>}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center gap-3 mt-3 pt-3 border-t border-white/5">
        {date && (
          <span className="flex items-center gap-1 text-[10px] text-slate-600">
            <Calendar size={9} /> {date}
          </span>
        )}
        {memory.source_document || memory.source_file ? (
          <span className="flex items-center gap-1 text-[10px] text-slate-600 truncate">
            <FileText size={9} /> {memory.source_document || memory.source_file}
          </span>
        ) : null}
      </div>

      {/* Delete confirm */}
      {showConfirm && (
        <div className="mt-3 pt-3 border-t border-rose-500/20 flex items-center gap-2 animate-fade-in">
          <p className="text-xs text-rose-400 flex-1">Delete this memory?</p>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="px-3 py-1 text-xs rounded-lg bg-rose-500/20 border border-rose-500/30 text-rose-400 hover:bg-rose-500/30 transition disabled:opacity-50"
          >
            {deleting ? '...' : 'Delete'}
          </button>
          <button
            onClick={() => setShowConfirm(false)}
            className="px-3 py-1 text-xs rounded-lg bg-slate-700/40 border border-white/10 text-slate-400 hover:text-white transition"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

function Memories() {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('newest');

  useEffect(() => { fetchMemories(); }, [filter]);

  const fetchMemories = async () => {
    const token = localStorage.getItem('token');
    setLoading(true);
    try {
      let url = filter !== 'all' ? `${API_BASE}/memories/type/${filter}` : `${API_BASE}/memories?limit=200`;
      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setMemories(await res.json());
    } catch (e) {
      console.error('Failed to fetch memories:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_BASE}/memories/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setMemories(prev => prev.filter(m => m.id !== id));
    } catch (e) {
      console.error('Delete failed:', e);
    }
  };

  const filtered = memories
    .filter(m => {
      if (!search) return true;
      const q = search.toLowerCase();
      return (m.title || '').toLowerCase().includes(q) ||
             (m.content || '').toLowerCase().includes(q) ||
             (m.tags || '').toLowerCase().includes(q);
    })
    .sort((a, b) => {
      if (sort === 'newest')     return new Date(b.created_at) - new Date(a.created_at);
      if (sort === 'oldest')     return new Date(a.created_at) - new Date(b.created_at);
      if (sort === 'importance') {
        const order = { high: 3, medium: 2, low: 1 };
        return (order[b.importance] || 0) - (order[a.importance] || 0);
      }
      return 0;
    });

  const filters = [
    { id: 'all', label: 'All' },
    ...Object.entries(TYPE_CONFIG).map(([id, c]) => ({ id, label: c.label })),
  ];

  return (
    <div className="min-h-screen flex">
      <div className="app-bg" />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col lg:ml-64 min-h-screen">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title="Memory Explorer" subtitle="Browse your extracted knowledge" />

        <main className="flex-1 p-5 md:p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">

            {/* Controls */}
            <div className="glass-card p-4 space-y-3">
              <div className="flex flex-col sm:flex-row gap-3">
                {/* Search */}
                <div className="flex-1 relative">
                  <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="Search memories..."
                    className="w-full pl-10 pr-10 py-2.5 glass-input rounded-xl text-sm placeholder-slate-500"
                    aria-label="Search memories"
                  />
                  {search && (
                    <button
                      onClick={() => setSearch('')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                    >
                      <X size={14} />
                    </button>
                  )}
                </div>

                {/* Sort */}
                <select
                  value={sort}
                  onChange={e => setSort(e.target.value)}
                  className="px-3 py-2.5 glass-input rounded-xl text-sm w-auto"
                  aria-label="Sort memories"
                >
                  <option value="newest">Newest first</option>
                  <option value="oldest">Oldest first</option>
                  <option value="importance">By importance</option>
                </select>

                <button
                  onClick={fetchMemories}
                  className="flex items-center gap-2 px-4 py-2.5 glass border border-white/10 rounded-xl text-sm text-slate-400 hover:text-white transition shrink-0"
                >
                  <RefreshCw size={14} />
                </button>
              </div>

              {/* Filter pills */}
              <div className="flex flex-wrap gap-2">
                {filters.map(f => (
                  <button
                    key={f.id}
                    onClick={() => setFilter(f.id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                      filter === f.id
                        ? 'bg-purple-600/30 border border-purple-500/50 text-purple-300'
                        : 'bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:border-purple-500/30'
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Results count */}
            {!loading && (
              <p className="text-xs text-slate-500">
                {filtered.length} memor{filtered.length !== 1 ? 'ies' : 'y'}
                {search ? ` matching "${search}"` : ''}
                {filter !== 'all' ? ` of type "${filter}"` : ''}
              </p>
            )}

            {/* Grid */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array(9).fill(0).map((_, i) => (
                  <div key={i} className="glass-card p-4">
                    <div className="skeleton h-4 w-3/4 mb-3 rounded" />
                    <div className="skeleton h-3 w-full mb-1 rounded" />
                    <div className="skeleton h-3 w-2/3 rounded" />
                  </div>
                ))}
              </div>
            ) : filtered.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filtered.map((m, i) => (
                  <div key={m.id} style={{ animationDelay: `${(i % 9) * 40}ms` }}>
                    <MemoryCard memory={m} onDelete={handleDelete} />
                  </div>
                ))}
              </div>
            ) : (
              <div className="glass-card p-12 text-center border-dashed">
                <Brain size={40} className="text-slate-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">
                  {search || filter !== 'all' ? 'No memories match your filters' : 'No memories yet'}
                </h3>
                <p className="text-sm text-slate-400">
                  {search || filter !== 'all'
                    ? 'Try different search terms or clear filters.'
                    : 'Upload documents to extract and save memories.'}
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
