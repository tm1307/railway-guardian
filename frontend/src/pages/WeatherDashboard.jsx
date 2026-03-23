import React, { useState, useEffect } from 'react';
import { Cloud, Thermometer, Droplets, Wind, Eye, Sun, AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getWeather, getForecast, getRailImpact } from '../services/api';

const WeatherDashboard = () => {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [impact, setImpact] = useState(null);

  const load = () => {
    getWeather().then(r => setWeather(r.data)).catch(() => {});
    getForecast().then(r => setForecast(r.data || [])).catch(() => {});
    getRailImpact().then(r => setImpact(r.data)).catch(() => {});
  };

  useEffect(() => {
    load();
    const iv = setInterval(load, 30000);
    return () => clearInterval(iv);
  }, []);

  if (!weather) return <div style={{ color: '#64748b', padding: 40 }}>Loading weather data...</div>;

  return (
    <div className="animate-in">
      <div className="page-title">Weather & Environment</div>
      <div className="page-subtitle">Delhi NCR Railway Corridor • Live Environmental Monitoring</div>

      {/* Weather Hero */}
      <div className="weather-hero">
        <div>
          <div className="weather-temp">{weather.temperature}°</div>
          <div className="weather-condition">{weather.condition}</div>
          <div className="weather-detail">Delhi Railway Corridor</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px 24px', marginLeft: 'auto' }}>
          <WeatherStat icon={<Droplets size={14} />} label="Humidity" value={`${weather.humidity}%`} />
          <WeatherStat icon={<Wind size={14} />} label="Wind" value={`${weather.wind_speed} km/h ${weather.wind_direction}`} />
          <WeatherStat icon={<Eye size={14} />} label="Visibility" value={`${weather.visibility} km`} />
          <WeatherStat icon={<Thermometer size={14} />} label="Rail Temp" value={`${weather.rail_temp}°C`} />
          <WeatherStat icon={<Sun size={14} />} label="UV Index" value={weather.uv_index} />
          <WeatherStat icon={<Cloud size={14} />} label="Pressure" value={`${weather.pressure} hPa`} />
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 16 }}>
        {/* Rail Impact */}
        <div className="card">
          <div className="card-header">
            <span className="card-title"><AlertTriangle size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />Railway Operations Impact</span>
            {impact && <span className={`badge ${impact.risk_level === 'HIGH' ? 'critical' : impact.risk_level === 'MEDIUM' ? 'high' : 'low'}`}>{impact.risk_level}</span>}
          </div>
          {impact && (
            <>
              <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: 12 }}>
                Risk Score: <strong style={{ color: impact.risk_score > 40 ? '#ef4444' : '#10b981' }}>{impact.risk_score}/100</strong>
              </div>
              {impact.impacts?.map((imp, i) => (
                <div key={i} style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.02)', borderRadius: 6, marginBottom: 6, borderLeft: `3px solid ${imp.severity === 'HIGH' ? '#ef4444' : imp.severity === 'MEDIUM' ? '#f59e0b' : '#10b981'}` }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: 0.5, color: imp.severity === 'HIGH' ? '#f87171' : imp.severity === 'MEDIUM' ? '#fbbf24' : '#34d399' }}>
                    {imp.type.replace(/_/g, ' ')}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: 2 }}>{imp.detail}</div>
                </div>
              ))}
              <div style={{ marginTop: 12, padding: 10, background: 'rgba(59,130,246,0.06)', borderRadius: 6, fontSize: '0.75rem', color: '#60a5fa' }}>
                <strong>Recommendation:</strong> {impact.recommendation}
              </div>
            </>
          )}
        </div>

        {/* 24h Forecast */}
        <div className="card">
          <div className="card-header"><span className="card-title">24-Hour Temperature Forecast</span></div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={forecast.slice(0, 24)}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
              <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 9 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', fontSize: '0.75rem', borderRadius: 6 }} />
              <Bar dataKey="temperature" fill="#06b6d4" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div style={{ maxHeight: 140, overflowY: 'auto', marginTop: 8 }}>
            <table className="data-table">
              <thead>
                <tr><th>Hour</th><th>Temp</th><th>Condition</th><th>Wind</th></tr>
              </thead>
              <tbody>
                {forecast.slice(0, 12).map((f, i) => (
                  <tr key={i}>
                    <td>{f.hour}</td>
                    <td>{f.temperature}°C</td>
                    <td>{f.condition}</td>
                    <td>{f.wind_speed} km/h</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const WeatherStat = ({ icon, label, value }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
    <span style={{ color: '#64748b' }}>{icon}</span>
    <div>
      <div style={{ fontSize: '0.65rem', color: '#64748b' }}>{label}</div>
      <div style={{ fontSize: '0.82rem', fontWeight: 600 }}>{value}</div>
    </div>
  </div>
);

export default WeatherDashboard;
