import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { BarChart2, List } from 'lucide-react';

const CenterPanel = ({ history, predictions }) => {
  const chartData = history.map(h => ({
    time: h.timestamp,
    energy: h.energy_consumption
  }));

  if (predictions) {
    chartData.push({
      time: "Now",
      energy: predictions.energy_consumption
    });
  }

  return (
    <div className="panel" style={{ overflow: 'hidden' }}>
      <h2 className="panel-title">
        <BarChart2 size={20} /> Energy Monitoring & Trends
      </h2>
      
      <div className="chart-container" style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={chartData}>
            <XAxis dataKey="time" hide />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="energy" 
              stroke="#3b82f6" 
              strokeWidth={2} 
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <h2 className="panel-title" style={{ marginTop: '16px' }}>
        <List size={20} /> Recent Batch History
      </h2>
      
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Batch ID</th>
              <th>Time</th>
              <th>Binder</th>
              <th>Temp</th>
              <th>Speed</th>
              <th>Energy</th>
            </tr>
          </thead>
          <tbody>
            {history.slice(-10).reverse().map((batch, i) => (
              <tr key={i}>
                <td>{batch.batch_id}</td>
                <td style={{ fontSize: '0.8rem' }}>
                  {batch.timestamp.split(' ')[1]}
                </td>
                <td>{batch.binder_amount} kg</td>
                <td>{batch.drying_temp} °C</td>
                <td>{batch.machine_speed} rpm</td>
                <td style={{ fontWeight: 600 }}>
                  {batch.energy_consumption} kWh
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CenterPanel;