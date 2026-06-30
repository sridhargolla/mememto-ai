import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Brain, Search, Filter, Trash2, ChevronDown, ChevronUp,
  Calendar, Tag, FileText, Users, MapPin, Building2,
  Code, Star, SortAsc, RefreshCw, X, Edit, Download, Copy, Check, ExternalLink
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import BackgroundLayout from '../components/BackgroundLayout';
import { backgroundImages } from '../constants/backgrounds';

import API_BASE from '../config/api';

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

function MemoryCard({ memory, onDelete, onClick }) {
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

  const date = memory.created_at
    ? new Date(memory.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
    : '';

  const isLong = memory.content?.length > 200;

  const handleDelete = async (e) => {
    e.stopPropagation();
    setDeleting(true);
    await onDelete(memory.id);
    setDeleting(false);
    setShowConfirm(false);
  };

  return (
    <div 
      onClick={() => onClick(memory)}
      className="glass-card p-4 group animate-fade-in border border-transparent hover:border-purple-500/20 cursor-pointer flex flex-col justify-between h-full"
    >
      <div>
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
                  <span className={`w-1.5 h-1.5 rounded-full ${impCfg.dot}`} />
                  {impCfg.label}
                </span>
              )}
            </div>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); setShowConfirm(true); }}
            className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-600 hover:text-rose-400 hover:bg-rose-500/10 transition shrink-0"
            aria-label="Delete memory"
          >
            <Trash2 size={13} />
          </button>
        </div>

        {/* Content */}
        <div className="relative mt-2">
          <p className={`text-xs text-slate-400 leading-relaxed ${!expanded && isLong ? 'line-clamp-3' : ''}`}>
            {memory.content}
          </p>
        </div>

        {/* Entities */}
        {(people.length > 0 || orgs.length > 0 || locs.length > 0) && (
          <div className="mt-3 space-y-1">
            {people.length > 0 && (
              <div className="flex items-center gap-1 flex-wrap">
                <span className="text-[10px] text-slate-500 font-medium">People:</span>
                {people.slice(0, 2).map(p => <span key={p} className="badge badge-cyan">{p}</span>)}
              </div>
            )}
          </div>
        )}

        {/* Tags */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {tags.slice(0, 3).map(tag => (
              <span key={tag} className="badge badge-purple">
                <Tag size={9} className="mr-0.5" />{tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-[10px] text-slate-600">
        {date && (
          <span className="flex items-center gap-1">
            <Calendar size={9} /> {date}
          </span>
        )}
        {(memory.source_document || memory.source_file) && (
          <span className="truncate max-w-[120px] flex items-center gap-1" title={memory.source_document || memory.source_file}>
            <FileText size={9} /> {memory.source_document || memory.source_file}
          </span>
        )}
      </div>

      {/* Delete confirm inline */}
      {showConfirm && (
        <div className="mt-3 pt-3 border-t border-rose-500/20 flex items-center gap-2 animate-fade-in" onClick={e => e.stopPropagation()}>
          <p className="text-[10px] text-rose-400 flex-1">Delete memory?</p>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="px-2.5 py-1 text-[10px] rounded-lg bg-rose-500/20 border border-rose-500/30 text-rose-400 hover:bg-rose-500/30 transition disabled:opacity-50 font-semibold"
          >
            Delete
          </button>
          <button
            onClick={() => setShowConfirm(false)}
            className="px-2.5 py-1 text-[10px] rounded-lg bg-slate-700/40 border border-white/10 text-slate-400 hover:text-white transition"
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

  // Preview Modal States
  const [selectedMemory, setSelectedMemory] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editTags, setEditTags] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => { fetchMemories(); }, [filter]);

  const fetchMemories = async () => {
    const token = localStorage.getItem('token');
    setLoading(true);
    try {
      let url = filter !== 'all' ? `${API_BASE}/memories/tag/${filter}` : `${API_BASE}/memories?limit=200`;
      // Check if filter corresponds to memory_type
      if (filter !== 'all' && ['person', 'event', 'experience', 'project', 'education', 'skill', 'document'].includes(filter)) {
        url = `${API_BASE}/memories/type/${filter}`;
      }
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
      if (res.ok) {
        setMemories(prev => prev.filter(m => m.id !== id));
        if (selectedMemory?.id === id) {
          setSelectedMemory(null);
        }
      }
    } catch (e) {
      console.error('Delete failed:', e);
    }
  };

  const handleCardClick = (memory) => {
    setSelectedMemory(memory);
    setEditTitle(memory.title || '');
    setEditContent(memory.content || '');
    setEditTags(memory.tags || '');
    setIsEditing(false);
    setCopied(false);
  };

  const handleSaveEdit = async () => {
    if (!selectedMemory) return;
    setSavingEdit(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_BASE}/memories/${selectedMemory.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title: editTitle,
          content: editContent,
          tags: editTags,
          memory_type: selectedMemory.memory_type,
          importance: selectedMemory.importance,
          source_document: selectedMemory.source_document || selectedMemory.source_file || ''
        })
      });
      if (res.ok) {
        const updated = await res.json();
        // Update in list
        setMemories(prev => prev.map(m => m.id === updated.id ? updated : m));
        setSelectedMemory(updated);
        setIsEditing(false);
      }
    } catch (err) {
      console.error('Failed to save memory edit:', err);
    } finally {
      setSavingEdit(false);
    }
  };

  const handleCopyContent = async () => {
    if (!selectedMemory) return;
    try {
      await navigator.clipboard.writeText(selectedMemory.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy memory content:', err);
    }
  };

  const handleDownload = (format) => {
    if (!selectedMemory) return;
    let mime = 'text/plain';
    let ext = 'txt';
    let dataStr = '';

    if (format === 'json') {
      mime = 'application/json';
      ext = 'json';
      dataStr = JSON.stringify(selectedMemory, null, 2);
    } else if (format === 'md') {
      mime = 'text/markdown';
      ext = 'md';
      dataStr = `# ${selectedMemory.title}\n\n- **Type**: ${selectedMemory.memory_type}\n- **Importance**: ${selectedMemory.importance}\n- **Date**: ${selectedMemory.created_at}\n\n## Content\n${selectedMemory.content}`;
    } else {
      dataStr = `Title: ${selectedMemory.title}\nType: ${selectedMemory.memory_type}\nImportance: ${selectedMemory.importance}\nDate: ${selectedMemory.created_at}\n\nContent:\n${selectedMemory.content}`;
    }

    const blob = new Blob([dataStr], { type: mime });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `memory_${selectedMemory.id}.${ext}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
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

  // Helper to resolve preview elements
  const renderSourcePreview = (filename) => {
    if (!filename) return null;
    const lower = filename.toLowerCase();
    const sourceUrl = `/api/uploads/${encodeURIComponent(filename)}`;

    if (lower.endsWith('.pdf')) {
      return (
        <iframe src={sourceUrl} className="w-full h-[350px] md:h-[450px] rounded-xl border border-white/5 bg-slate-900" title="PDF Preview" />
      );
    }
    if (lower.endsWith('.png') || lower.endsWith('.jpg') || lower.endsWith('.jpeg') || lower.endsWith('.webp') || lower.endsWith('.gif')) {
      return (
        <div className="w-full flex items-center justify-center p-2 border border-white/5 rounded-xl bg-slate-900 overflow-hidden h-[350px] md:h-[450px]">
          <img src={sourceUrl} alt="Source Preview" className="max-w-full max-h-full object-contain rounded" />
        </div>
      );
    }
    if (lower.endsWith('.mp3') || lower.endsWith('.wav') || lower.endsWith('.ogg') || lower.endsWith('.m4a')) {
      return (
        <div className="w-full p-6 border border-white/5 rounded-xl bg-slate-900 flex flex-col items-center justify-center h-[350px] md:h-[450px] gap-4">
          <Brain size={48} className="text-purple-400 animate-pulse" />
          <p className="text-xs text-slate-400 font-medium">Audio Recording Transcription</p>
          <audio controls src={sourceUrl} className="w-full max-w-xs mt-2" />
        </div>
      );
    }
    if (lower.endsWith('.mp4') || lower.endsWith('.webm')) {
      return (
        <div className="w-full p-2 border border-white/5 rounded-xl bg-slate-900 flex items-center justify-center h-[350px] md:h-[450px]">
          <video controls src={sourceUrl} className="max-w-full max-h-full rounded" />
        </div>
      );
    }

    return (
      <div className="w-full p-6 border border-white/5 rounded-xl bg-slate-900/60 flex flex-col items-center justify-center h-[350px] md:h-[450px] text-center gap-2">
        <FileText size={40} className="text-slate-500 mb-2" />
        <p className="text-xs text-slate-300 font-medium">{filename}</p>
        <p className="text-[10px] text-slate-500">Document contents extracted as memory content on the left panel.</p>
        <a 
          href={sourceUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="mt-4 flex items-center gap-1.5 text-xs text-purple-400 hover:text-purple-300 font-medium transition"
        >
          <ExternalLink size={12} />
          Open File in New Tab
        </a>
      </div>
    );
  };

  return (
    <BackgroundLayout image={backgroundImages.memories}>
      <div className="min-h-screen flex">
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
                  className="px-3 py-2.5 glass-input rounded-xl text-sm w-auto cursor-pointer"
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
                    <MemoryCard memory={m} onDelete={handleDelete} onClick={handleCardClick} />
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

      {/* Details & Live Preview Modal */}
      {selectedMemory && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-5xl glass border border-white/10 rounded-2xl flex flex-col max-h-[90vh] overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/5">
              <div className="flex items-center gap-2">
                <Brain className="text-purple-400" size={18} />
                <h3 className="text-sm font-bold text-white">Memory Details & Live Preview</h3>
              </div>
              <button
                onClick={() => setSelectedMemory(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition"
              >
                <X size={16} />
              </button>
            </div>

            {/* Split Pane Body */}
            <div className="flex-1 overflow-y-auto p-5 grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Pane: Interactive Details & Meta */}
              <div className="space-y-4 flex flex-col justify-between">
                <div className="space-y-4">
                  {isEditing ? (
                    <div className="space-y-3">
                      <div>
                        <label className="text-[10px] text-slate-400 font-semibold tracking-wider block mb-1">TITLE</label>
                        <input
                          type="text"
                          value={editTitle}
                          onChange={e => setEditTitle(e.target.value)}
                          className="w-full px-3 py-2 bg-slate-900 border border-purple-500/40 rounded-xl text-sm text-white focus:outline-none focus:border-purple-500"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-400 font-semibold tracking-wider block mb-1">CONTENT</label>
                        <textarea
                          value={editContent}
                          onChange={e => setEditContent(e.target.value)}
                          rows={6}
                          className="w-full px-3 py-2 bg-slate-900 border border-purple-500/40 rounded-xl text-sm text-white focus:outline-none focus:border-purple-500 resize-none leading-relaxed"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-400 font-semibold tracking-wider block mb-1">TAGS (comma separated)</label>
                        <input
                          type="text"
                          value={editTags}
                          onChange={e => setEditTags(e.target.value)}
                          className="w-full px-3 py-2 bg-slate-900 border border-purple-500/40 rounded-xl text-sm text-white focus:outline-none focus:border-purple-500"
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div>
                        <h2 className="text-lg font-bold text-white leading-snug">{selectedMemory.title}</h2>
                        <div className="flex flex-wrap items-center gap-1.5 mt-2">
                          <span className="badge badge-purple">{selectedMemory.memory_type}</span>
                          <span className="badge badge-slate">{selectedMemory.importance} importance</span>
                        </div>
                      </div>
                      <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5">
                        <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">{selectedMemory.content}</p>
                      </div>
                      {selectedMemory.tags && (
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <Tag size={10} className="text-slate-500" />
                          {selectedMemory.tags.split(',').map(tag => (
                            <span key={tag} className="badge badge-purple text-[10px]">{tag.trim()}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Metadata fields */}
                  <div className="pt-4 border-t border-white/5 space-y-2">
                    <h4 className="text-[10px] text-slate-500 font-bold tracking-wider">METADATA</h4>
                    <div className="grid grid-cols-2 gap-3 text-[11px]">
                      <div>
                        <span className="text-slate-500 block">Created On</span>
                        <span className="text-slate-300 font-medium">{new Date(selectedMemory.created_at).toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">Source Document</span>
                        <span className="text-slate-300 font-medium truncate block max-w-[200px]" title={selectedMemory.source_document || selectedMemory.source_file || 'Personal knowledge'}>
                          {selectedMemory.source_document || selectedMemory.source_file || 'Personal knowledge'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Left Pane Actions */}
                <div className="pt-4 border-t border-white/5 flex flex-wrap gap-2 justify-between items-center">
                  <div className="flex gap-2">
                    {isEditing ? (
                      <>
                        <button
                          onClick={handleSaveEdit}
                          disabled={savingEdit}
                          className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition disabled:opacity-50"
                        >
                          {savingEdit ? 'Saving...' : 'Save'}
                        </button>
                        <button
                          onClick={() => setIsEditing(false)}
                          className="px-4 py-2 rounded-xl bg-slate-800 border border-white/5 hover:bg-slate-700 text-slate-300 text-xs font-bold transition"
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => setIsEditing(true)}
                          className="px-4 py-2 rounded-xl bg-purple-600/20 border border-purple-500/30 hover:bg-purple-600/30 text-purple-300 text-xs font-bold transition flex items-center gap-1.5"
                        >
                          <Edit size={12} />
                          Edit
                        </button>
                        <button
                          onClick={handleCopyContent}
                          className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                            copied 
                              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                              : 'bg-slate-800 border border-white/5 hover:bg-slate-700 text-slate-300'
                          }`}
                        >
                          {copied ? <Check size={12} /> : <Copy size={12} />}
                          {copied ? 'Copied!' : 'Copy'}
                        </button>
                      </>
                    )}
                  </div>

                  {/* Format downloads */}
                  {!isEditing && (
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] text-slate-500 font-semibold uppercase">Download:</span>
                      <button
                        onClick={() => handleDownload('txt')}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-slate-300 font-medium transition"
                      >
                        TXT
                      </button>
                      <button
                        onClick={() => handleDownload('md')}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-slate-300 font-medium transition"
                      >
                        MD
                      </button>
                      <button
                        onClick={() => handleDownload('json')}
                        className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-slate-300 font-medium transition"
                      >
                        JSON
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Pane: Live Document Preview Frame */}
              <div className="space-y-2">
                <h4 className="text-[10px] text-slate-400 font-bold tracking-wider flex items-center gap-1">
                  <FileText size={12} className="text-purple-400" />
                  ORIGINAL SOURCE PREVIEW
                </h4>
                {renderSourcePreview(selectedMemory.source_document || selectedMemory.source_file)}
              </div>
            </div>
          </div>
        </div>
      )}
    </BackgroundLayout>
  );
}

export default Memories;
