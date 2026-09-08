import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LeftPanel from './components/LeftPanel';
import CenterPanel from './components/CenterPanel';
import RightPanel from './components/RightPanel';
import { Activity } from 'lucide-react';
import './index.css';

const API_BASE = (import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000').replace(/\/$/, '');

function App() {
  const [params, setParams] = useState({
    granulation_time: 40.0,
    binder_amount: 6.0,
    drying_temp: 60.0,
    drying_time: 75.0,
    compression_force: 20.0,
    machine_speed: 40.0
  });

  const [predictions, setPredictions] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistory();
    simulateBatch();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      simulateBatch();
    }, 500);
    return () => clearTimeout(timer);
  }, [params]);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/history`);
      if (res.data) setHistory(res.data);
    } catch (e) {
      console.error('Failed to fetch history', e);
    }
  };

  const simulateBatch = async () => {
    setLoading(true);
    try {
      const predRes = await axios.post(`${API_BASE}/predict`, params);
      setPredictions(predRes.data.predictions);
      
      let currentAlerts = [];
      if (predRes.data.is_parameter_anomaly) {
        currentAlerts.push("Unusual Parameters Detected");
      }

      // Simulate an occasional spike in actual energy compared to predicted
      const hasSpike = Math.random() > 0.85;
      const actualEnergy = predRes.data.predictions.energy_consumption + (hasSpike ? 25 : 0);
      
      const anomalyRes = await axios.post(`${API_BASE}/anomaly`, {
        ...params,
        actual_energy: actualEnergy
      });
      
      currentAlerts = [...currentAlerts, ...anomalyRes.data.alerts];
      setAlerts([...new Set(currentAlerts)]);

      const optRes = await axios.post(`${API_BASE}/optimize`, params);
      setRecommendations(optRes.data.recommendations);
      
    } catch (e) {
      console.error('Simulation error', e);
    }
    setLoading(false);
  };

  const handleParamChange = (name, value) => {
    setParams(prev => ({
      ...prev,
      [name]: parseFloat(value)
    }));
  };

  return (
    <div className="dashboard-container">
      <div className="panel" style={{ gridColumn: '1 / -1', padding: '16px 24px', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="panel-title" style={{ margin: 0, border: 'none', padding: 0 }}>
          <Activity size={24} color="var(--color-accent)" />
          AI-Driven Batch Process Dashboard
        </div>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <span className={`badge ${loading ? 'bg-warning' : 'bg-good'}`}>
            {loading ? 'Simulating...' : 'System Active'}
          </span>
        </div>
      </div>
      
      <LeftPanel 
        params={params} 
        onParamChange={handleParamChange} 
        predictions={predictions} 
        alertsCount={alerts.length} 
      />
      
      <CenterPanel 
        history={history} 
        predictions={predictions} 
      />
      
      <RightPanel 
        alerts={alerts} 
        recommendations={recommendations} 
        predictions={predictions} 
      />
    </div>
  );
}

export default App;
