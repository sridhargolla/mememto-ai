function SkeletonCard({ lines = 3, className = '' }) {
  return (
    <div className={`glass-card p-5 ${className}`} aria-hidden="true">
      <div className="flex items-center gap-3 mb-4">
        <div className="skeleton w-10 h-10 rounded-full" />
        <div className="flex-1 space-y-2">
          <div className="skeleton h-4 w-3/4 rounded" />
          <div className="skeleton h-3 w-1/3 rounded" />
        </div>
      </div>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton h-3 rounded mb-2"
          style={{ width: `${85 - i * 15}%` }}
        />
      ))}
      <div className="flex gap-2 mt-4">
        <div className="skeleton h-6 w-16 rounded-full" />
        <div className="skeleton h-6 w-20 rounded-full" />
      </div>
    </div>
  );
}

export function SkeletonGrid({ count = 6, cols = 3 }) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-${cols} gap-6`}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

export function SkeletonLine({ width = '100%', height = '14px', className = '' }) {
  return (
    <div
      className={`skeleton rounded ${className}`}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}

export default SkeletonCard;
