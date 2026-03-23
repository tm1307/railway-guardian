import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Brain, AlertTriangle, Shield, Clock } from 'lucide-react';
import { getPredictions, getPredictionTimeline } from '../services/api';

const IntentPrediction = () => {
  const [predictions, setPredictions] = useState([]);
  const [timeline, setTimeline] = useState([]);

  const load = () => {
    getPredictions().then(r => setPredictions(r.data || [])).catch(() => {});
    getPredictionTimeline().then(r => setTimeline(r.data || [])).catch(() => {});
  };

  useEffect(() => {
    load();
    const iv = setInterval(load, 15000);
    return () => clearInterval(iv);
  }, []);

  const threatColor = (t) => {
    const map = { tampering: '#ef4444', theft: '#f59e0b', vandalism: '#8b5cf6', trespassing: '#06b6d4', safe: '#10b981' };
    return map[t] || '#64748b';
  };

  const threats = predictions.filter(p => p.predicted_threat !== 'safe');
  const highConf = threats.filter(p => p.confidence > 0.7);

  return (
    <div className="animate-in">
      <div className="page-title">Intent Prediction Engine</div>
      <div className="page-subtitle">AI-powered threat prediction • Pattern analysis • Proactive security</div>

      <div className="kpi-grid" style={{ marginBottom: 16 }}>
        <div className="kpi-card">
          <div className="kpi-icon red"><Brain size={20} /></div>
          <div><div className="kpi-value">{threats.length}</div><div className="kpi-label">Active Predictions</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon amber"><AlertTriangle size={20} /></div>
          <div><div className="kpi-value">{highConf.length}</div><div className="kpi-label">High Confidence Threats</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon green"><Shield size={20} /></div>
          <div><div className="kpi-value">{predictions.filter(p => p.predicted_threat === 'safe').length}</div><div className="kpi-label">Safe Zones</div></div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 16 }}>
        {/* Timeline Chart */}
        <div className="card">
          <div className="card-header"><span className="card-title"><Clock size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />24h Threat Timeline</span></div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={timeline}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
              <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 9 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', fontSize: '0.75rem', borderRadius: 6 }} />
              <Bar dataKey="threat_count" fill="#ef4444" radius={[3, 3, 0, 0]} name="Threats" />
              <Bar dataKey="safe_count" fill="#10b981" radius={[3, 3, 0, 0]} name="Safe" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Confidence Distribution */}
        <div className="card">
          <div className="card-header"><span className="card-title">Threat Distribution</span></div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: '8px 0' }}>
            {['tampering', 'theft', 'vandalism', 'trespassing'].map(type => {
              const count = predictions.filter(p => p.predicted_threat === type).length;
              const pct = predictions.length > 0 ? (count / predictions.length * 100).toFixed(0) : 0;
              return (
                <div key={type}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 3 }}>
                    <span style={{ color: threatColor(type), fontWeight: 600, textTransform: 'uppercase' }}>{type}</span>
                    <span style={{ color: '#94a3b8' }}>{count} ({pct}%)</span>
                  </div>
                  <div className="health-bar">
                    <div className="health-bar-fill" style={{ width: `${pct}%`, background: threatColor(type) }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Prediction Cards */}
      <div className="card">
        <div className="card-header"><span className="card-title">Zone Predictions</span></div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 12, maxHeight: 350, overflowY: 'auto' }}>
          {predictions.map((p, i) => (
            <div key={i} className="prediction-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span className="prediction-zone">{p.zone_name}</span>
                <span className={`badge ${p.predicted_threat === 'safe' ? 'safe' : p.confidence > 0.7 ? 'critical' : 'high'}`}>
                  {p.predicted_threat.toUpperCase()}
                </span>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginBottom: 4 }}>
                Confidence: <strong style={{ color: threatColor(p.predicted_threat) }}>{(p.confidence * 100).toFixed(1)}%</strong> • Window: {p.time_window}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#64748b', marginBottom: 6, fontStyle: 'italic' }}>{p.reasoning}</div>
              <div className="confidence-bar">
                <div className="confidence-fill" style={{ width: `${p.confidence * 100}%`, background: threatColor(p.predicted_threat) }} />
              </div>
              {p.predicted_threat !== 'safe' && (
                <div style={{ marginTop: 6, fontSize: '0.7rem', color: '#60a5fa', padding: '4px 8px', background: 'rgba(59,130,246,0.06)', borderRadius: 4 }}>
                  ➜ {p.recommended_action}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default IntentPrediction;
