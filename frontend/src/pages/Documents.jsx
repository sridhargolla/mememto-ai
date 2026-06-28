import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import DocumentCard from '../components/DocumentCard';
import UploadZone from '../components/UploadZone';

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
      const response = await fetch('/api/documents', {
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

      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Success! Extracted ${data.memories_created || 0} memories from ${file.name}`);
        await fetchDocuments();
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error.message}. Please check the file format and try again.`);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (documentId) => {
    const token = localStorage.getItem('token');
    
    if (!confirm(t('documents.deleteConfirm'))) return;

    try {
      const response = await fetch(`/api/documents/${documentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        await fetchDocuments();
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`Delete failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Connection error. Please check your network.');
    }
  };

  return (
    <div className="min-h-screen flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex-1 flex flex-col lg:ml-64">
        <Navbar onMenuClick={() => setSidebarOpen(true)} title={t('documents.title')} />
        
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            {/* Upload Section */}
            <div className="animate-fade-in">
              <h3 className="text-lg font-semibold text-white mb-4">{t('documents.uploadDocument')}</h3>
              <UploadZone 
                onUpload={(data) => {
                  alert(`Success! Extracted ${data.memories_created || 0} memories.`);
                  fetchDocuments();
                }}
                uploading={uploading}
              />
            </div>

            {/* Documents Grid */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-white animate-pulse">{t('common.loading')}</div>
              </div>
            ) : documents.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {documents.map((doc) => (
                  <DocumentCard key={doc.id} document={doc} onDelete={handleDelete} />
                ))}
              </div>
            ) : (
              <div className="glass-card-dark p-12 text-center animate-fade-in">
                <div className="text-6xl mb-4 animate-float">📄</div>
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
