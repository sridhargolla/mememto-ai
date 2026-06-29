function MemoryCard({ memory, onEdit, onDelete }) {
  const getTypeIcon = (type) => {
    const icons = {
      person: '👤',
      event: '📅',
      experience: '💡',
      project: '🚀',
      education: '🎓',
      skill: '⚡',
      document: '📄',
    };
    return icons[type] || '🧠';
  };

  const getImportanceColor = (importance) => {
    const colors = {
      low: 'bg-green-500/20 text-green-400 border-green-500/30',
      medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      high: 'bg-red-500/20 text-red-400 border-red-500/30',
    };
    return colors[importance] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  return (
    <div className="glass-card-dark rounded-xl p-5 border border-slate-700/50 hover:border-purple-500/50 transition-all duration-200 hover:shadow-lg hover:shadow-purple-500/10 group premium-card">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{getTypeIcon(memory.memory_type)}</span>
          <div>
            <h3 className="font-semibold text-white">{memory.title}</h3>
            {memory.memory_type && (
              <span className="text-xs text-purple-400 capitalize">{memory.memory_type}</span>
            )}
          </div>
        </div>
        {memory.importance && (
          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getImportanceColor(memory.importance)}`}>
            {memory.importance}
          </span>
        )}
      </div>

      {/* Content */}
      <p className="text-gray-300 text-sm mb-4 line-clamp-3">{memory.content}</p>

      {/* Tags */}
      {memory.tags && (
        <div className="flex flex-wrap gap-2 mb-4">
          {memory.tags.split(',').map((tag, idx) => (
            <span
              key={idx}
              className="px-2 py-1 bg-slate-700/50 text-gray-300 text-xs rounded-full"
            >
              {tag.trim()}
            </span>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-700/50">
        <span className="text-xs text-gray-500">
          {new Date(memory.created_at).toLocaleDateString()}
        </span>
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          {onEdit && (
            <button
              onClick={() => onEdit(memory)}
              className="p-1.5 text-gray-400 hover:text-purple-400 hover:bg-slate-700/50 rounded transition"
            >
              ✏️
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(memory.id)}
              className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-slate-700/50 rounded transition"
            >
              🗑️
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default MemoryCard;
