import { useState, useCallback } from 'react';

/**
 * Renders markdown text with syntax highlighting.
 * Supports: headings, bold, italic, inline code, code blocks,
 * ordered/unordered lists, blockquotes, links, hr, tables.
 * Does NOT require any additional npm packages.
 */
function MarkdownMessage({ content = '', isStreaming = false }) {
  if (!content) return null;

  const tokens = parseMarkdown(content, isStreaming);
  return (
    <div className="markdown-content">
      {renderTokens(tokens)}
    </div>
  );
}

// ─── Copy Button for Code Blocks ───
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [text]);

  return (
    <button
      className="code-copy-btn"
      onClick={handleCopy}
      title="Copy code"
      aria-label={copied ? 'Copied!' : 'Copy code'}
    >
      {copied ? '✓ Copied' : 'Copy'}
    </button>
  );
}

// ─── Token Types ───
const TOKEN = {
  HEADING: 'heading',
  CODE_BLOCK: 'code_block',
  BLOCKQUOTE: 'blockquote',
  HR: 'hr',
  UL: 'ul',
  OL: 'ol',
  TABLE: 'table',
  PARAGRAPH: 'paragraph',
};

// ─── Block-level Parser ───
function parseMarkdown(text, isStreaming) {
  if (isStreaming) {
    // During streaming don't try to render incomplete code blocks
    text = text.replace(/```[^`]*$/, '');
  }

  const lines = text.split('\n');
  const tokens = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Heading
    const headingMatch = line.match(/^(#{1,3})\s+(.+)/);
    if (headingMatch) {
      tokens.push({ type: TOKEN.HEADING, level: headingMatch[1].length, text: headingMatch[2] });
      i++;
      continue;
    }

    // HR
    if (/^---+$|^\*\*\*+$/.test(line.trim())) {
      tokens.push({ type: TOKEN.HR });
      i++;
      continue;
    }

    // Fenced code block
    if (/^```/.test(line)) {
      const lang = line.slice(3).trim();
      const codeLines = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i])) {
        codeLines.push(lines[i]);
        i++;
      }
      tokens.push({ type: TOKEN.CODE_BLOCK, lang, code: codeLines.join('\n') });
      i++; // skip closing ```
      continue;
    }

    // Blockquote
    if (/^>\s/.test(line)) {
      const bqLines = [];
      while (i < lines.length && /^>\s/.test(lines[i])) {
        bqLines.push(lines[i].slice(2));
        i++;
      }
      tokens.push({ type: TOKEN.BLOCKQUOTE, text: bqLines.join('\n') });
      continue;
    }

    // Unordered list
    if (/^[-*+]\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^[-*+]\s/.test(lines[i])) {
        items.push(lines[i].replace(/^[-*+]\s/, ''));
        i++;
      }
      tokens.push({ type: TOKEN.UL, items });
      continue;
    }

    // Ordered list
    if (/^\d+\.\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\.\s/, ''));
        i++;
      }
      tokens.push({ type: TOKEN.OL, items });
      continue;
    }

    // Table
    if (/\|/.test(line) && i + 1 < lines.length && /^[\s|:-]+$/.test(lines[i + 1])) {
      const headers = line.split('|').map(c => c.trim()).filter(Boolean);
      i += 2; // skip header + separator
      const rows = [];
      while (i < lines.length && /\|/.test(lines[i])) {
        rows.push(lines[i].split('|').map(c => c.trim()).filter(Boolean));
        i++;
      }
      tokens.push({ type: TOKEN.TABLE, headers, rows });
      continue;
    }

    // Empty line
    if (line.trim() === '') {
      i++;
      continue;
    }

    // Paragraph — collect consecutive non-blank, non-special lines
    const paraLines = [];
    while (
      i < lines.length &&
      lines[i].trim() !== '' &&
      !/^(#{1,3}\s|```|>\s|[-*+]\s|\d+\.\s|---+|\*\*\*+)/.test(lines[i])
    ) {
      paraLines.push(lines[i]);
      i++;
    }
    if (paraLines.length > 0) {
      tokens.push({ type: TOKEN.PARAGRAPH, text: paraLines.join('\n') });
    }
  }

  return tokens;
}

// ─── Render Block Tokens ───
function renderTokens(tokens) {
  return tokens.map((token, idx) => {
    switch (token.type) {
      case TOKEN.HEADING:
        const Tag = `h${token.level}`;
        return <Tag key={idx}>{renderInline(token.text)}</Tag>;

      case TOKEN.CODE_BLOCK:
        return (
          <pre key={idx} style={{ position: 'relative' }}>
            {token.lang && (
              <span style={{
                position: 'absolute', top: 8, left: 12,
                fontSize: '10px', color: '#6366f1',
                fontFamily: 'var(--font-mono)',
                textTransform: 'uppercase', letterSpacing: '0.05em',
              }}>
                {token.lang}
              </span>
            )}
            <code style={{ display: 'block', paddingTop: token.lang ? '20px' : '0' }}>
              {token.code}
            </code>
            <CopyButton text={token.code} />
          </pre>
        );

      case TOKEN.BLOCKQUOTE:
        return <blockquote key={idx}>{renderInline(token.text)}</blockquote>;

      case TOKEN.HR:
        return <hr key={idx} />;

      case TOKEN.UL:
        return (
          <ul key={idx}>
            {token.items.map((item, j) => <li key={j}>{renderInline(item)}</li>)}
          </ul>
        );

      case TOKEN.OL:
        return (
          <ol key={idx}>
            {token.items.map((item, j) => <li key={j}>{renderInline(item)}</li>)}
          </ol>
        );

      case TOKEN.TABLE:
        return (
          <table key={idx}>
            <thead>
              <tr>{token.headers.map((h, j) => <th key={j}>{renderInline(h)}</th>)}</tr>
            </thead>
            <tbody>
              {token.rows.map((row, j) => (
                <tr key={j}>{row.map((cell, k) => <td key={k}>{renderInline(cell)}</td>)}</tr>
              ))}
            </tbody>
          </table>
        );

      case TOKEN.PARAGRAPH:
        // Handle multi-line paragraphs — render each line and add <br> between
        const lines = token.text.split('\n');
        return (
          <p key={idx}>
            {lines.map((line, j) => (
              <span key={j}>
                {renderInline(line)}
                {j < lines.length - 1 && <br />}
              </span>
            ))}
          </p>
        );

      default:
        return null;
    }
  });
}

// ─── Inline Renderer ───
function renderInline(text) {
  // Split text by inline patterns and render each part
  const parts = [];
  let remaining = text;
  let key = 0;

  const patterns = [
    // Code span
    { re: /`([^`]+)`/g, render: (m, [code]) => <code key={key++}>{code}</code> },
    // Bold
    { re: /\*\*([^*]+)\*\*/g, render: (m, [t]) => <strong key={key++}>{t}</strong> },
    { re: /__([^_]+)__/g, render: (m, [t]) => <strong key={key++}>{t}</strong> },
    // Italic
    { re: /\*([^*]+)\*/g, render: (m, [t]) => <em key={key++}>{t}</em> },
    { re: /_([^_]+)_/g, render: (m, [t]) => <em key={key++}>{t}</em> },
    // Link
    { re: /\[([^\]]+)\]\(([^)]+)\)/g, render: (m, [label, href]) => (
      <a key={key++} href={href} target="_blank" rel="noopener noreferrer">{label}</a>
    )},
  ];

  // Build a merged pattern list to process in order
  const allMatches = [];
  for (const { re, render } of patterns) {
    let m;
    const regex = new RegExp(re.source, 'g');
    while ((m = regex.exec(text)) !== null) {
      allMatches.push({ index: m.index, end: m.index + m[0].length, match: m, render });
    }
  }

  allMatches.sort((a, b) => a.index - b.index);

  let cursor = 0;
  const result = [];

  for (const { index, end, match, render } of allMatches) {
    if (index < cursor) continue; // overlapping — skip
    if (index > cursor) {
      result.push(<span key={key++}>{text.slice(cursor, index)}</span>);
    }
    result.push(render(match[0], match.slice(1)));
    cursor = end;
  }

  if (cursor < text.length) {
    result.push(<span key={key++}>{text.slice(cursor)}</span>);
  }

  return result.length === 0 ? text : result;
}

export default MarkdownMessage;
