import { useEffect, useRef } from 'react';

function ConfirmModal({ isOpen, title, message, confirmLabel = 'Delete', cancelLabel = 'Cancel', onConfirm, onCancel, danger = true }) {
  const cancelRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      cancelRef.current?.focus();
      const handleKey = (e) => { if (e.key === 'Escape') onCancel(); };
      window.addEventListener('keydown', handleKey);
      return () => window.removeEventListener('keydown', handleKey);
    }
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="modal-box">
        <div className="flex items-start gap-4 mb-4">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 text-lg ${
            danger ? 'bg-red-500/15 text-red-400' : 'bg-yellow-500/15 text-yellow-400'
          }`}>
            {danger ? '🗑️' : '⚠️'}
          </div>
          <div>
            <h3 id="modal-title" className="text-white font-semibold text-base mb-1">{title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">{message}</p>
          </div>
        </div>

        <div className="flex gap-3 justify-end mt-6">
          <button
            ref={cancelRef}
            onClick={onCancel}
            className="px-4 py-2 rounded-lg text-sm font-medium text-slate-300 glass-btn"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`px-5 py-2 rounded-lg text-sm font-semibold text-white transition ${
              danger
                ? 'bg-red-600 hover:bg-red-500 shadow-lg shadow-red-900/30'
                : 'bg-yellow-600 hover:bg-yellow-500'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmModal;
