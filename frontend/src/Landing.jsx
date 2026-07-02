import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import BackgroundLayout from './components/BackgroundLayout';
import { backgroundImages } from './constants/backgrounds';

function Landing() {
  const { t } = useTranslation();
  return (
    <div
      className="min-h-screen relative"
      style={{
        backgroundImage: "url('/bg-clock.jpg')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* Dark overlay for readability */}
      <div className="absolute inset-0 bg-black/55 pointer-events-none" />

      {/* Page content — above overlay */}
      <div className="relative z-10">
        {/* Navigation */}
        <nav className="flex items-center justify-between px-8 py-6">
          <div className="text-2xl font-bold text-white">Memento AI</div>
          <div className="flex gap-4">
            <Link to="/login" className="px-4 py-2 text-white hover:text-purple-300 transition">
              {t('auth.login')}
            </Link>
            <Link
              to="/signup"
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              {t('auth.signup')}
            </Link>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="flex flex-col items-center justify-center px-4 py-20 text-center">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            {t('landing.title')}
            <span className="block text-purple-400">{t('landing.subtitle')}</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl">
            {t('landing.description')}
          </p>
          <div className="flex gap-4">
            <Link
              to="/signup"
              className="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-lg hover:bg-purple-700 transition shadow-lg"
            >
              {t('landing.getStarted')}
            </Link>
            <Link
              to="/login"
              className="px-8 py-4 bg-transparent border-2 border-white text-white text-lg font-semibold rounded-lg hover:bg-white hover:text-slate-900 transition"
            >
              {t('landing.signIn')}
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="px-8 py-20">
          <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
              <div className="text-4xl mb-4">🧠</div>
              <h3 className="text-xl font-semibold text-white mb-2">{t('landing.feature1Title')}</h3>
              <p className="text-gray-300">
                {t('landing.feature1Desc')}
              </p>
            </div>
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
              <div className="text-4xl mb-4">🔒</div>
              <h3 className="text-xl font-semibold text-white mb-2">{t('landing.feature2Title')}</h3>
              <p className="text-gray-300">
                {t('landing.feature2Desc')}
              </p>
            </div>
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold text-white mb-2">{t('landing.feature3Title')}</h3>
              <p className="text-gray-300">
                {t('landing.feature3Desc')}
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="px-8 py-8 text-center text-gray-400">
          <p>{t('landing.footer')}</p>
        </footer>
      </div>
    </div>
  );
}

export default Landing;
