import { useState, useCallback } from 'react';
import MarkdownMessage from './MarkdownMessage';

function ChatMessage({ message, isLast, isLoading, onRegenerate }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const isStreaming = isLoading && isLast && !isUser;
  const isEmpty = !message.content && isStreaming;

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(message.content || '').then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [message.content]);

  const formatTime = (ts) => {
    if (!ts) return '';
    const d = new Date(ts);
    return isNaN(d) ? ts : d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-5 animate-fade-in-up`}
      aria-label={`${isUser ? 'You' : 'Memento AI'}: ${message.content || 'Typing…'}`}
    >
      <div className={`flex max-w-[85%] lg:max-w-[78%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3 items-start`}>

        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shadow-lg mt-0.5 ${
          isUser
            ? 'bg-gradient-to-br from-purple-500 to-indigo-600 text-white'
            : 'bg-gradient-to-br from-slate-700 to-slate-800 text-purple-300 border border-purple-500/20'
        }`}>
          {isUser ? (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          ) : '🤖'}
        </div>

        {/* Bubble */}
        <div className="flex-1 min-w-0">
          <div className={`
            rounded-2xl px-4 py-3 relative group
            ${isUser
              ? 'bg-gradient-to-br from-purple-600 to-indigo-700 text-white rounded-tr-sm shadow-lg shadow-purple-900/20'
              : 'glass-card rounded-tl-sm text-slate-200'
            }
          `}>

            {/* Content */}
            {isEmpty ? (
              // Typing indicator
              <div className="flex items-center gap-1.5 py-1" aria-label="Memento AI is typing">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            ) : isUser ? (
              <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{message.content}</p>
            ) : (
              <MarkdownMessage content={message.content} isStreaming={isStreaming} />
            )}

            {/* Source citations */}
            {!isUser && message.sources && message.sources.length > 0 && (
              <div className="mt-3 pt-3 border-t border-white/10">
                <button
                  onClick={() => setSourcesOpen(o => !o)}
                  className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-purple-400 transition font-medium"
                  aria-expanded={sourcesOpen}
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
                  <svg className={`w-3 h-3 transition-transform ${sourcesOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {sourcesOpen && (
                  <div className="mt-2 space-y-2">
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="flex flex-col gap-1 px-3 py-2 bg-black/20 rounded-lg border border-white/5">
                        <div className="flex items-start gap-2">
                          <span className="text-purple-400 flex-shrink-0 mt-0.5">📄</span>
                          <div className="flex-1 min-w-0">
                            {source.document && (
                              <p className="text-[11px] font-semibold text-slate-300 truncate">{source.document}</p>
                            )}
                            <p className="text-[11px] text-slate-400 leading-snug mt-0.5 line-clamp-2">{source.memory}</p>
                          </div>
                          {source.relevance_score !== undefined && (
                            <span className="flex-shrink-0 text-[10px] text-purple-400 font-mono">
                              {(source.relevance_score * 100).toFixed(0)}%
                            </span>
                          )}
                        </div>
                        {source.relevance_score !== undefined && (
                          <div className="progress-bar h-0.5 mt-1">
                            <div
                              className="progress-fill h-0.5"
                              style={{ width: `${(source.relevance_score * 100).toFixed(0)}%` }}
                            />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Performance metrics */}
            {!isUser && message.metrics && (
              <div className="mt-2 pt-2 border-t border-white/5 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-slate-500 font-mono">
                <span title="Inference time">⏱ {message.metrics.inference_time_seconds}s</span>
                <span title="Tokens per second">⚡ {message.metrics.tokens_per_second} t/s</span>
                <span title="Memory usage">💾 {message.metrics.memory_usage_mb} MB</span>
                {message.metrics.cached && <span title="Cached response">📦 cached</span>}
              </div>
            )}
          </div>

          {/* Actions row */}
          {!isUser && message.content && (
            <div className="flex items-center gap-2 mt-1.5 opacity-0 group-hover:opacity-100 transition-opacity" style={{ marginLeft: '2px' }}>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 px-2 py-1 text-[11px] text-slate-500 hover:text-slate-300 hover:bg-white/5 rounded transition"
                title="Copy response"
                aria-label={copied ? 'Copied!' : 'Copy response'}
              >
                {copied ? (
                  <><span>✓</span><span>Copied</span></>
                ) : (
                  <>
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <span>Copy</span>
                  </>
                )}
              </button>
              {isLast && onRegenerate && (
                <button
                  onClick={onRegenerate}
                  className="flex items-center gap-1 px-2 py-1 text-[11px] text-slate-500 hover:text-purple-400 hover:bg-purple-500/5 rounded transition"
                  title="Regenerate response"
                  aria-label="Regenerate response"
                >
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Regenerate</span>
                </button>
              )}
            </div>
          )}

          {/* Timestamp */}
          <p className={`text-[10px] text-slate-600 mt-1 ${isUser ? 'text-right' : 'text-left'}`} style={{ marginLeft: isUser ? 0 : '2px' }}>
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    </div>
  );
}

export default ChatMessage;
