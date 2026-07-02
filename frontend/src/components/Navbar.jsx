import { Menu, Wifi, WifiOff, Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';

function Navbar({ onMenuClick, title, subtitle }) {
  const { i18n } = useTranslation();
  const currentLang = i18n.language || 'en';

  const handleLanguageChange = async (e) => {
    const newLang = e.target.value;
    await i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);

    // Persist language to backend database if logged in
    const token = localStorage.getItem('token');
    if (token) {
      try {
        await fetch('/api/user/language', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ preferred_language: newLang })
        });
      } catch (err) {
        console.error("Failed to sync language to backend:", err);
      }
    }
  };

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

      {/* Language Selector Dropdown */}
      <div className="flex items-center gap-2">
        <div className="relative flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 flex-shrink-0">
          <Globe size={11} />
          <select
            value={currentLang}
            onChange={handleLanguageChange}
            className="bg-transparent text-[10px] font-semibold text-purple-400 focus:outline-none cursor-pointer pr-1 border-none"
            title="Switch Language"
          >
            <option value="en" className="bg-slate-900 text-slate-200">EN</option>
            <option value="hi" className="bg-slate-900 text-slate-200">हिंदी</option>
            <option value="te" className="bg-slate-900 text-slate-200">తెలుగు</option>
          </select>
        </div>

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
