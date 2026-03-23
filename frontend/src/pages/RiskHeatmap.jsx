import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip as LTooltip } from 'react-leaflet';
import { getHeatmap, getRiskScores } from '../services/api';
import 'leaflet/dist/leaflet.css';

const RiskHeatmap = () => {
  const [zones, setZones] = useState([]);
  const [scores, setScores] = useState([]);

  const load = () => {
    getHeatmap().then(r => setZones(r.data || [])).catch(() => {});
    getRiskScores().then(r => setScores(r.data || [])).catch(() => {});
  };

  useEffect(() => {
    load();
    const iv = setInterval(load, 10000);
    return () => clearInterval(iv);
  }, []);

  const riskColor = (score) => {
    if (score > 70) return '#ef4444';
    if (score > 50) return '#f59e0b';
    if (score > 30) return '#3b82f6';
    return '#10b981';
  };

  const criticalZones = scores.filter(s => s.risk_score > 50).length;
  const avgRisk = scores.length > 0 ? Math.round(scores.reduce((s, z) => s + z.risk_score, 0) / scores.length) : 0;

  return (
    <div className="animate-in">
      <div className="page-title">Risk Heatmap</div>
      <div className="page-subtitle">Zone-wise threat assessment • Auto-refreshing every 10s</div>

      <div className="kpi-grid" style={{ marginBottom: 16 }}>
        <div className="kpi-card">
          <div className="kpi-icon red"><span style={{ fontSize: '1.2rem', fontWeight: 800 }}>{criticalZones}</span></div>
          <div><div className="kpi-label">High-Risk Zones</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon amber"><span style={{ fontSize: '1.2rem', fontWeight: 800 }}>{avgRisk}</span></div>
          <div><div className="kpi-label">Average Risk Score</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon green"><span style={{ fontSize: '1.2rem', fontWeight: 800 }}>{scores.length}</span></div>
          <div><div className="kpi-label">Monitored Zones</div></div>
        </div>
      </div>

      <div className="grid-2-1">
        {/* Heatmap */}
        <div className="map-container" style={{ height: 450 }}>
          <MapContainer center={[28.61, 77.23]} zoom={10} style={{ height: '100%', width: '100%' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {zones.map((z, i) => (
              <CircleMarker key={i} center={[z.lat, z.lng]} radius={Math.max(10, z.risk_score / 4)}
                pathOptions={{ color: riskColor(z.risk_score), fillColor: riskColor(z.risk_score), fillOpacity: 0.35, weight: 2 }}>
                <LTooltip>
                  <div style={{ fontFamily: 'Inter', fontSize: 11 }}>
                    <strong>{z.name}</strong><br />
                    Risk: <strong style={{ color: riskColor(z.risk_score) }}>{z.risk_score.toFixed(0)}</strong> ({z.risk_level})<br />
                    {z.factors?.slice(0, 2).join(', ')}
                  </div>
                </LTooltip>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        {/* Risk Table */}
        <div className="card" style={{ maxHeight: 450, overflowY: 'auto' }}>
          <div className="card-header"><span className="card-title">Zone Risk Ranking</span></div>
          <table className="data-table">
            <thead>
              <tr><th>Zone</th><th>Score</th><th>Level</th></tr>
            </thead>
            <tbody>
              {scores.map((s, i) => (
                <tr key={i}>
                  <td style={{ fontSize: '0.75rem' }}>{s.name}</td>
                  <td><strong style={{ color: riskColor(s.risk_score) }}>{s.risk_score.toFixed(0)}</strong></td>
                  <td><span className={`badge ${s.risk_level === 'CRITICAL' ? 'critical' : s.risk_level === 'HIGH' ? 'high' : s.risk_level === 'MEDIUM' ? 'medium' : 'low'}`}>{s.risk_level}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RiskHeatmap;
