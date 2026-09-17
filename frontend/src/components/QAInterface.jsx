import React, { useState } from 'react';
import { queryRAG } from '../services/api';

export const QAInterface = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showPassages, setShowPassages] = useState(false);

  const handleQuery = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await queryRAG(question);
      setResult(response.data);
    } catch (error) {
      setResult({
        answer: `Error: ${error.response?.data?.detail || error.message}`,
        sources: [],
        context_passages: [],
        latency: 0,
        metrics: {},
        injection_flagged: false
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  const getMetricColor = (metric, value) => {
    if (metric === 'hit_rate') return value > 0.7 ? 'green' : value > 0.4 ? 'amber' : 'red';
    if (metric === 'citation_correctness') return value > 0.8 ? 'green' : value > 0.5 ? 'amber' : 'red';
    if (metric === 'groundedness') return value > 0.6 ? 'green' : value > 0.3 ? 'amber' : 'red';
    return 'blue';
  };

  return (
    <div className="tab-content">
      <h2>💬 Q&A Interface</h2>

      <div className="qa-container">
        <div className="input-section">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about the research documents..."
            rows="4"
            disabled={loading}
          />
          <button
            onClick={handleQuery}
            disabled={loading || !question.trim()}
            className="query-button"
          >
            {loading ? '🔄 Processing...' : '🔍 Ask'}
          </button>
        </div>

        {result && (
          <div className="result-section">
            {result.injection_flagged && (
              <div className="warning">⚠️ Prompt injection attempt detected in query</div>
            )}

            <div className="answer-box">
              <h3>Answer</h3>
              <p>{result.answer}</p>
            </div>

            {result.sources && result.sources.length > 0 && (
              <div className="sources-box">
                <h4>📚 Sources</h4>
                <ul>
                  {result.sources.map((source, i) => (
                    <li key={i}>{source}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.latency && (
              <div className="latency">⏱️ Response time: {(result.latency * 1000).toFixed(2)}ms</div>
            )}

            {result.metrics && Object.keys(result.metrics).length > 0 && (
              <div className="metrics-box">
                <h4>📊 Metrics</h4>
                <div className="metrics-grid">
                  {Object.entries(result.metrics).map(([key, value]) => (
                    <div key={key} className={`metric-item ${getMetricColor(key, value)}`}>
                      <span className="metric-label">{key.replace(/_/g, ' ')}</span>
                      <span className="metric-value">
                        {typeof value === 'number' ? (
                          value <= 1 ? (value * 100).toFixed(1) + '%' : value.toFixed(2)
                        ) : (
                          value ? '✓' : '✗'
                        )}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => setShowPassages(!showPassages)}
              className="toggle-button"
            >
              {showPassages ? '▼ Hide' : '▶ Show'} Retrieved Passages ({result.context_passages?.length || 0})
            </button>

            {showPassages && result.context_passages && (
              <div className="passages-box">
                {result.context_passages.map((passage, i) => (
                  <div key={i} className="passage">
                    <h5>Source: {passage.metadata?.source} (Page {passage.metadata?.page}, Chunk {passage.metadata?.chunk_id})</h5>
                    <p>{passage.text}</p>
                    {passage.rerank_score && <small>Rerank Score: {passage.rerank_score.toFixed(3)}</small>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
