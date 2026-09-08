import React from 'react';
import { Settings, Clock, AlertTriangle } from 'lucide-react';

const LeftPanel = ({ params, onParamChange, predictions, alertsCount }) => {
  return (
    <div className="panel">
      <h2 className="panel-title">
        <Settings size={20} /> Parameters & Overview
      </h2>
      
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span className="metric-label">Batch ID</span>
          <span className="badge bg-good">Active</span>
        </div>
        <div className="metric-value">BATCH_1000_SIM</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
          <Clock size={14} /> {new Date().toLocaleTimeString()}
        </div>
      </div>

      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div className="metric-label">Active Alerts</div>
          <div className="metric-value status-alert">{alertsCount}</div>
        </div>
        <AlertTriangle size={32} color={alertsCount > 0 ? "var(--color-alert)" : "var(--color-good)"} />
      </div>

      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Adjust Parameters</h3>
        
        <div className="form-group">
          <label>Granulation Time (min) <span>{params.granulation_time}</span></label>
          <input 
            type="range" min="15" max="75" step="1" 
            value={params.granulation_time} 
            onChange={(e) => onParamChange('granulation_time', e.target.value)} 
          />
        </div>
        
        <div className="form-group">
          <label>Binder Amount (kg) <span>{params.binder_amount}</span></label>
          <input 
            type="range" min="1" max="15" step="0.5" 
            value={params.binder_amount} 
            onChange={(e) => onParamChange('binder_amount', e.target.value)} 
          />
        </div>
        
        <div className="form-group">
          <label>Drying Temp (°C) <span>{params.drying_temp}</span></label>
          <input 
            type="range" min="30" max="95" step="1" 
            value={params.drying_temp} 
            onChange={(e) => onParamChange('drying_temp', e.target.value)} 
          />
        </div>
        
        <div className="form-group">
          <label>Drying Time (min) <span>{params.drying_time}</span></label>
          <input 
            type="range" min="20" max="150" step="5" 
            value={params.drying_time} 
            onChange={(e) => onParamChange('drying_time', e.target.value)} 
          />
        </div>

        <div className="form-group">
          <label>Compression Force (kN) <span>{params.compression_force}</span></label>
          <input 
            type="range" min="5" max="40" step="1" 
            value={params.compression_force} 
            onChange={(e) => onParamChange('compression_force', e.target.value)} 
          />
        </div>
        
        <div className="form-group">
          <label>Machine Speed (rpm) <span>{params.machine_speed}</span></label>
          <input 
            type="range" min="10" max="80" step="1" 
            value={params.machine_speed} 
            onChange={(e) => onParamChange('machine_speed', e.target.value)} 
          />
        </div>
      </div>
      
      {predictions && (
        <div className="card" style={{ background: 'var(--color-accent)', color: 'white' }}>
          <div className="metric-label" style={{ color: '#e2e8f0' }}>Predicted Energy (kWh)</div>
          <div className="metric-value">{predictions.energy_consumption.toFixed(2)}</div>
        </div>
      )}
    </div>
  );
};

export default LeftPanel;
