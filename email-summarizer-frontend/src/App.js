import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  const authenticate = async () => {
    setIsAuthenticating(true);
    setError(null);
    
    // Open authentication in a new window
    const authWindow = window.open(
      'http://localhost:5000/auth',
      'Google Authentication',
      'width=600,height=800'
    );

    // Check periodically if auth is complete
    const checkAuth = setInterval(() => {
      if (authWindow.closed) {
        clearInterval(checkAuth);
        setIsAuthenticating(false);
        // Try fetching summary after authentication
        fetchSummary();
      }
    }, 1000);
  };

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/get-summary');
      const data = await response.json();
      
      if (response.status === 401) {
        // Need authentication
        await authenticate();
        return;
      }

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch summary');
      }
      
      setSummary(data.summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Email Summarizer</h1>
        <p>Click the button below to get summaries of the past 24 hours of emails</p>
      </header>

      <main className="App-main">
        <button 
          className="summary-button" 
          onClick={fetchSummary}
          disabled={loading || isAuthenticating}
        >
          {loading ? 'Generating Summary...' : 
           isAuthenticating ? 'Authenticating with Google...' : 
           'Get Email Summary'}
        </button>

        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            {error.includes('authenticate') && (
              <p>Please complete the Google authentication in the popup window to continue.</p>
            )}
          </div>
        )}

        {summary && (
          <div className="summary-container">
            <h2>Your Email Summary</h2>
            <div className="summary-content">
              <ReactMarkdown>{summary}</ReactMarkdown>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;