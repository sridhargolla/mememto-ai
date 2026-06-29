/**
 * Sparkline — tiny inline SVG line chart.
 * No external dependencies.
 *
 * Props:
 *   data: number[]   — array of values
 *   width: number    — chart width (px)
 *   height: number   — chart height (px)
 *   color: string    — stroke color (CSS)
 *   fill: boolean    — fill area under line
 *   label: string    — accessible label
 */
function Sparkline({
  data = [],
  width = 120,
  height = 36,
  color = '#7c3aed',
  fill = true,
  label = 'Sparkline chart',
}) {
  if (!data || data.length < 2) {
    return (
      <svg width={width} height={height} aria-label={label}>
        <line
          x1={0} y1={height / 2}
          x2={width} y2={height / 2}
          stroke={color} strokeOpacity="0.3"
          strokeWidth="1.5" strokeDasharray="4 4"
        />
      </svg>
    );
  }

  const pad = 2;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data.map((v, i) => {
    const x = pad + (i / (data.length - 1)) * (width - pad * 2);
    const y = pad + (1 - (v - min) / range) * (height - pad * 2);
    return [x, y];
  });

  const pathD = points
    .map(([x, y], i) => `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`)
    .join(' ');

  const fillD = `${pathD} L ${points[points.length - 1][0].toFixed(1)} ${height} L ${points[0][0].toFixed(1)} ${height} Z`;

  const gradId = `spark-grad-${Math.random().toString(36).slice(2)}`;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      aria-label={label}
      role="img"
      style={{ overflow: 'visible' }}
    >
      {fill && (
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
      )}

      {fill && (
        <path d={fillD} fill={`url(#${gradId})`} />
      )}

      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Latest value dot */}
      <circle
        cx={points[points.length - 1][0]}
        cy={points[points.length - 1][1]}
        r="3"
        fill={color}
        opacity="0.9"
      />
    </svg>
  );
}

export default Sparkline;
