import React, { useState, useEffect } from 'react';
import { uploadDocument, getDocuments } from '../services/api';

export const DocumentUpload = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    fetchDocuments();
    const interval = setInterval(fetchDocuments, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await getDocuments();
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleUpload(files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleUpload(e.target.files[0]);
    }
  };

  const handleUpload = async (file) => {
    setLoading(true);
    setMessage('');

    try {
      const response = await uploadDocument(file);
      setMessage(`✓ Uploaded: ${response.data.filename} (${response.data.chunks} chunks)`);
      setTimeout(() => setMessage(''), 5000);
      fetchDocuments();
    } catch (error) {
      setMessage(`✗ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tab-content">
      <h2>📄 Document Upload</h2>

      <div
        className={`upload-area ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          onChange={handleFileInput}
          accept=".pdf,.txt,.md"
          disabled={loading}
          style={{ display: 'none' }}
        />
        <label htmlFor="file-input" className="upload-label">
          <p>📤 Drag and drop your files here</p>
          <p>or click to select (PDF, TXT, MD)</p>
        </label>
      </div>

      {message && <div className={`message ${message.includes('✗') ? 'error' : 'success'}`}>{message}</div>}

      <h3>Indexed Documents</h3>
      {documents.length === 0 ? (
        <p className="no-data">No documents indexed yet. Upload your first document!</p>
      ) : (
        <table className="documents-table">
          <thead>
            <tr>
              <th>Document Name</th>
              <th>Chunks</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc, i) => (
              <tr key={i}>
                <td>{doc.source}</td>
                <td>{doc.chunks}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
