import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import BackgroundLayout from '../components/BackgroundLayout';
import { backgroundImages } from '../constants/backgrounds';
import API_BASE from '../config/api';

function Settings() {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [settings, setSettings] = useState({
    theme: 'dark',
    notifications: true,
    autoSave: true,
  });
  const [saving, setSaving] = useState(false);
  const [aiStatus, setAiStatus] = useState(null);

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    setUser(userData);

    // Fetch AI status
    fetch(`${API_BASE}/status`)
      .then(res => res.json())
      .then(data => setAiStatus(data))
      .catch(err => console.error('Failed to fetch AI status:', err));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    // Simulate saving
    setTimeout(() => {
      setSaving(false);
      alert(t('settings.saved'));
    }, 500);
  };

  const handleDeleteData = async () => {
    if (!confirm(t('settings.deleteConfirm1'))) {
      return;
    }

    if (!confirm(t('settings.deleteConfirm2'))) {
      return;
    }

    const token = localStorage.getItem('token');

    try {
      // This would need to be implemented on the backend
      alert('Data deletion feature requires backend implementation');
    } catch (error) {
      alert('Failed to delete data');
    }
  };

  return (
    <BackgroundLayout image={backgroundImages.settings}>
      <div className="min-h-screen flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <div className="flex-1 flex flex-col lg:ml-64">
          <Navbar onMenuClick={() => setSidebarOpen(true)} title={t('settings.title')} />

          <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Profile Section */}
            <div className="glass-card-dark p-6 animate-fade-in">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">👤</span>
                {t('settings.profile')}
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.name')}</label>
                  <input
                    type="text"
                    value={user?.name || ''}
                    disabled
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600/50 rounded-lg text-gray-400 cursor-not-allowed backdrop-blur-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{t('settings.email')}</label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600/50 rounded-lg text-gray-400 cursor-not-allowed backdrop-blur-sm"
                  />
                </div>
                <p className="text-xs text-gray-500">{t('settings.profileInfo')}</p>
              </div>
            </div>

            {/* Appearance */}
            <div className="glass-card-dark p-6 animate-fade-in">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">🎨</span>
                {t('settings.appearance')}
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-slate-700/50">
                  <div>
                    <span className="text-white">{t('settings.theme')}</span>
                    <p className="text-sm text-gray-400">{t('settings.themeDesc')}</p>
                  </div>
                  <select
                    value={settings.theme}
                    onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                    className="px-4 py-2 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 backdrop-blur-sm"
                  >
                    <option value="dark">{t('settings.dark')}</option>
                    <option value="light">{t('settings.light')}</option>
                    <option value="system">{t('settings.system')}</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Notifications */}
            <div className="glass-card-dark p-6 animate-fade-in">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">🔔</span>
                {t('settings.notifications')}
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-slate-700/50">
                  <div>
                    <span className="text-white">{t('settings.enableNotifications')}</span>
                    <p className="text-sm text-gray-400">{t('settings.notificationsDesc')}</p>
                  </div>
                  <button
                    onClick={() => setSettings({ ...settings, notifications: !settings.notifications })}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      settings.notifications ? 'bg-purple-600' : 'bg-slate-600'
                    }`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full transform transition-transform ${
                      settings.notifications ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </button>
                </div>
              </div>
            </div>

            {/* Data Management */}
            <div className="glass-card-dark p-6 animate-fade-in">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">💾</span>
                {t('settings.dataManagement')}
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-slate-700/50">
                  <div>
                    <span className="text-white">{t('settings.autoSave')}</span>
                    <p className="text-sm text-gray-400">{t('settings.autoSaveDesc')}</p>
                  </div>
                  <button
                    onClick={() => setSettings({ ...settings, autoSave: !settings.autoSave })}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      settings.autoSave ? 'bg-purple-600' : 'bg-slate-600'
                    }`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full transform transition-transform ${
                      settings.autoSave ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </button>
                </div>
                <div className="pt-4">
                  <button
                    onClick={handleDeleteData}
                    className="premium-card px-4 py-2 bg-red-600/20 border border-red-500/30 text-red-400 rounded-lg hover:bg-red-600/30 transition btn-premium"
                  >
                    {t('settings.deleteAllData')}
                  </button>
                  <p className="text-xs text-gray-500 mt-2">
                    {t('settings.deleteWarning')}
                  </p>
                </div>
              </div>
            </div>

            {/* AI Status */}
            <div className="glass-card-dark p-6 animate-fade-in">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">🤖</span>
                AI Status
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-slate-700/50">
                  <span className="text-gray-400">AI Runtime</span>
                  <span className="text-white font-medium">{aiStatus?.runtime || 'Loading...'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700/50">
                  <span className="text-gray-400">Device</span>
                  <span className="text-white font-medium">{aiStatus?.device || 'Loading...'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700/50">
                  <span className="text-gray-400">Internet</span>
                  <span className={`font-medium ${aiStatus?.offline ? 'text-green-400' : 'text-red-400'}`}>
                    {aiStatus?.offline ? 'Offline' : 'Online'}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700/50">
                  <span className="text-gray-400">Model</span>
                  <span className="text-white font-medium">{aiStatus?.model || 'Loading...'}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-gray-400">External API Calls</span>
                  <span className="text-green-400 font-medium">{aiStatus?.external_api_calls ?? 0}</span>
                </div>
              </div>
            </div>

            {/* About */}
            <div className="glass-card-dark p-6 animate-fade-in">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">ℹ️</span>
                {t('settings.about')}
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-slate-700/50">
                  <span className="text-gray-400">{t('settings.version')}</span>
                  <span className="text-white">1.0.0</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700/50">
                  <span className="text-gray-400">{t('settings.aiModel')}</span>
                  <span className="text-white">Local LLM</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-gray-400">{t('settings.license')}</span>
                  <span className="text-white">AGPL-3.0</span>
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end">
              <button
                onClick={handleSave}
                disabled={saving}
                className="premium-card px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed btn-premium animate-glow"
              >
                {saving ? t('settings.saving') : t('settings.saveSettings')}
              </button>
            </div>
          </div>
        </main>
        </div>
      </div>
    </BackgroundLayout>
  );
}

export default Settings;
