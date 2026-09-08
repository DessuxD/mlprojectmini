import React from 'react';
import { AlertTriangle, Zap, CheckCircle, Percent } from 'lucide-react';

const RightPanel = ({ alerts, recommendations, predictions }) => {
  return (
    <div className="panel">
      <h2 className="panel-title">
        <AlertTriangle size={20} /> Alerts & Intelligence
      </h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {alerts.length === 0 ? (
          <div className="alert-item bg-good">
            <CheckCircle className="alert-icon status-good" size={20} />
            <div>
              <div style={{ fontWeight: 600, color: 'var(--color-good)' }}>System Normal</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>No anomalies detected in current batch.</div>
            </div>
          </div>
        ) : (
          alerts.map((alert, i) => (
            <div key={i} className="alert-item bg-alert">
              <AlertTriangle className="alert-icon status-alert" size={20} />
              <div>
                <div style={{ fontWeight: 600, color: 'var(--color-alert)' }}>{alert}</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Immediate attention may be required.</div>
              </div>
            </div>
          ))
        )}
      </div>

      <h2 className="panel-title" style={{ marginTop: '16px' }}>
        <Zap size={20} /> AI Recommendations
      </h2>
      
      <div className="card" style={{ background: '#f8fafc' }}>
        {recommendations.length === 0 ? (
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>No optimizations needed at current parameters.</div>
        ) : (
          <ul style={{ paddingLeft: '20px', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
            {recommendations.map((rec, i) => (
              <li key={i} style={{ marginBottom: '8px' }}>{rec}</li>
            ))}
          </ul>
        )}
      </div>

      <h2 className="panel-title" style={{ marginTop: '16px' }}>
        <Percent size={20} /> Quality & Yield Targets
      </h2>
      
      {predictions && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="card" style={{ textAlign: 'center' }}>
            <div className="metric-label">Predicted Quality</div>
            <div className={`metric-value ${predictions.quality_pct >= 90 ? 'status-good' : 'status-warning'}`}>
              {predictions.quality_pct.toFixed(1)}%
            </div>
          </div>
          
          <div className="card" style={{ textAlign: 'center' }}>
            <div className="metric-label">Predicted Yield</div>
            <div className={`metric-value ${predictions.yield_pct >= 90 ? 'status-good' : 'status-warning'}`}>
              {predictions.yield_pct.toFixed(1)}%
            </div>
          </div>
          
          <div className="card" style={{ textAlign: 'center' }}>
            <div className="metric-label">Performance Score</div>
            <div className="metric-value status-accent" style={{ color: 'var(--color-accent)' }}>
              {predictions.performance_score.toFixed(1)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RightPanel;
