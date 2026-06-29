import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, Brain, User, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';

function CopyButton({ text, className = '' }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <button
      onClick={handleCopy}
      title="Copy"
      aria-label={copied ? 'Copied!' : 'Copy to clipboard'}
      className={`flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg transition-all duration-200 ${
        copied
          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
          : 'bg-white/5 text-slate-400 hover:text-slate-200 hover:bg-white/10 border border-white/5'
      } ${className}`}
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
      <span>{copied ? 'Copied!' : 'Copy'}</span>
    </button>
  );
}

function CodeBlock({ language, children }) {
  const [copied, setCopied] = useState(false);
  const code = String(children).replace(/\n$/, '');

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="code-block-wrapper">
      <div className="code-block-header">
        <span className="text-purple-400/80">{language || 'code'}</span>
        <button
          onClick={handleCopy}
          className="code-copy-btn flex items-center gap-1"
          aria-label="Copy code"
        >
          {copied ? <Check size={11} /> : <Copy size={11} />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <SyntaxHighlighter
        style={oneDark}
        language={language || 'text'}
        PreTag="div"
        customStyle={{
          margin: 0,
          borderRadius: '0 0 10px 10px',
          border: '1px solid rgba(100,116,139,0.2)',
          borderTop: 'none',
          fontSize: '0.8125rem',
          background: 'rgba(5, 6, 20, 0.95)',
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

function SourceCitations({ sources }) {
  const [expanded, setExpanded] = useState(false);
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-white/5">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs text-slate-400 hover:text-purple-400 transition mb-2"
      >
        <ExternalLink size={12} />
        <span className="font-medium">{sources.length} source{sources.length !== 1 ? 's' : ''} used</span>
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>
      {expanded && (
        <div className="space-y-1.5 animate-fade-in">
          {sources.map((source, idx) => (
            <div
              key={idx}
              className="flex items-start gap-2 p-2 rounded-lg bg-purple-500/5 border border-purple-500/15"
            >
              <span className="text-[10px] font-bold text-purple-400/60 mt-0.5 shrink-0">#{idx + 1}</span>
              <div className="min-w-0">
                <p className="text-xs text-slate-300 font-medium truncate">
                  {source.memory}
                </p>
                {source.document && (
                  <p className="text-[10px] text-slate-500 truncate mt-0.5">
                    📄 {source.document}
                  </p>
                )}
                {source.relevance_score !== undefined && (
                  <div className="flex items-center gap-1.5 mt-1">
                    <div className="h-1 w-16 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-500 rounded-full"
                        style={{ width: `${Math.round(source.relevance_score * 100)}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-slate-500">
                      {Math.round(source.relevance_score * 100)}% match
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MetricsBadge({ metrics }) {
  if (!metrics) return null;
  return (
    <div className="mt-2 pt-2 border-t border-white/5 flex flex-wrap gap-x-4 gap-y-1">
      <span className="text-[10px] text-slate-500 font-mono" title="Inference Time">
        ⏱ {metrics.inference_time_seconds}s
      </span>
      <span className="text-[10px] text-slate-500 font-mono" title="Speed">
        ⚡ {metrics.tokens_per_second} t/s
      </span>
      <span className="text-[10px] text-slate-500 font-mono" title="RAM">
        💾 {metrics.memory_usage_mb} MB
      </span>
      {metrics.cached && (
        <span className="text-[10px] text-cyan-500/60 font-mono">✦ cached</span>
      )}
    </div>
  );
}

function ChatMessage({ message, isLast, isLoading, onRegenerate }) {
  const isUser = message.role === 'user';
  const isEmpty = !message.content && isLoading && isLast;
  const time = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-5 animate-fade-in group`}>
      <div className={`flex gap-3 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>

        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center shadow-lg ${
          isUser
            ? 'bg-gradient-to-br from-purple-500 to-violet-600 shadow-purple-900/40'
            : 'bg-gradient-to-br from-slate-600 to-slate-700 shadow-slate-900/40 border border-white/5'
        }`}>
          {isUser ? <User size={15} className="text-white" /> : <Brain size={15} className="text-purple-300" />}
        </div>

        {/* Message */}
        <div className={`flex-1 ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
          {/* Role label */}
          <span className={`text-[10px] font-semibold tracking-wider ${
            isUser ? 'text-purple-400/60 text-right' : 'text-slate-500'
          }`}>
            {isUser ? 'YOU' : 'MEMENTO AI'}
          </span>

          {/* Bubble */}
          <div className={`relative px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-gradient-to-br from-purple-600 to-violet-700 text-white rounded-tr-sm shadow-lg shadow-purple-900/30'
              : 'glass-card text-slate-200 rounded-tl-sm'
          }`}>

            {/* Typing indicator */}
            {isEmpty ? (
              <div className="flex items-center gap-1.5 py-1">
                <span className="w-2 h-2 rounded-full bg-purple-400 typing-dot" />
                <span className="w-2 h-2 rounded-full bg-purple-400 typing-dot" />
                <span className="w-2 h-2 rounded-full bg-purple-400 typing-dot" />
              </div>
            ) : isUser ? (
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
            ) : (
              <div className="markdown-content text-sm">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      if (!inline && match) {
                        return <CodeBlock language={match[1]}>{children}</CodeBlock>;
                      }
                      return (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                    pre({ children }) {
                      return <>{children}</>;
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}

            {/* Sources */}
            {!isUser && <SourceCitations sources={message.sources} />}

            {/* Metrics */}
            {!isUser && <MetricsBadge metrics={message.metrics} />}
          </div>

          {/* Actions row */}
          <div className={`flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity ${
            isUser ? 'justify-end' : 'justify-start'
          }`}>
            <span className="text-[10px] text-slate-600">{time}</span>
            {!isUser && message.content && (
              <>
                <CopyButton text={message.content} />
                {isLast && onRegenerate && (
                  <button
                    onClick={onRegenerate}
                    className="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg bg-white/5 text-slate-400 hover:text-amber-400 hover:bg-amber-500/10 border border-white/5 transition"
                    aria-label="Regenerate response"
                  >
                    ↺ Regenerate
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatMessage;
