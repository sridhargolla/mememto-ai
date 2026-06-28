function DocumentCard({ document, onDelete }) {
  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {
      pdf: '📕',
      txt: '📄',
      doc: '📘',
      docx: '📘',
      png: '🖼️',
      jpg: '🖼️',
      jpeg: '🖼️',
      gif: '🖼️',
      bmp: '🖼️',
      wav: '🎵',
      mp3: '🎵',
    };
    return icons[ext] || '📁';
  };

  const getFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-purple-500/50 transition-all duration-200 hover:shadow-lg hover:shadow-purple-500/10 group">
      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        <span className="text-3xl">{getFileIcon(document.filename || document.name)}</span>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white truncate">{document.filename || document.name}</h3>
          <p className="text-xs text-gray-400">
            {document.size ? getFileSize(document.size) : ''}
            {document.memories_count && ` • ${document.memories_count} memories`}
          </p>
        </div>
      </div>

      {/* Status */}
      {document.status && (
        <div className="mb-3">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            document.status === 'completed' 
              ? 'bg-green-500/20 text-green-400' 
              : document.status === 'processing'
              ? 'bg-yellow-500/20 text-yellow-400'
              : 'bg-red-500/20 text-red-400'
          }`}>
            {document.status}
          </span>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-700">
        <span className="text-xs text-gray-500">
          {document.uploaded_at ? new Date(document.uploaded_at).toLocaleDateString() : ''}
        </span>
        {onDelete && (
          <button
            onClick={() => onDelete(document.id)}
            className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-slate-700 rounded transition opacity-0 group-hover:opacity-100"
          >
            🗑️
          </button>
        )}
      </div>
    </div>
  );
}

export default DocumentCard;
