function ChatMessage({ message, isLast, isLoading }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-purple-600' : 'bg-slate-600'
        }`}>
          {isUser ? '👤' : '🤖'}
        </div>

        {/* Message bubble */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className={`inline-block px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-purple-600 text-white rounded-br-sm'
              : 'bg-slate-700 text-gray-200 rounded-bl-sm'
          }`}>
            {/* Message content */}
            {message.content || (isLoading && isLast ? (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            ) : '')}

            {/* Source citations */}
            {message.sources && message.sources.length > 0 && (
              <div className="mt-3 pt-3 border-t border-slate-600">
                <p className="text-xs text-gray-400 mb-2 font-medium">Sources:</p>
                <ul className="space-y-1">
                  {message.sources.map((source, idx) => (
                    <li key={idx} className="text-xs flex items-start gap-2">
                      <span className="text-purple-400">📄</span>
                      <span className="text-gray-300">
                        {source.document && `${source.document} - `}
                        {source.memory}
                      </span>
                      {source.relevance_score !== undefined && (
                        <span className="text-purple-400 ml-2">
                          ({(source.relevance_score * 100).toFixed(0)}%)
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Performance Metrics */}
            {message.metrics && (
              <div className="mt-2 pt-2 border-t border-slate-600/40 text-[10px] text-gray-400 flex flex-wrap gap-x-3 gap-y-1 font-mono">
                <span title="Inference Time">⏱️ {message.metrics.inference_time_seconds}s</span>
                <span title="Generation Speed">⚡ {message.metrics.tokens_per_second} t/s</span>
                <span title="RAM Usage">💾 {message.metrics.memory_usage_mb} MB</span>
                <span title="Active Model" className="opacity-60">🤖 {message.metrics.model}</span>
              </div>
            )}

          </div>

          {/* Timestamp */}
          <p className="text-xs text-gray-500 mt-1">
            {message.timestamp || new Date().toLocaleTimeString()}
          </p>
        </div>
      </div>
    </div>
  );
}

export default ChatMessage;
