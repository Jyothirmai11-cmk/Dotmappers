import React, { useState, useEffect } from 'react';
import { DocumentUpload } from './components/DocumentUpload';
import { QAInterface } from './components/QAInterface';
import { EvaluationLog } from './components/EvaluationLog';
import { healthCheck } from './services/api';
import './styles/App.css';

function App() {
  const [activeTab, setActiveTab] = useState('qa');
  const [backendConnected, setBackendConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);

  useEffect(() => {
    checkBackendConnection();
    const interval = setInterval(checkBackendConnection, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendConnection = async () => {
    try {
      await healthCheck();
      setBackendConnected(true);
      setConnectionError(null);
    } catch (error) {
      setBackendConnected(false);
      setConnectionError('Backend API is not running. Start it with: python backend/main.py');
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <h1>🔬 Evidence-Grounded AI Research Assistant</h1>
          <p>Retrieval-Augmented Generation with Security & Evaluation</p>
        </div>
        <div className={`status ${backendConnected ? 'connected' : 'disconnected'}`}>
          {backendConnected ? '✓ Backend Connected' : '✗ Backend Offline'}
        </div>
      </header>

      {connectionError && (
        <div className="error-banner">
          <p>{connectionError}</p>
        </div>
      )}

      <div className="tabs-container">
        <nav className="tabs-nav">
          <button
            className={`tab-button ${activeTab === 'qa' ? 'active' : ''}`}
            onClick={() => setActiveTab('qa')}
          >
            💬 Q&A
          </button>
          <button
            className={`tab-button ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            📄 Documents
          </button>
          <button
            className={`tab-button ${activeTab === 'eval' ? 'active' : ''}`}
            onClick={() => setActiveTab('eval')}
          >
            📊 Evaluations
          </button>
        </nav>

        <div className="tabs-content">
          {activeTab === 'qa' && <QAInterface />}
          {activeTab === 'documents' && <DocumentUpload />}
          {activeTab === 'eval' && <EvaluationLog />}
        </div>
      </div>

      <footer className="app-footer">
        <p>RAG Research Assistant © 2026 | DotMappers AI Engineer Assessment</p>
      </footer>
    </div>
  );
}

export default App;
