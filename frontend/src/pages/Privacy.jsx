import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';

function Privacy() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-900 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col lg:ml-64">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title="Privacy" />
        
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="bg-slate-800 rounded-xl p-8 border border-slate-700">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-green-600/20 rounded-xl flex items-center justify-center">
                  <span className="text-4xl">🔒</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">100% Private & Offline</h2>
                  <p className="text-gray-400">Your data never leaves your device</p>
                </div>
              </div>
            </div>

            {/* AI Model Info */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">🤖</span>
                AI Model
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">Model Type</span>
                  <span className="text-white font-medium">Local LLM (llama.cpp)</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">Inference</span>
                  <span className="text-green-400 font-medium">Local CPU</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">Cloud API</span>
                  <span className="text-red-400 font-medium">Not Used</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="text-gray-400">Data Collection</span>
                  <span className="text-green-400 font-medium">None</span>
                </div>
              </div>
            </div>

            {/* Data Storage */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">💾</span>
                Data Storage
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">Database</span>
                  <span className="text-white font-medium">Local SQLite</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">Location</span>
                  <span className="text-white font-medium">Your Device</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">Encryption</span>
                  <span className="text-green-400 font-medium">Password Hashed (bcrypt)</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="text-gray-400">External Storage</span>
                  <span className="text-red-400 font-medium">None</span>
                </div>
              </div>
            </div>

            {/* Network Status */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">📡</span>
                Network Status
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">Internet Required</span>
                  <span className="text-red-400 font-medium">No</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-slate-700">
                  <span className="text-gray-400">Outbound Connections</span>
                  <span className="text-green-400 font-medium">None</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="text-gray-400">Offline Mode</span>
                  <span className="text-green-400 font-medium">Always On</span>
                </div>
              </div>
            </div>

            {/* Privacy Features */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">✅</span>
                Privacy Features
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">No account registration required</span>
                    <p className="text-gray-400 text-sm">All data stored locally on your device</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">No telemetry or analytics</span>
                    <p className="text-gray-400 text-sm">We don't track usage or collect metrics</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">No cloud synchronization</span>
                    <p className="text-gray-400 text-sm">Your memories stay on your device</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">Open source transparency</span>
                    <p className="text-gray-400 text-sm">Code is available for audit</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 py-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <div>
                    <span className="text-white">User-controlled data</span>
                    <p className="text-gray-400 text-sm">You can export or delete all data anytime</p>
                  </div>
                </li>
              </ul>
            </div>

            {/* Security Note */}
            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6">
              <div className="flex items-start gap-3">
                <span className="text-2xl">🛡️</span>
                <div>
                  <h4 className="text-green-400 font-semibold mb-2">Security Note</h4>
                  <p className="text-gray-300 text-sm">
                    Memento AI is designed for privacy. All AI inference happens locally on your CPU. 
                    Your documents, memories, and conversations are stored in a local SQLite database. 
                    No data is sent to any external server. Your password is hashed using bcrypt before storage.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Privacy;
