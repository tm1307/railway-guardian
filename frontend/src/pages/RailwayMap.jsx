import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker, Tooltip as LTooltip } from 'react-leaflet';
import { getHeatmap } from '../services/api';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix default icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Delhi major stations
const STATIONS = [
  { name: "New Delhi", lat: 28.6425, lng: 77.2195, code: "NDLS" },
  { name: "Old Delhi Jn", lat: 28.6606, lng: 77.2264, code: "DLI" },
  { name: "Hazrat Nizamuddin", lat: 28.5878, lng: 77.2508, code: "NZM" },
  { name: "Anand Vihar", lat: 28.6461, lng: 77.3152, code: "ANVT" },
  { name: "Delhi Sarai Rohilla", lat: 28.6607, lng: 77.1756, code: "DSR" },
  { name: "Tilak Bridge", lat: 28.6355, lng: 77.2434, code: "TKJ" },
  { name: "Delhi Cantt", lat: 28.5981, lng: 77.1504, code: "DEC" },
  { name: "Shakurbasti", lat: 28.6784, lng: 77.1511, code: "SSB" },
  { name: "Okhla", lat: 28.5310, lng: 77.2710, code: "OKA" },
  { name: "Ghaziabad Jn", lat: 28.6706, lng: 77.4381, code: "GZB" },
  { name: "Faridabad", lat: 28.4089, lng: 77.3178, code: "FDB" },
  { name: "Gurgaon", lat: 28.4595, lng: 77.0266, code: "GGN" },
];

// Track routes (simplified)
const ROUTES = [
  { name: "Main Line (NDLS-GZB)", points: [[28.6425,77.2195],[28.6355,77.2434],[28.6550,77.2450],[28.6706,77.4381]], color: "#3b82f6" },
  { name: "South Line (NDLS-FDB)", points: [[28.6425,77.2195],[28.5878,77.2508],[28.5310,77.2710],[28.4089,77.3178]], color: "#10b981" },
  { name: "West Line (NDLS-GGN)", points: [[28.6425,77.2195],[28.5981,77.1504],[28.4595,77.0266]], color: "#f59e0b" },
  { name: "North Line (DLI-SSB-DSR)", points: [[28.6606,77.2264],[28.6784,77.1511],[28.6607,77.1756]], color: "#8b5cf6" },
  { name: "NDLS-ANVT Link", points: [[28.6425,77.2195],[28.6461,77.3152]], color: "#06b6d4" },
];

const RailwayMap = () => {
  const [zones, setZones] = useState([]);

  useEffect(() => {
    getHeatmap().then(r => setZones(r.data || [])).catch(() => {});
    const iv = setInterval(() => {
      getHeatmap().then(r => setZones(r.data || [])).catch(() => {});
    }, 15000);
    return () => clearInterval(iv);
  }, []);

  const riskColor = (score) => {
    if (score > 70) return '#ef4444';
    if (score > 50) return '#f59e0b';
    if (score > 30) return '#3b82f6';
    return '#10b981';
  };

  return (
    <div className="animate-in">
      <div className="page-title">Delhi Railway Network Map</div>
      <div className="page-subtitle">Live station monitoring • Track sections • Risk overlay</div>

      <div className="grid-2-1">
        <div className="map-container" style={{ height: 520 }}>
          <MapContainer center={[28.61, 77.23]} zoom={11} style={{ height: '100%', width: '100%' }} scrollWheelZoom={true}>
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Track Routes */}
            {ROUTES.map((r, i) => (
              <Polyline key={i} positions={r.points} color={r.color} weight={3} opacity={0.7}>
                <LTooltip permanent={false}>{r.name}</LTooltip>
              </Polyline>
            ))}

            {/* Stations */}
            {STATIONS.map((s, i) => (
              <Marker key={i} position={[s.lat, s.lng]}>
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 12 }}>
                    <strong>{s.name}</strong><br />
                    Code: {s.code}<br />
                    Status: <span style={{ color: '#10b981' }}>Operational</span>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Risk Zones */}
            {zones.map((z, i) => (
              <CircleMarker key={i} center={[z.lat, z.lng]} radius={Math.max(8, z.risk_score / 5)}
                pathOptions={{ color: riskColor(z.risk_score), fillColor: riskColor(z.risk_score), fillOpacity: 0.3, weight: 2 }}>
                <LTooltip>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 11 }}>
                    <strong>{z.name}</strong><br />
                    Risk: {z.risk_score.toFixed(0)} ({z.risk_level})
                  </div>
                </LTooltip>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        <div>
          <div className="card" style={{ marginBottom: 12 }}>
            <div className="card-header"><span className="card-title">Track Sections</span></div>
            {ROUTES.map((r, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 0', fontSize: '0.78rem' }}>
                <div style={{ width: 12, height: 3, backgroundColor: r.color, borderRadius: 2 }} />
                <span style={{ color: '#cbd5e1' }}>{r.name}</span>
              </div>
            ))}
          </div>
          <div className="card">
            <div className="card-header"><span className="card-title">Station Status</span></div>
            <div style={{ maxHeight: 320, overflowY: 'auto' }}>
              {STATIONS.map((s, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: '1px solid rgba(148,163,184,0.08)', fontSize: '0.78rem' }}>
                  <span><strong>{s.code}</strong> — {s.name}</span>
                  <span className="badge operational">Online</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RailwayMap;
