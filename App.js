import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [systemStatus, setSystemStatus] = useState({
    backend: false,
    models: false,
    audio: false
  });

  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const backendResponse = await fetch('http://localhost:5000/health', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (backendResponse.ok) {
        const status = await backendResponse.json();
        setSystemStatus(status);
      }
    } catch (error) {
      console.error('Failed to check system status:', error);
      setSystemStatus({
        backend: false,
        models: false,
        audio: false
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    setIsLoading(true);
    checkSystemStatus();
  };

  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <h2>Initializing Telugu AI Assistant</h2>
          <p>Loading models and connecting to services...</p>
        </div>
      </div>
    );
  }

  const allSystemsReady = Object.values(systemStatus).every(status => status);

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 Telugu AI Assistant</h1>
          <div className="status-indicators">
            <div className={`status-dot ${systemStatus.backend ? 'online' : 'offline'}`}>
              Backend
            </div>
            <div className={`status-dot ${systemStatus.models ? 'online' : 'offline'}`}>
              Models
            </div>
            <div className={`status-dot ${systemStatus.audio ? 'online' : 'offline'}`}>
              Audio
            </div>
          </div>
        </div>
      </header>

      <main className="app-main">
        {allSystemsReady ? (
          <ChatInterface />
        ) : (
          <div className="system-error">
            <div className="error-content">
              <h2>🚧 System Not Ready</h2>
              <p>Some services are not available:</p>
              <ul className="error-list">
                {!systemStatus.backend && <li>❌ Backend server connection failed</li>}
                {!systemStatus.models && <li>❌ AI models not loaded</li>}
                {!systemStatus.audio && <li>❌ Audio services unavailable</li>}
              </ul>
              <div className="error-actions">
                <button onClick={handleRetry} className="retry-button">
                  🔄 Retry Connection
                </button>
                <p className="help-text">
                  Make sure the Flask backend is running on port 5000
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Telugu AI Assistant - Powered by Phi-3 Mini, Whisper & Coqui TTS</p>
      </footer>
    </div>
  );
}

export default App;
