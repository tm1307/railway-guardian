import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Activity, AlertTriangle, Clock, TrendingUp, Shield, Wrench } from 'lucide-react';
import api from '../services/api';

const PredictiveHealth = () => {
  const [sections, setSections] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [healthRes, anomRes] = await Promise.all([
        api.get('/api/v1/predictive/health'),
        api.get('/api/v1/predictive/anomalies'),
      ]);
      setSections(healthRes.data || []);
      setAnomalies(anomRes.data || []);
    } catch (e) {
      console.error('PTFE fetch error:', e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    const iv = setInterval(fetchData, 10000); // Refresh every 10s
    return () => clearInterval(iv);
  }, []);

  const avgHealth = sections.length > 0
    ? Math.round(sections.reduce((s, x) => s + x.health_pct, 0) / sections.length)
    : 100;
  const criticalCount = sections.filter(s => s.risk_level === 'CRITICAL').length;
  const highCount = sections.filter(s => s.risk_level === 'HIGH').length;
  const avgDaysToFail = sections.length > 0
    ? Math.round(sections.reduce((s, x) => s + x.days_to_failure, 0) / sections.length)
    : 0;

  const riskColor = (level) => {
    if (level === 'CRITICAL') return '#ef4444';
    if (level === 'HIGH') return '#f59e0b';
    if (level === 'MEDIUM') return '#3b82f6';
    return '#10b981';
  };

  if (loading) {
    return (
      <div className="animate-in" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh', color: '#64748b' }}>
        Initializing Predictive Track Failure Engine...
      </div>
    );
  }

  return (
    <div className="animate-in">
      <div className="page-title">Predictive Track Health AI</div>
      <div className="page-subtitle">
        Miner's Rule Cumulative Fatigue Analysis • EWMA Anomaly Detection • Failure Prediction
      </div>

      {/* KPIs */}
      <div className="kpi-grid" style={{ marginBottom: 16 }}>
        <div className="kpi-card">
          <div className="kpi-icon green"><Shield size={20} /></div>
          <div>
            <div className="kpi-value">{avgHealth}%</div>
            <div className="kpi-label">Avg Track Health</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon red"><AlertTriangle size={20} /></div>
          <div>
            <div className="kpi-value">{criticalCount}</div>
            <div className="kpi-label">Critical Sections</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon amber"><Clock size={20} /></div>
          <div>
            <div className="kpi-value">{avgDaysToFail}d</div>
            <div className="kpi-label">Avg Days to Failure</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon purple"><TrendingUp size={20} /></div>
          <div>
            <div className="kpi-value">{anomalies.length}</div>
            <div className="kpi-label">Anomalies Detected</div>
          </div>
        </div>
      </div>

      {/* Section Health Cards */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header">
          <span className="card-title"><Activity size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />Section Health — Fatigue Analysis</span>
          <span className="badge operational" style={{ fontSize: '0.6rem' }}>● LIVE</span>
        </div>
        {sections.length === 0 ? (
          <div style={{ padding: 30, textAlign: 'center', color: '#64748b', fontSize: '0.82rem' }}>
            Accumulating sensor data for fatigue analysis (needs ~30s of readings)...
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 12 }}>
            {sections.map((s) => (
              <div key={s.node_id} style={{
                padding: 14, borderRadius: 8,
                background: 'rgba(255,255,255,0.02)',
                border: `1px solid ${riskColor(s.risk_level)}22`,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.82rem' }}>{s.node_name}</div>
                    <div style={{ fontSize: '0.65rem', color: '#64748b' }}>{s.node_id} • {s.readings_count} readings</div>
                  </div>
                  <span className={`badge ${s.risk_level === 'CRITICAL' ? 'critical' : s.risk_level === 'HIGH' ? 'high' : s.risk_level === 'MEDIUM' ? 'medium' : 'low'}`}>
                    {s.risk_level}
                  </span>
                </div>

                {/* Health Bar */}
                <div style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#94a3b8', marginBottom: 3 }}>
                    <span>Track Health</span>
                    <span style={{ color: riskColor(s.risk_level), fontWeight: 700 }}>{s.health_pct}%</span>
                  </div>
                  <div style={{ height: 6, background: 'rgba(255,255,255,0.05)', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{
                      width: `${s.health_pct}%`, height: '100%', borderRadius: 3,
                      background: `linear-gradient(90deg, ${riskColor(s.risk_level)}, ${riskColor(s.risk_level)}88)`,
                      transition: 'width 0.5s ease',
                    }} />
                  </div>
                </div>

                {/* Stats Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, fontSize: '0.72rem' }}>
                  <div>
                    <span style={{ color: '#64748b' }}>Predicted Failure: </span>
                    <span style={{ fontWeight: 600 }}>{s.days_to_failure}d</span>
                  </div>
                  <div>
                    <span style={{ color: '#64748b' }}>Fatigue Index: </span>
                    <span style={{ fontWeight: 600 }}>{s.fatigue_index}</span>
                  </div>
                  <div>
                    <span style={{ color: '#64748b' }}>Anomaly Rate: </span>
                    <span style={{ fontWeight: 600, color: s.anomaly_rate > 10 ? '#ef4444' : '#94a3b8' }}>{s.anomaly_rate}%</span>
                  </div>
                  <div>
                    <span style={{ color: '#64748b' }}>Trend: </span>
                    <span style={{ fontWeight: 600, color: s.vibration_trend === 'increasing' ? '#f59e0b' : '#10b981' }}>
                      {s.vibration_trend === 'increasing' ? '↑ Rising' : s.vibration_trend === 'decreasing' ? '↓ Falling' : '→ Stable'}
                    </span>
                  </div>
                </div>

                {/* Sparkline */}
                {s.sparkline && s.sparkline.length > 5 && (
                  <div style={{ marginTop: 8 }}>
                    <ResponsiveContainer width="100%" height={50}>
                      <LineChart data={s.sparkline.map((v, i) => ({ i, v }))}>
                        <Line type="monotone" dataKey="v" stroke={riskColor(s.risk_level)} strokeWidth={1.5} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Maintenance Recommendation */}
                <div style={{
                  marginTop: 8, padding: '6px 10px', borderRadius: 6,
                  background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.15)',
                  fontSize: '0.68rem', color: '#34d399',
                }}>
                  <Wrench size={10} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                  Schedule maintenance by <strong>{s.recommended_maintenance}</strong>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Anomalies Table */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><AlertTriangle size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />EWMA Anomaly Detections</span>
          <span className="badge high" style={{ fontSize: '0.6rem' }}>{anomalies.length} detected</span>
        </div>
        {anomalies.length === 0 ? (
          <div style={{ padding: 20, textAlign: 'center', color: '#64748b', fontSize: '0.82rem' }}>
            No anomalies detected yet. The EWMA engine needs ~1 minute of readings to baseline.
          </div>
        ) : (
          <div style={{ maxHeight: 300, overflowY: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr><th>Section</th><th>Z-Score</th><th>Severity</th><th>Vibration</th></tr>
              </thead>
              <tbody>
                {anomalies.map((a, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600, fontSize: '0.75rem' }}>{a.node_name}</td>
                    <td style={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600, color: a.z_score > 4 ? '#ef4444' : '#f59e0b' }}>{a.z_score.toFixed(2)}σ</td>
                    <td><span className={`badge ${a.severity === 'CRITICAL' ? 'critical' : a.severity === 'HIGH' ? 'high' : 'medium'}`}>{a.severity}</span></td>
                    <td style={{ fontSize: '0.75rem' }}>{a.vibration?.toFixed(3)}g</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictiveHealth;
