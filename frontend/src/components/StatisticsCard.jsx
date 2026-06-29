function StatisticsCard({ icon, title, value, subtitle, trend, color = 'purple' }) {
  const colorClasses = {
    purple: 'bg-purple-500/10 border-purple-500/30 text-purple-400',
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
    green: 'bg-green-500/10 border-green-500/30 text-green-400',
    orange: 'bg-orange-500/10 border-orange-500/30 text-orange-400',
    red: 'bg-red-500/10 border-red-500/30 text-red-400',
  };

  const iconBgClasses = {
    purple: 'bg-purple-600',
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    orange: 'bg-orange-600',
    red: 'bg-red-600',
  };

  return (
    <div className="glass-card-dark rounded-xl p-6 border border-slate-700/50 hover:border-purple-500/50 transition-all duration-200 hover:shadow-lg hover:shadow-purple-500/10 premium-card">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 ${iconBgClasses[color]} rounded-xl flex items-center justify-center text-2xl`}>
          {icon}
        </div>
        {trend && (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            trend > 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            {trend > 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>

      <div className="mb-2">
        <p className="text-3xl font-bold text-white">{value}</p>
        <p className="text-sm text-gray-400">{title}</p>
      </div>

      {subtitle && (
        <p className={`text-xs px-2 py-1 rounded-full inline-block ${colorClasses[color]}`}>
          {subtitle}
        </p>
      )}
    </div>
  );
}

export default StatisticsCard;
