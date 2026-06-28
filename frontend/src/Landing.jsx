import { Link } from 'react-router-dom';

function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-8 py-6">
        <div className="text-2xl font-bold text-white">Memento AI</div>
        <div className="flex gap-4">
          <Link to="/login" className="px-4 py-2 text-white hover:text-purple-300 transition">
            Login
          </Link>
          <Link 
            to="/signup" 
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            Sign Up
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center px-4 py-20 text-center">
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
          Your Personal AI
          <span className="block text-purple-400">Memory Assistant</span>
        </h1>
        <p className="text-xl text-gray-300 mb-8 max-w-2xl">
          Store, organize, and retrieve your memories with the power of AI. 
          Completely offline, completely private, completely yours.
        </p>
        <div className="flex gap-4">
          <Link 
            to="/signup" 
            className="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-lg hover:bg-purple-700 transition shadow-lg"
          >
            Get Started Free
          </Link>
          <Link 
            to="/login" 
            className="px-8 py-4 bg-transparent border-2 border-white text-white text-lg font-semibold rounded-lg hover:bg-white hover:text-slate-900 transition"
          >
            Sign In
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="px-8 py-20">
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
            <div className="text-4xl mb-4">🧠</div>
            <h3 className="text-xl font-semibold text-white mb-2">AI-Powered Memory</h3>
            <p className="text-gray-300">
              Extract and organize memories from documents, audio, and conversations using local AI.
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
            <div className="text-4xl mb-4">🔒</div>
            <h3 className="text-xl font-semibold text-white mb-2">100% Offline</h3>
            <p className="text-gray-300">
              All processing happens locally on your machine. Your data never leaves your computer.
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-white mb-2">Smart Retrieval</h3>
            <p className="text-gray-300">
              Find memories instantly with semantic search and intelligent context understanding.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="px-8 py-8 text-center text-gray-400">
        <p>&copy; 2024 Memento AI. Your memories, your control.</p>
      </footer>
    </div>
  );
}

export default Landing;
