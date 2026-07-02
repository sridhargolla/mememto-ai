import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import BackgroundLayout from '../components/BackgroundLayout';
import { backgroundImages } from '../constants/backgrounds';

function Privacy() {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <BackgroundLayout image={backgroundImages.privacy}>
      <div className="min-h-screen flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <div className="flex-1 flex flex-col lg:ml-64">
          <Navbar onMenuClick={() => setSidebarOpen(true)} title={t('privacy.title')} />

          <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="bg-slate-800 rounded-xl p-8 border border-slate-700">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-green-600/20 rounded-xl flex items-center justify-center">
                  <span className="text-4xl">🔒</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">{t('privacy.subtitle')}</h2>
                  <p className="text-gray-400">{t('privacy.description')}</p>
                </div>
              </div>
            </div>

            {/* AI Model Info */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">🤖</span>
                {t('privacy.aiModel')}
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">{t('privacy.modelType')}</span>
                  <span className="text-white font-medium">{t('privacy.localLLM')}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">{t('privacy.inference')}</span>
                  <span className="text-green-400 font-medium">{t('privacy.localCPU')}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">{t('privacy.cloudAPI')}</span>
                  <span className="text-red-400 font-medium">{t('privacy.notUsed')}</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="text-gray-400">{t('privacy.dataCollection')}</span>
                  <span className="text-green-400 font-medium">{t('privacy.none')}</span>
                </div>
              </div>
            </div>

            {/* Data Storage */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">💾</span>
                {t('privacy.dataStorage')}
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">{t('privacy.database')}</span>
                  <span className="text-white font-medium">{t('privacy.localSQLite')}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">{t('privacy.location')}</span>
                  <span className="text-white font-medium">{t('privacy.yourDevice')}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">{t('privacy.encryption')}</span>
                  <span className="text-green-400 font-medium">{t('privacy.passwordHashed')}</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="text-gray-400">{t('privacy.externalStorage')}</span>
                  <span className="text-red-400 font-medium">{t('privacy.none')}</span>
                </div>
              </div>
            </div>

            {/* Network Status */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">📡</span>
                {t('privacy.networkStatus')}
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">{t('privacy.internetRequired')}</span>
                  <span className="text-red-400 font-medium">{t('privacy.no')}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">{t('privacy.outboundConnections')}</span>
                  <span className="text-green-400 font-medium">{t('privacy.none')}</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="text-gray-400">{t('privacy.offlineMode')}</span>
                  <span className="text-green-400 font-medium">{t('privacy.alwaysOn')}</span>
                </div>
              </div>
            </div>

            {/* Privacy Features */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">✅</span>
                {t('privacy.privacyFeatures')}
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">{t('privacy.feature1Title')}</span>
                    <p className="text-gray-400 text-sm">{t('privacy.feature1Desc')}</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">{t('privacy.feature2Title')}</span>
                    <p className="text-gray-400 text-sm">{t('privacy.feature2Desc')}</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">{t('privacy.feature3Title')}</span>
                    <p className="text-gray-400 text-sm">{t('privacy.feature3Desc')}</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">{t('privacy.feature4Title')}</span>
                    <p className="text-gray-400 text-sm">{t('privacy.feature4Desc')}</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">{t('privacy.feature5Title')}</span>
                    <p className="text-gray-400 text-sm">{t('privacy.feature5Desc')}</p>
                  </div>
                </li>
              </ul>
            </div>

            {/* Security Note */}
            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6">
              <div className="flex items-start gap-3">
                <span className="text-2xl">🛡️</span>
                <div>
                  <h4 className="text-green-400 font-semibold mb-2">{t('privacy.securityNote')}</h4>
                  <p className="text-gray-300 text-sm">
                    {t('privacy.securityDesc')}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </main>
        </div>
      </div>
    </BackgroundLayout>
  );
}

export default Privacy;
