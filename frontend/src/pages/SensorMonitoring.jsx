import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Thermometer, Volume2, Gauge, Smartphone, Wifi, WifiOff } from 'lucide-react';
import { getSensorLatest, getSensorHistory, connectPhyphox, getPhyphoxStatus, createWS } from '../services/api';

const SensorMonitoring = () => {
  const [readings, setReadings] = useState([]);
  const [liveData, setLiveData] = useState([]);
  const [phyphoxIP, setPhyphoxIP] = useState('');
  const [phyphoxStatus, setPhyphoxStatus] = useState({ connected: false });
  const [connecting, setConnecting] = useState(false);
  const [dataSource, setDataSource] = useState('SIMULATION');

  useEffect(() => {
    getSensorLatest().then(r => setReadings(r.data || [])).catch(() => {});
    getPhyphoxStatus().then(r => setPhyphoxStatus(r.data || {})).catch(() => {});

    const ws = createWS('sensors');
    ws.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data);
        setDataSource(d.source || 'SIMULATION');
        setLiveData(prev => [...prev, {
          time: new Date(d.timestamp).toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          vibration: d.vibration,
          temperature: d.temperature,
          strain: d.strain,
          acoustic: d.acoustic,
          node: d.node_name,
          source: d.source,
          rawAccel: d.raw_accel,
        }].slice(-120));
      } catch {}
    };

    // Refresh phyphox status every 5s
    const statusIv = setInterval(() => {
      getPhyphoxStatus().then(r => {
        setPhyphoxStatus(r.data || {});
      }).catch(() => {});
    }, 5000);

    return () => {
      ws.close();
      clearInterval(statusIv);
    };
  }, []);

  const handleConnectPhyphox = async () => {
    if (!phyphoxIP.trim()) return;
    setConnecting(true);
    try {
      const res = await connectPhyphox(phyphoxIP.trim());
      setPhyphoxStatus({ connected: res.data.connected });
      if (!res.data.connected) alert(res.data.message);
    } catch (err) {
      alert('Failed to connect: ' + (err.response?.data?.detail || err.message));
    }
    setConnecting(false);
  };

  // Group latest readings by node
  const nodeMap = {};
  readings.forEach(r => {
    if (!nodeMap[r.node_id]) nodeMap[r.node_id] = {};
    nodeMap[r.node_id][r.sensor_type] = r;
  });

  const lastPoint = liveData[liveData.length - 1] || {};

  return (
    <div className="animate-in">
      <div className="page-title">Sensor Analytics</div>
      <div className="page-subtitle">
        {dataSource === 'PHYPHOX_LIVE' ? (
          <span style={{ color: '#10b981', fontWeight: 600 }}>📱 PHYPHOX LIVE • Real phone sensor data active</span>
        ) : (
          <span>Simulated sensor stream • Connect Phyphox for real data</span>
        )}
      </div>

      {/* Phyphox Connect Panel */}
      <div className="card" style={{ marginBottom: 16, padding: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Smartphone size={18} color={phyphoxStatus.connected ? '#10b981' : '#64748b'} />
            <span style={{ fontSize: '0.82rem', fontWeight: 600 }}>Phyphox Phone Sensor</span>
            {phyphoxStatus.connected ? (
              <span className="badge operational" style={{ fontSize: '0.6rem' }}>
                <Wifi size={10} style={{ marginRight: 3 }} /> CONNECTED
              </span>
            ) : (
              <span className="badge offline" style={{ fontSize: '0.6rem' }}>
                <WifiOff size={10} style={{ marginRight: 3 }} /> DISCONNECTED
              </span>
            )}
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <input
              className="form-input"
              value={phyphoxIP}
              onChange={e => setPhyphoxIP(e.target.value)}
              placeholder="Phone IP e.g. 192.168.1.5:8080"
              style={{ width: 220, fontSize: '0.78rem', padding: '6px 10px' }}
            />
            <button className="btn btn-primary" onClick={handleConnectPhyphox} disabled={connecting}>
              {connecting ? 'Connecting...' : 'Connect'}
            </button>
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748b', marginLeft: 'auto' }}>
            Open Phyphox → Accelerometer → ▶ Play → Enable "Remote Access"
          </div>
        </div>
      </div>

      {/* Live Accelerometer (if Phyphox connected) */}
      {dataSource === 'PHYPHOX_LIVE' && lastPoint.rawAccel && (
        <div className="kpi-grid" style={{ marginBottom: 16 }}>
          <div className="kpi-card">
            <div className="kpi-icon red"><span style={{ fontWeight: 800, fontSize: '0.9rem' }}>X</span></div>
            <div><div className="kpi-value" style={{ fontSize: '1.2rem', color: '#ef4444' }}>{lastPoint.rawAccel.x?.toFixed(4)}</div><div className="kpi-label">Accel X (m/s²)</div></div>
          </div>
          <div className="kpi-card">
            <div className="kpi-icon green"><span style={{ fontWeight: 800, fontSize: '0.9rem' }}>Y</span></div>
            <div><div className="kpi-value" style={{ fontSize: '1.2rem', color: '#10b981' }}>{lastPoint.rawAccel.y?.toFixed(4)}</div><div className="kpi-label">Accel Y (m/s²)</div></div>
          </div>
          <div className="kpi-card">
            <div className="kpi-icon blue"><span style={{ fontWeight: 800, fontSize: '0.9rem' }}>Z</span></div>
            <div><div className="kpi-value" style={{ fontSize: '1.2rem', color: '#3b82f6' }}>{lastPoint.rawAccel.z?.toFixed(4)}</div><div className="kpi-label">Accel Z (m/s²)</div></div>
          </div>
          <div className="kpi-card">
            <div className="kpi-icon purple"><Activity size={20} /></div>
            <div><div className="kpi-value" style={{ fontSize: '1.2rem' }}>{lastPoint.vibration?.toFixed(4)}</div><div className="kpi-label">Total Magnitude (g)</div></div>
          </div>
        </div>
      )}

      {/* Live Sensor Cards */}
      <div className="sensor-grid" style={{ marginBottom: 20 }}>
        {Object.entries(nodeMap).slice(0, 6).map(([nodeId, sensors]) => (
          <div key={nodeId} className="sensor-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ fontSize: '0.7rem', color: '#64748b', fontWeight: 600 }}>{nodeId}</span>
              {sensors.vibration?.source && (
                <span className={`badge ${sensors.vibration.source === 'PHYPHOX_LIVE' ? 'operational' : 'offline'}`} style={{ fontSize: '0.55rem' }}>
                  {sensors.vibration.source === 'PHYPHOX_LIVE' ? '📱 REAL' : 'SIM'}
                </span>
              )}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <SensorVal icon={<Activity size={12} />} label="Vibration" value={sensors.vibration?.value?.toFixed(3)} unit="g" status={sensors.vibration?.status} />
              <SensorVal icon={<Thermometer size={12} />} label="Temp" value={sensors.temperature?.value?.toFixed(1)} unit="°C" status={sensors.temperature?.status} />
              <SensorVal icon={<Gauge size={12} />} label="Strain" value={sensors.strain?.value?.toFixed(0)} unit="μɛ" status={sensors.strain?.status} />
              <SensorVal icon={<Volume2 size={12} />} label="Acoustic" value={sensors.acoustic?.value?.toFixed(0)} unit="dB" status={sensors.acoustic?.status} />
            </div>
          </div>
        ))}
      </div>

      {/* Live Charts */}
      <div className="grid-2" style={{ marginBottom: 16 }}>
        <div className="card">
          <div className="card-header">
            <span className="card-title">Live Vibration</span>
            <span className="badge critical" style={{ fontSize: '0.6rem' }}>● STREAMING</span>
          </div>
          {liveData.length < 2 ? (
            <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', fontSize: '0.82rem' }}>Accumulating data (every 3s)...</div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={liveData.slice(-40)}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
                <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 9 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} domain={[0, 0.6]} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', fontSize: '0.75rem', borderRadius: 6 }} />
                <Line type="monotone" dataKey="vibration" stroke="#ef4444" strokeWidth={2} dot={false} name="Vibration (g)" animationDuration={300} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="card">
          <div className="card-header">
            <span className="card-title">Live Temperature</span>
            <span className="badge low" style={{ fontSize: '0.6rem' }}>● STREAMING</span>
          </div>
          {liveData.length < 2 ? (
            <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', fontSize: '0.82rem' }}>Accumulating data (every 3s)...</div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={liveData.slice(-40)}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
                <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 9 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} domain={[20, 50]} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', fontSize: '0.75rem', borderRadius: 6 }} />
                <Line type="monotone" dataKey="temperature" stroke="#f59e0b" strokeWidth={2} dot={false} name="Temp (°C)" animationDuration={300} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header"><span className="card-title">Live Strain</span></div>
          {liveData.length < 2 ? (
            <div style={{ height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', fontSize: '0.82rem' }}>Waiting...</div>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={liveData.slice(-40)}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
                <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 9 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', fontSize: '0.75rem', borderRadius: 6 }} />
                <Line type="monotone" dataKey="strain" stroke="#8b5cf6" strokeWidth={1.5} dot={false} name="Strain (μɛ)" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">Live Acoustic</span></div>
          {liveData.length < 2 ? (
            <div style={{ height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', fontSize: '0.82rem' }}>Waiting...</div>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={liveData.slice(-40)}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
                <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 9 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', fontSize: '0.75rem', borderRadius: 6 }} />
                <Line type="monotone" dataKey="acoustic" stroke="#06b6d4" strokeWidth={1.5} dot={false} name="Acoustic (dB)" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};

const SensorVal = ({ icon, label, value, unit, status }) => (
  <div>
    <div style={{ fontSize: '0.62rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: 3 }}>
      {icon} {label}
    </div>
    <div style={{ fontSize: '1rem', fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
      <span className={`sensor-status ${status || 'normal'}`} />
      {value || '--'}<span style={{ fontSize: '0.65rem', color: '#64748b', marginLeft: 2 }}>{unit}</span>
    </div>
  </div>
);

export default SensorMonitoring;
