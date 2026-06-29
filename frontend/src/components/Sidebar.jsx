import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard, MessageSquare, FileText, Brain,
  Clock, ShieldCheck, Settings, Activity, Cpu,
  X, Menu, LogOut, ChevronRight
} from 'lucide-react';

function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const initials = user.name ? user.name.slice(0, 2).toUpperCase() : 'U';

  const menuItems = [
    { path: '/dashboard',              icon: LayoutDashboard, label: t('navigation.dashboard'),  color: 'text-purple-400' },
    { path: '/dashboard/chat',         icon: MessageSquare,   label: t('navigation.chat'),        color: 'text-cyan-400' },
    { path: '/dashboard/documents',    icon: FileText,        label: t('navigation.documents'),   color: 'text-blue-400' },
    { path: '/dashboard/memories',     icon: Brain,           label: t('navigation.memories'),    color: 'text-violet-400' },
    { path: '/dashboard/timeline',     icon: Clock,           label: t('navigation.timeline'),    color: 'text-indigo-400' },
    { path: '/dashboard/status',       icon: Activity,        label: 'System Status',             color: 'text-emerald-400' },
    { path: '/dashboard/performance',  icon: Cpu,             label: 'Performance',               color: 'text-amber-400' },
    { path: '/dashboard/privacy',      icon: ShieldCheck,     label: t('navigation.privacy'),     color: 'text-rose-400' },
    { path: '/dashboard/settings',     icon: Settings,        label: t('navigation.settings'),    color: 'text-slate-400' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 lg:hidden backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-50 h-full w-64 glass-sidebar transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:static lg:z-0`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-5 border-b border-white/5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500 to-violet-700 flex items-center justify-center shadow-lg shadow-purple-900/40">
                  <Brain size={18} className="text-white" />
                </div>
                <div>
                  <h1 className="text-base font-bold text-white leading-none">Memento AI</h1>
                  <p className="text-[10px] text-purple-400/70 mt-0.5 font-medium">Personal Memory System</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="lg:hidden w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/10 transition"
                aria-label="Close sidebar"
              >
                <X size={16} />
              </button>
            </div>

            {/* CPU mode badge */}
            <div className="mt-3 flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 w-fit">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-slow" />
              <span className="text-[11px] text-emerald-400 font-semibold tracking-wide">LOCAL CPU MODE</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto" role="navigation" aria-label="Main navigation">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => onClose()}
                  aria-current={isActive ? 'page' : undefined}
                  className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 relative ${
                    isActive
                      ? 'bg-gradient-to-r from-purple-600/30 to-violet-600/20 border border-purple-500/30 text-white shadow-lg shadow-purple-900/20'
                      : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                  }`}
                >
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-purple-400 rounded-r-full" />
                  )}
                  <Icon
                    size={17}
                    className={`flex-shrink-0 transition-colors ${isActive ? item.color : 'group-hover:' + item.color}`}
                  />
                  <span className="text-sm font-medium">{item.label}</span>
                  {isActive && <ChevronRight size={13} className="ml-auto text-purple-400/60" />}
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="p-3 border-t border-white/5">
            <div className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/5 transition group cursor-default">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                {initials}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{user.name || 'User'}</p>
                <p className="text-xs text-slate-500 truncate">{user.email || 'Offline'}</p>
              </div>
              <button
                onClick={handleLogout}
                className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition"
                title="Logout"
                aria-label="Logout"
              >
                <LogOut size={15} />
              </button>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
