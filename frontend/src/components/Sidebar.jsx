import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  const { t } = useTranslation();

  const menuItems = [
    { path: '/dashboard', icon: '📊', label: t('navigation.dashboard') },
    { path: '/dashboard/chat', icon: '💬', label: t('navigation.chat') },
    { path: '/dashboard/documents', icon: '📄', label: t('navigation.documents') },
    { path: '/dashboard/memories', icon: '🧠', label: t('navigation.memories') },
    { path: '/dashboard/timeline', icon: '📅', label: t('navigation.timeline') },
    { path: '/dashboard/privacy', icon: '🔒', label: t('navigation.privacy') },
    { path: '/dashboard/settings', icon: '⚙️', label: t('navigation.settings') },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-50 h-full w-64 bg-slate-800 border-r border-slate-700 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:static lg:z-0`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b border-slate-700">
            <h1 className="text-xl font-bold text-white">Memento AI</h1>
            <button
              onClick={onClose}
              className="lg:hidden text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => onClose()}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-purple-600 text-white shadow-lg'
                      : 'text-gray-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-slate-700">
            <div className="flex items-center gap-3 px-4 py-3">
              <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                {JSON.parse(localStorage.getItem('user') || '{}')?.name?.[0] || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {JSON.parse(localStorage.getItem('user') || '{}')?.name || 'User'}
                </p>
                <p className="text-xs text-gray-400 truncate">
                  {JSON.parse(localStorage.getItem('user') || '{}')?.email || ''}
                </p>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
