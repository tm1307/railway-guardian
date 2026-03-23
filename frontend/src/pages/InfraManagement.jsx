import React, { useState, useEffect } from 'react';
import { Cpu, Wrench, AlertTriangle, CheckCircle } from 'lucide-react';
import { getAssets, getRecommendations } from '../services/api';

const InfraManagement = () => {
  const [assets, setAssets] = useState([]);
  const [recs, setRecs] = useState([]);

  useEffect(() => {
    getAssets().then(r => setAssets(r.data || [])).catch(() => {});
    getRecommendations().then(r => setRecs(r.data || [])).catch(() => {});
  }, []);

  const healthColor = (score) => {
    if (score > 80) return '#10b981';
    if (score > 60) return '#f59e0b';
    if (score > 40) return '#ef4444';
    return '#64748b';
  };

  const typeIcons = { track: '🛤', signal: '🚦', bridge: '🌉', switch: '🔀', station: '🏛', crossing: '🚧', ohe: '⚡', relay_room: '📡' };

  const operational = assets.filter(a => a.status === 'operational').length;
  const degraded = assets.filter(a => a.status === 'degraded').length;
  const critical = assets.filter(a => a.status === 'critical').length;

  return (
    <div className="animate-in">
      <div className="page-title">Smart Infrastructure Management</div>
      <div className="page-subtitle">Asset health monitoring • AI maintenance recommendations • Inspection tracking</div>

      <div className="kpi-grid" style={{ marginBottom: 16 }}>
        <div className="kpi-card">
          <div className="kpi-icon green"><CheckCircle size={20} /></div>
          <div><div className="kpi-value">{operational}</div><div className="kpi-label">Operational</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon amber"><AlertTriangle size={20} /></div>
          <div><div className="kpi-value">{degraded}</div><div className="kpi-label">Degraded</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon red"><Cpu size={20} /></div>
          <div><div className="kpi-value">{critical}</div><div className="kpi-label">Critical</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon blue"><Wrench size={20} /></div>
          <div><div className="kpi-value">{recs.length}</div><div className="kpi-label">Pending Actions</div></div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 16 }}>
        {/* Asset Inventory */}
        <div className="card">
          <div className="card-header"><span className="card-title">Infrastructure Assets</span></div>
          <div style={{ maxHeight: 420, overflowY: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr><th>Asset</th><th>Type</th><th>Health</th><th>Status</th></tr>
              </thead>
              <tbody>
                {assets.map((a, i) => (
                  <tr key={i}>
                    <td>
                      <div style={{ fontWeight: 600, fontSize: '0.78rem' }}>{a.name}</div>
                      <div style={{ fontSize: '0.68rem', color: '#64748b' }}>{a.location}</div>
                    </td>
                    <td>{typeIcons[a.asset_type] || '📦'} {a.asset_type}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <strong style={{ color: healthColor(a.health_score), fontSize: '0.82rem' }}>{a.health_score.toFixed(0)}%</strong>
                      </div>
                      <div className="health-bar" style={{ width: 60, marginTop: 2 }}>
                        <div className="health-bar-fill" style={{ width: `${a.health_score}%`, background: healthColor(a.health_score) }} />
                      </div>
                    </td>
                    <td><span className={`badge ${a.status}`}>{a.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="card">
          <div className="card-header">
            <span className="card-title"><Wrench size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />AI Maintenance Recommendations</span>
          </div>
          <div style={{ maxHeight: 420, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
            {recs.map((r, i) => (
              <div key={i} style={{
                padding: 12,
                background: 'rgba(255,255,255,0.02)',
                borderRadius: 8,
                borderLeft: `3px solid ${r.priority === 'URGENT' ? '#ef4444' : '#f59e0b'}`
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <strong style={{ fontSize: '0.78rem' }}>{r.asset_name}</strong>
                  <span className={`badge ${r.priority === 'URGENT' ? 'critical' : 'high'}`}>{r.priority}</span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: 4 }}>{r.recommendation}</div>
                <div style={{ display: 'flex', gap: 12, fontSize: '0.68rem', color: '#64748b' }}>
                  <span>Health: <strong style={{ color: healthColor(r.health_score) }}>{r.health_score.toFixed(0)}%</strong></span>
                  <span>Team: {r.team_required}</span>
                  <span>Est: {r.estimated_hours}h</span>
                </div>
              </div>
            ))}
            {recs.length === 0 && <div style={{ color: '#64748b', padding: 20, textAlign: 'center', fontSize: '0.8rem' }}>All assets in good condition.</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InfraManagement;
