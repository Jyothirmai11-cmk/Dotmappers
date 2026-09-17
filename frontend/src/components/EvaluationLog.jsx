import React, { useState, useEffect } from 'react';
import { getEvaluations, clearEvaluations } from '../services/api';

export const EvaluationLog = () => {
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEvaluations();
    const interval = setInterval(fetchEvaluations, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchEvaluations = async () => {
    try {
      const response = await getEvaluations();
      setEvaluations(response.data.evaluations || []);
    } catch (error) {
      console.error('Error fetching evaluations:', error);
    }
  };

  const handleClear = async () => {
    if (window.confirm('Clear all evaluation logs?')) {
      try {
        await clearEvaluations();
        setEvaluations([]);
      } catch (error) {
        console.error('Error clearing evaluations:', error);
      }
    }
  };

  const getColor = (value) => {
    if (value >= 0.7) return 'green';
    if (value >= 0.4) return 'amber';
    return 'red';
  };

  const formatValue = (value) => {
    if (typeof value === 'number' && value <= 1) {
      return (value * 100).toFixed(1) + '%';
    }
    if (typeof value === 'number') {
      return value.toFixed(2);
    }
    return value ? '✓' : '✗';
  };

  return (
    <div className="tab-content">
      <h2>📊 Evaluation Log</h2>

      <div className="eval-controls">
        <button onClick={fetchEvaluations} disabled={loading} className="refresh-button">
          🔄 Refresh
        </button>
        <button onClick={handleClear} disabled={evaluations.length === 0} className="clear-button">
          🗑️ Clear All
        </button>
        <span className="eval-count">Total Queries: {evaluations.length}</span>
      </div>

      {evaluations.length === 0 ? (
        <p className="no-data">No evaluation data yet. Ask questions in the Q&A tab!</p>
      ) : (
        <div className="eval-table-wrapper">
          <table className="eval-table">
            <thead>
              <tr>
                <th>Question</th>
                <th className="metric-col">Hit Rate</th>
                <th className="metric-col">Citation</th>
                <th className="metric-col">Groundedness</th>
                <th className="metric-col">Refusal</th>
                <th className="metric-col">Latency</th>
                <th className="metric-col">Injection</th>
              </tr>
            </thead>
            <tbody>
              {evaluations.map((eval, i) => (
                <tr key={i}>
                  <td className="question-cell" title={eval.question}>
                    {eval.question.substring(0, 50)}...
                  </td>
                  <td className={`metric-cell ${getColor(eval.hit_rate)}`}>
                    {formatValue(eval.hit_rate)}
                  </td>
                  <td className={`metric-cell ${getColor(eval.citation_correctness)}`}>
                    {formatValue(eval.citation_correctness)}
                  </td>
                  <td className={`metric-cell ${getColor(eval.groundedness)}`}>
                    {formatValue(eval.groundedness)}
                  </td>
                  <td className={`metric-cell ${eval.refusal_accuracy ? 'green' : 'red'}`}>
                    {eval.refusal_accuracy ? '✓' : '✗'}
                  </td>
                  <td className="metric-cell">
                    {(eval.latency * 1000).toFixed(0)}ms
                  </td>
                  <td className="metric-cell">
                    {eval.injection_flagged ? '⚠️' : '✓'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="legend">
        <div className="legend-item"><span className="legend-color green"></span> Strong (>70%)</div>
        <div className="legend-item"><span className="legend-color amber"></span> Moderate (40-70%)</div>
        <div className="legend-item"><span className="legend-color red"></span> Weak (<40%)</div>
      </div>
    </div>
  );
};
