import { useState, useRef } from 'react';

function UploadZone({ onUpload, uploading }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStage, setUploadStage] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file) => {
    const token = localStorage.getItem('token');
    setUploadProgress(0);
    setUploadStage('Uploading...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Simulate progress stages
      setUploadProgress(20);
      setUploadStage('Uploading file...');

      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      setUploadProgress(50);
      setUploadStage('Extracting text...');

      if (response.ok) {
        setUploadProgress(70);
        setUploadStage('Running AI extraction...');

        const data = await response.json();

        setUploadProgress(90);
        setUploadStage('Creating memories...');

        setTimeout(() => {
          setUploadProgress(100);
          setUploadStage('Completed!');
          onUpload(data);
          setTimeout(() => {
            setUploadProgress(0);
            setUploadStage('');
          }, 2000);
        }, 500);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStage(`Error: ${error.message}`);
      setTimeout(() => {
        setUploadProgress(0);
        setUploadStage('');
      }, 3000);
    }
  };

  return (
    <div className="w-full">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        disabled={uploading}
        className="hidden"
        accept=".pdf,.txt,.png,.jpg,.jpeg,.gif,.bmp,.tiff,.wav,.mp3"
      />

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
        className={`glass-card-dark p-8 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 ${
          isDragging
            ? 'border-purple-500 bg-purple-500/10 scale-105'
            : 'border-slate-600 hover:border-purple-500/50 hover:bg-slate-800/50'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {uploadProgress > 0 ? (
          <div className="text-center">
            <div className="mb-4">
              <div className="text-4xl animate-spin">⏳</div>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2 mb-4">
              <div
                className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="text-white font-medium">{uploadStage}</p>
            <p className="text-gray-400 text-sm mt-1">{uploadProgress}%</p>
          </div>
        ) : (
          <div className="text-center">
            <div className={`text-6xl mb-4 ${isDragging ? 'animate-bounce' : 'animate-float'}`}>
              📤
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {isDragging ? 'Drop your file here' : 'Drag & drop your file here'}
            </h3>
            <p className="text-gray-400 mb-4">or click to browse</p>
            <div className="flex flex-wrap gap-2 justify-center text-sm text-gray-500">
              <span className="px-2 py-1 bg-slate-700/50 rounded">PDF</span>
              <span className="px-2 py-1 bg-slate-700/50 rounded">TXT</span>
              <span className="px-2 py-1 bg-slate-700/50 rounded">PNG</span>
              <span className="px-2 py-1 bg-slate-700/50 rounded">JPG</span>
              <span className="px-2 py-1 bg-slate-700/50 rounded">WAV</span>
              <span className="px-2 py-1 bg-slate-700/50 rounded">MP3</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadZone;
