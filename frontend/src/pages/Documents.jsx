import { useState, useEffect, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../AuthContext';
import {
  Upload, FileText, Image, FileType, X, CheckCircle,
  AlertCircle, Trash2, Calendar, Brain, Search,
  RefreshCw, File, Music, Video, Archive, Code
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';

import API_BASE from '../config/api';

// ── File type helpers ──────────────────────────────────────────────────────────
function getFileIcon(filename) {
  const ext = (filename?.split('.').pop() || '').toLowerCase();
  const IMAGE = ['png','jpg','jpeg','gif','bmp','tiff','webp','svg','ico'];
  const VIDEO = ['mp4','mov','avi','mkv','webm','flv','wmv','mpeg','mpg','3gp','m4v'];
  const AUDIO = ['mp3','wav','ogg','flac','aac','m4a','wma','opus'];
  const DOC   = ['pdf','doc','docx','odt','rtf'];
  const CODE  = ['py','js','ts','jsx','tsx','java','c','cpp','cs','go','rs','html','css','json','xml','yaml','yml','md','csv'];
  const ZIP   = ['zip','tar','gz','rar','7z','bz2'];
  if (ext === 'pdf')       return { icon: FileText, color: 'text-rose-400',    bg: 'bg-rose-500/15',    label: 'PDF' };
  if (DOC.includes(ext))   return { icon: FileText, color: 'text-orange-400',  bg: 'bg-orange-500/15',  label: 'DOC' };
  if (IMAGE.includes(ext)) return { icon: Image,    color: 'text-blue-400',    bg: 'bg-blue-500/15',    label: 'IMAGE' };
  if (VIDEO.includes(ext)) return { icon: Video,    color: 'text-purple-400',  bg: 'bg-purple-500/15',  label: 'VIDEO' };
  if (AUDIO.includes(ext)) return { icon: Music,    color: 'text-pink-400',    bg: 'bg-pink-500/15',    label: 'AUDIO' };
  if (CODE.includes(ext))  return { icon: Code,     color: 'text-emerald-400', bg: 'bg-emerald-500/15', label: 'CODE' };
  if (ZIP.includes(ext))   return { icon: Archive,  color: 'text-yellow-400',  bg: 'bg-yellow-500/15',  label: 'ARCHIVE' };
  if (ext === 'txt')       return { icon: FileType, color: 'text-cyan-400',    bg: 'bg-cyan-500/15',    label: 'TXT' };
  return                          { icon: File,     color: 'text-slate-400',   bg: 'bg-slate-500/15',   label: ext.toUpperCase() || 'FILE' };
}

// ── Toast ──────────────────────────────────────────────────────────────────────
function Toast({ message, type, onClose }) {
  useEffect(() => { const t = setTimeout(onClose, 5000); return () => clearTimeout(t); }, []);
  const styles = { success: 'toast-success', error: 'toast-error', info: 'toast-info' };
  return (
    <div className={`toast ${styles[type] || ''}`}>
      {type === 'success' && <CheckCircle size={16} className="text-emerald-400 shrink-0" />}
      {type === 'error'   && <AlertCircle size={16} className="text-rose-400 shrink-0" />}
      {type === 'info'    && <Brain size={16} className="text-cyan-400 shrink-0" />}
      <span className="flex-1">{message}</span>
      <button onClick={onClose} className="text-slate-500 hover:text-white ml-2"><X size={14} /></button>
    </div>
  );
}

// ── Upload progress ────────────────────────────────────────────────────────────
function UploadProgress({ filename, progress }) {
  return (
    <div className="glass-card p-5 border border-purple-500/20 animate-scale-in">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-9 h-9 rounded-xl bg-purple-500/20 flex items-center justify-center">
          <Upload size={18} className="text-purple-400 animate-bounce" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white truncate max-w-xs">Saving {filename}</p>
          <p className="text-xs text-slate-400">Storing to your memory bank…</p>
        </div>
      </div>
      <div className="progress-bar">
        <div className="progress-bar-fill" style={{ width: `${progress}%`, transition: 'width 0.4s ease' }} />
      </div>
    </div>
  );
}

// ── Document card ──────────────────────────────────────────────────────────────
function DocumentCard({ doc, onDelete }) {
  const [deleting, setDeleting]       = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const name = doc.source_file || doc.title || 'Untitled';
  const { icon: Icon, color, bg, label } = getFileIcon(name);

  let sizeStr = '';
  try {
    const meta = doc.json_metadata ? JSON.parse(doc.json_metadata) : null;
    if (meta?.file_size_human) sizeStr = meta.file_size_human;
  } catch {}

  const date = doc.created_at
    ? new Date(doc.created_at).toLocaleDateString(undefined, { month:'short', day:'numeric', year:'numeric' })
    : 'Unknown';

  const handleDelete = async () => {
    setDeleting(true);
    await onDelete(doc.id);
    setDeleting(false);
    setShowConfirm(false);
  };

  // Strip the metadata header from content preview
  const preview = (doc.content || '')
    .replace(/^(File|Type|Size|Uploaded|Uploaded by):.*\n?/gm, '')
    .replace(/^Note:.*$/m, '')
    .trim()
    .slice(0, 120);

  return (
    <div className="glass-card p-4 group animate-fade-in hover:border-purple-500/30 transition">
      <div className="flex items-start gap-3">
        <div className={`w-11 h-11 rounded-xl ${bg} flex items-center justify-center shrink-0`}>
          <Icon size={20} className={color} />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-white truncate">{name}</h4>
          <div className="flex flex-wrap items-center gap-2 mt-1">
            <span className="flex items-center gap-1 text-xs text-slate-500"><Calendar size={10} />{date}</span>
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${bg} ${color}`}>{label}</span>
            {sizeStr && <span className="text-xs text-slate-500">{sizeStr}</span>}
          </div>
          {preview && <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">{preview}</p>}
        </div>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition shrink-0">
          <button onClick={() => setShowConfirm(true)}
            className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition" title="Delete">
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {showConfirm && (
        <div className="mt-3 pt-3 border-t border-white/5 flex items-center gap-2 animate-fade-in">
          <p className="text-xs text-rose-400 flex-1">Delete this file memory?</p>
          <button onClick={handleDelete} disabled={deleting}
            className="px-3 py-1 text-xs rounded-lg bg-rose-500/20 border border-rose-500/30 text-rose-400 hover:bg-rose-500/30 transition disabled:opacity-50">
            {deleting ? 'Deleting…' : 'Confirm'}
          </button>
          <button onClick={() => setShowConfirm(false)}
            className="px-3 py-1 text-xs rounded-lg bg-slate-700/40 border border-white/10 text-slate-400 hover:text-white transition">
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
function Documents() {
  const { t } = useTranslation();
  const { authFetch } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [documents,   setDocuments]   = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [uploadState, setUploadState] = useState(null);
  const [dragOver,    setDragOver]    = useState(false);
  const [toasts,      setToasts]      = useState([]);
  const [search,      setSearch]      = useState('');
  const dropZoneRef  = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => { fetchDocuments(); }, []);

  const addToast    = useCallback((msg, type='info') => setToasts(p => [...p, { id: Date.now(), message: msg, type }]), []);
  const removeToast = useCallback((id) => setToasts(p => p.filter(t => t.id !== id)), []);

  const fetchDocuments = async () => {
    try {
      const res = await authFetch(`${API_BASE}/documents`);
      if (res.ok) setDocuments(await res.json());
    } catch (err) {
      if (!err.message?.includes('Session expired')) {
        addToast('Cannot connect to backend. Is the server running?', 'error');
      }
    } finally { setLoading(false); }
  };

  const uploadFile = async (file) => {
    if (!file) return;
    if (file.size > 500 * 1024 * 1024) { addToast('File too large. Maximum 500 MB.', 'error'); return; }

    setUploadState({ filename: file.name, progress: 10 });

    // Animate progress bar while waiting for server
    const tick = setInterval(() =>
      setUploadState(prev => prev ? { ...prev, progress: Math.min(prev.progress + 12, 85) } : null), 250);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const res  = await authFetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      clearInterval(tick);

      if (res.ok) {
        setUploadState(prev => prev ? { ...prev, progress: 100 } : null);
        setTimeout(() => setUploadState(null), 600);
        addToast(`✅ ${file.name} saved to memories!`, 'success');
        await fetchDocuments();
      } else {
        throw new Error(data.detail || `Server error: ${res.status}`);
      }
    } catch (err) {
      clearInterval(tick);
      setUploadState(null);
      if (!err.message?.includes('Session expired')) {
        addToast(`Upload failed: ${err.message}`, 'error');
      }
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleFileInput = (e) => uploadFile(e.target.files?.[0]);
  const handleDrop      = (e) => { e.preventDefault(); setDragOver(false); uploadFile(e.dataTransfer.files?.[0]); };

  const handleDelete = async (docId) => {
    try {
      const res = await authFetch(`${API_BASE}/documents/${docId}`, { method: 'DELETE' });
      if (res.ok) { await fetchDocuments(); addToast('File deleted.', 'info'); }
      else addToast('Failed to delete.', 'error');
    } catch (err) {
      if (!err.message?.includes('Session expired')) addToast('Connection error.', 'error');
    }
  };

  const filteredDocs = documents.filter(doc => {
    if (!search) return true;
    return (doc.source_file || doc.title || '').toLowerCase().includes(search.toLowerCase());
  });

  // Category counts
  const categories = filteredDocs.reduce((acc, d) => {
    try { const m = JSON.parse(d.json_metadata || '{}'); const k = m.file_type || 'file'; acc[k] = (acc[k]||0)+1; } catch {}
    return acc;
  }, {});

  return (
    <div className="min-h-screen flex">
      <div className="app-bg" />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col lg:ml-64 min-h-screen">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title="Files & Memories" subtitle="Upload anything — documents, media, code — saved instantly as memories" />

        <main className="flex-1 p-5 md:p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">

            {uploadState && <UploadProgress filename={uploadState.filename} progress={uploadState.progress} />}

            {!uploadState && (
              <div
                ref={dropZoneRef}
                className={`drop-zone p-10 flex flex-col items-center justify-center text-center transition-all duration-300 ${dragOver ? 'drag-over' : ''}`}
                onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                role="button" tabIndex={0}
                onKeyDown={e => e.key === 'Enter' && fileInputRef.current?.click()}
              >
                {/* Accept all file types */}
                <input ref={fileInputRef} type="file" className="hidden" accept="*/*" onChange={handleFileInput} />
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition ${dragOver ? 'bg-purple-500/30 scale-110' : 'bg-purple-500/10'}`}>
                  <Upload size={28} className={`transition ${dragOver ? 'text-purple-300' : 'text-purple-500'}`} />
                </div>
                <h3 className="text-lg font-semibold text-white mb-1">
                  {dragOver ? 'Drop to save as memory!' : 'Drop any file here or click to browse'}
                </h3>
                <p className="text-sm text-slate-400 mb-4">All file types supported — documents, images, audio, video, code, archives…</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {['PDF','DOCX','MP4','MP3','PNG','JPG','ZIP','PY','JS','ANY'].map(type => (
                    <span key={type} className="badge badge-purple text-xs">{type}</span>
                  ))}
                </div>
                <p className="text-xs text-slate-600 mt-3">Max 500 MB · Files saved as memories instantly (no AI delay)</p>
              </div>
            )}

            {/* Search bar */}
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input type="text" value={search} onChange={e => setSearch(e.target.value)}
                  placeholder="Search files…"
                  className="w-full pl-10 pr-4 py-2.5 glass-input rounded-xl text-sm placeholder-slate-500" />
              </div>
              <button onClick={fetchDocuments}
                className="flex items-center gap-2 px-4 py-2.5 glass border border-white/10 rounded-xl text-sm text-slate-400 hover:text-white hover:border-purple-500/30 transition">
                <RefreshCw size={14} /> Refresh
              </button>
            </div>

            {/* Stats */}
            {filteredDocs.length > 0 && (
              <div className="flex flex-wrap gap-3 text-xs text-slate-500">
                <span>{filteredDocs.length} file{filteredDocs.length !== 1 ? 's' : ''}</span>
                {Object.entries(categories).map(([cat, count]) => (
                  <span key={cat} className="badge badge-slate capitalize">{cat}: {count}</span>
                ))}
              </div>
            )}

            {/* Grid */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array(6).fill(0).map((_, i) => (
                  <div key={i} className="glass-card p-4">
                    <div className="flex gap-3">
                      <div className="skeleton w-11 h-11 rounded-xl" />
                      <div className="flex-1"><div className="skeleton h-4 w-3/4 mb-2 rounded" /><div className="skeleton h-3 w-1/2 rounded" /></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : filteredDocs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredDocs.map(doc => <DocumentCard key={doc.id} doc={doc} onDelete={handleDelete} />)}
              </div>
            ) : (
              <div className="glass-card p-12 text-center border-dashed">
                <Upload size={40} className="text-slate-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">
                  {search ? 'No files match your search' : 'No files yet'}
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  {search ? 'Try a different search term.' : 'Upload any file — it will be saved as a searchable memory.'}
                </p>
                {!search && (
                  <button onClick={() => fileInputRef.current?.click()}
                    className="px-5 py-2.5 rounded-xl bg-purple-600/20 border border-purple-500/30 text-purple-400 text-sm hover:bg-purple-600/30 transition">
                    Upload First File
                  </button>
                )}
              </div>
            )}
          </div>
        </main>
      </div>

      <div className="toast-container">
        {toasts.map(t => <Toast key={t.id} message={t.message} type={t.type} onClose={() => removeToast(t.id)} />)}
      </div>
    </div>
  );
}

export default Documents;
