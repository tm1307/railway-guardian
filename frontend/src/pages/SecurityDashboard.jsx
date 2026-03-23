import React, { useState, useEffect, useRef } from 'react';
import { Shield, AlertTriangle, Radio, TrendingUp, Activity, Zap, Send, Bell } from 'lucide-react';
import { AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { createWS, sendManualAlert, getActiveMaintenance } from '../services/api';
import { useAuth } from '../context/AuthContext';

const SecurityDashboard = () => {
  const { user, hasRole } = useAuth();
  const [liveAlerts, setLiveAlerts] = useState([]);
  const [alertTrend, setAlertTrend] = useState([]);
  const [sensorData, setSensorData] = useState([]);
  const [activeMaint, setActiveMaint] = useState([]);
  const totalCountRef = useRef(0);

  // Manual alert form
  const [showAlertForm, setShowAlertForm] = useState(false);
  const [alertForm, setAlertForm] = useState({ alert_type: 'SUSPICIOUS_ACTIVITY', severity: 'high', message: '', location: '' });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    // Fetch active maintenance windows
    getActiveMaintenance().then(r => setActiveMaint(r.data || [])).catch(() => {});
    const maintIv = setInterval(() => {
      getActiveMaintenance().then(r => setActiveMaint(r.data || [])).catch(() => {});
    }, 15000);

    const wsAlerts = createWS('alerts');
    wsAlerts.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        const now = new Date();
        const timeKey = now.toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit' });
        totalCountRef.current++;

        setLiveAlerts(prev => [{
          id: totalCountRef.current,
          type: data.alert_type,
          severity: (data.severity || 'low').toLowerCase(),
          time: now.toLocaleTimeString('en-IN', { hour12: false }),
          msg: data.explanation || data.alert_type,
          node: data.node_id || data.node_name,
          risk: data.risk_score || 0,
          source: data.source,
          reported_by: data.reported_by,
        }, ...prev].slice(0, 50));

        setAlertTrend(prev => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last && last.time === timeKey) {
            last.count = (last.count || 0) + 1;
          } else {
            copy.push({ time: timeKey, count: 1 });
          }
          return copy.slice(-30);
        });
      } catch {}
    };

    const wsSensors = createWS('sensors');
    wsSensors.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setSensorData(prev => [...prev, {
          time: new Date(data.timestamp).toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          vibration: data.vibration,
          temperature: data.temperature,
          node: data.node_name,
          source: data.source,
        }].slice(-60));
      } catch {}
    };

    return () => {
      clearInterval(maintIv);
      wsAlerts.close();
      wsSensors.close();
    };
  }, []);

  const handleSendAlert = async (e) => {
    e.preventDefault();
    if (!alertForm.message.trim()) return;
    setSending(true);
    try {
      await sendManualAlert(alertForm);
      setAlertForm({ ...alertForm, message: '', location: '' });
      setShowAlertForm(false);
    } catch (err) {
      alert('Failed: ' + (err.response?.data?.detail || err.message));
    }
    setSending(false);
  };

  const criticalCount = liveAlerts.filter(a => a.severity === 'critical').length;
  const highCount = liveAlerts.filter(a => a.severity === 'high').length;
  const avgRisk = liveAlerts.length > 0 ? Math.round(liveAlerts.reduce((s, a) => s + (a.risk || 0), 0) / liveAlerts.length) : 0;
  const lastSensor = sensorData[sensorData.length - 1] || {};

  return (
    <div className="animate-in">
      <div className="page-title">Security Dashboard</div>
      <div className="page-subtitle">
        Live WebSocket streams • {hasRole('admin') ? 'Admin Control Panel' : hasRole('operator') ? 'Operator View — Send alerts to command' : 'Viewer — Read-only access'}
      </div>

      {/* Active Maintenance Banner */}
      {activeMaint.length > 0 && (
        <div style={{ padding: '8px 14px', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 8, marginBottom: 12, fontSize: '0.78rem', color: '#34d399' }}>
          <strong>🔧 Active Maintenance:</strong> {activeMaint.map(m => `${m.section} (${m.task})`).join(' • ')} — Person alerts suppressed in these zones
        </div>
      )}

      {/* KPIs */}
      <div className="kpi-grid">
        <KPI icon={<AlertTriangle size={20} />} color="red" value={criticalCount} label="Critical Alerts" trend={`${liveAlerts.length} total`} />
        <KPI icon={<Zap size={20} />} color="amber" value={lastSensor.vibration ? `${lastSensor.vibration.toFixed(3)}g` : '--'} label="Live Vibration" trend={lastSensor.source === 'PHYPHOX_LIVE' ? '📱 Real' : 'Simulated'} />
        <KPI icon={<Radio size={20} />} color="blue" value={`${lastSensor.temperature ? lastSensor.temperature.toFixed(1) : '--'}°C`} label="Rail Temp" trend="Live stream" />
        <KPI icon={<TrendingUp size={20} />} color="purple" value={avgRisk || '--'} label="Avg Risk" trend={`${highCount} high`} />
      </div>

      {/* Operator Alert Button */}
      {hasRole('admin', 'operator') && (
        <div style={{ marginBottom: 16 }}>
          {!showAlertForm ? (
            <button className="btn btn-primary" onClick={() => setShowAlertForm(true)}>
              <Bell size={14} /> Send Manual Alert to Command
            </button>
          ) : (
            <div className="card" style={{ borderColor: 'rgba(239,68,68,0.3)' }}>
              <div className="card-header"><span className="card-title" style={{ color: '#f87171' }}>⚠ Send Alert to All Connected Users</span></div>
              <form onSubmit={handleSendAlert} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Alert Type</label>
                  <select className="form-input" value={alertForm.alert_type} onChange={e => setAlertForm({ ...alertForm, alert_type: e.target.value })}>
                    <option value="SUSPICIOUS_ACTIVITY">Suspicious Activity</option>
                    <option value="PERSON_DETECTED">Person on Track</option>
                    <option value="EMERGENCY">Emergency</option>
                    <option value="OBJECT_DETECTED">Object on Track</option>
                    <option value="EQUIPMENT_FAILURE">Equipment Failure</option>
                    <option value="PERIMETER_BREACH">Perimeter Breach</option>
                  </select>
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Severity</label>
                  <select className="form-input" value={alertForm.severity} onChange={e => setAlertForm({ ...alertForm, severity: e.target.value })}>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Location</label>
                  <input className="form-input" value={alertForm.location} onChange={e => setAlertForm({ ...alertForm, location: e.target.value })} placeholder="e.g. New Delhi Yard" />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Message *</label>
                  <input className="form-input" value={alertForm.message} onChange={e => setAlertForm({ ...alertForm, message: e.target.value })} placeholder="Describe the situation..." required />
                </div>
                <div style={{ gridColumn: '1/-1', display: 'flex', gap: 8 }}>
                  <button type="submit" className="btn" style={{ background: 'rgba(239,68,68,0.15)', borderColor: 'rgba(239,68,68,0.4)', color: '#f87171', fontWeight: 700 }} disabled={sending}>
                    <Send size={14} /> {sending ? 'Sending...' : 'Broadcast Alert'}
                  </button>
                  <button type="button" className="btn" style={{ color: '#64748b' }} onClick={() => setShowAlertForm(false)}>Cancel</button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {/* Charts */}
      <div className="grid-2" style={{ marginBottom: 16 }}>
        <div className="card">
          <div className="card-header">
            <span className="card-title"><Activity size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />Alerts Per Minute (Live)</span>
            <span className="badge critical" style={{ fontSize: '0.6rem' }}>● STREAMING</span>
          </div>
          {alertTrend.length < 2 ? (
            <Waiting>Accumulating alert data...</Waiting>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={alertTrend}>
                <defs><linearGradient id="alg" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} /><stop offset="95%" stopColor="#ef4444" stopOpacity={0} /></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
                <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 9 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', fontSize: '0.75rem', borderRadius: 6 }} />
                <Area type="monotone" dataKey="count" stroke="#ef4444" fill="url(#alg)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="card">
          <div className="card-header">
            <span className="card-title">Live Sensor Stream</span>
            <span className="badge low" style={{ fontSize: '0.6rem' }}>● 3s</span>
          </div>
          {sensorData.length < 3 ? (
            <Waiting>Waiting for sensor data...</Waiting>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={sensorData.slice(-30)}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
                <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 9 }} />
                <YAxis yAxisId="l" tick={{ fill: '#64748b', fontSize: 10 }} domain={[0, 0.6]} />
                <YAxis yAxisId="r" orientation="right" tick={{ fill: '#64748b', fontSize: 10 }} domain={[20, 50]} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', fontSize: '0.75rem', borderRadius: 6 }} />
                <Line yAxisId="l" type="monotone" dataKey="vibration" stroke="#ef4444" strokeWidth={2} dot={false} />
                <Line yAxisId="r" type="monotone" dataKey="temperature" stroke="#f59e0b" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Live Alert Feed */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><Activity size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />Live Alert Feed</span>
          <span className="badge critical" style={{ fontSize: '0.6rem' }}>● {liveAlerts.length}</span>
        </div>
        <div className="alert-feed">
          {liveAlerts.length === 0 ? (
            <Waiting>Waiting for live alerts (within ~10 seconds)...</Waiting>
          ) : liveAlerts.slice(0, 30).map((a, i) => (
            <div key={`${a.id}-${i}`} className={`alert-item ${a.severity}`} style={i === 0 ? { animation: 'slideUp 0.3s ease' } : {}}>
              <div style={{ minWidth: 0 }}>
                <span className="alert-time">{a.time}</span>
                <span className="alert-type" style={{ marginLeft: 8 }}>[{a.type}]</span>
                {a.source === 'OPERATOR_MANUAL' && <span style={{ marginLeft: 6, fontSize: '0.65rem', color: '#f59e0b', fontWeight: 700 }}>👤 OPERATOR</span>}
              </div>
              <div className="alert-msg">{a.msg}</div>
              <div style={{ marginLeft: 'auto', display: 'flex', gap: 6, flexShrink: 0 }}>
                <span className={`badge ${a.severity}`}>{a.severity}</span>
                <span className="badge medium">{a.node}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const KPI = ({ icon, color, value, label, trend }) => (
  <div className="kpi-card">
    <div className={`kpi-icon ${color}`}>{icon}</div>
    <div><div className="kpi-value">{value}</div><div className="kpi-label">{label}</div>{trend && <div className="kpi-trend">{trend}</div>}</div>
  </div>
);

const Waiting = ({ children }) => (
  <div style={{ height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', fontSize: '0.82rem' }}>{children}</div>
);

export default SecurityDashboard;
