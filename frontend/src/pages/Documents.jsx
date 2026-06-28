import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import DocumentCard from '../components/DocumentCard';

function Documents() {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch('http://localhost:8000/documents', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const token = localStorage.getItem('token');
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        await fetchDocuments();
      } else {
        alert(t('documents.uploadFailed'));
      }
    } catch (error) {
      alert(t('documents.connectionError'));
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (documentId) => {
    const token = localStorage.getItem('token');
    
    if (!confirm(t('documents.deleteConfirm'))) return;

    try {
      const response = await fetch(`http://localhost:8000/documents/${documentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        await fetchDocuments();
      } else {
        alert(t('documents.deleteFailed'));
      }
    } catch (error) {
      alert(t('documents.connectionError'));
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col lg:ml-64">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title={t('documents.title')} />
        
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            {/* Upload Section */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-8">
              <h3 className="text-lg font-semibold text-white mb-4">{t('documents.uploadDocument')}</h3>
              <div className="flex gap-4">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="hidden"
                  id="document-upload"
                  accept=".pdf,.txt,.png,.jpg,.jpeg,.gif,.bmp,.tiff,.wav,.mp3"
                />
                <label
                  htmlFor="document-upload"
                  className={`px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition cursor-pointer flex items-center gap-2 ${
                    uploading ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  <span className="text-xl">📄</span>
                  <span>{uploading ? t('documents.uploading') : t('documents.chooseFile')}</span>
                </label>
                <p className="text-gray-400 text-sm self-center">
                  {t('documents.supportedFormats')}
                </p>
              </div>
            </div>

            {/* Documents Grid */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-white">{t('common.loading')}</div>
              </div>
            ) : documents.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {documents.map((doc) => (
                  <DocumentCard key={doc.id} document={doc} onDelete={handleDelete} />
                ))}
              </div>
            ) : (
              <div className="bg-slate-800 rounded-xl p-12 border border-slate-700 text-center">
                <div className="text-6xl mb-4">📄</div>
                <h3 className="text-xl font-semibold text-white mb-2">{t('documents.noDocuments')}</h3>
                <p className="text-gray-400 mb-6">{t('documents.noDocumentsDesc')}</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default Documents;
