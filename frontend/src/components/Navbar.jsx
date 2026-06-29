import { Menu, Wifi, WifiOff, Bell } from 'lucide-react';

function Navbar({ onMenuClick, title, subtitle }) {
  return (
    <header className="glass-navbar px-5 py-3 flex items-center gap-4 sticky top-0 z-30">
      {/* Mobile menu toggle */}
      <button
        onClick={onMenuClick}
        className="lg:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition"
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>

      {/* Title */}
      <div className="flex-1 min-w-0">
        <h2 className="text-base font-semibold text-white truncate">{title}</h2>
        {subtitle && <p className="text-xs text-slate-500 truncate">{subtitle}</p>}
      </div>

      {/* Status indicators */}
      <div className="flex items-center gap-2">
        {/* Offline badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/20">
          <WifiOff size={12} className="text-red-400" />
          <span className="text-[11px] text-red-400 font-semibold">OFFLINE</span>
        </div>

        {/* CPU badge */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[11px] text-emerald-400 font-semibold">CPU</span>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
