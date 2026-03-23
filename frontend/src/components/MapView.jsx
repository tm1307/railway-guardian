import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in Leaflet + React
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const MapView = ({ nodes }) => {
  const center = [28.6139, 77.2090]; // New Delhi reference
  
  // Simulated track path
  const trackPath = [
    [28.6139, 77.2090],
    [28.6239, 77.2190],
    [28.6339, 77.2290],
    [28.6439, 77.2390],
  ];

  return (
    <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%', background: '#111' }}>
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; OpenStreetMap &copy; CARTO'
      />
      
      <Polyline positions={trackPath} color="#3b82f6" weight={3} opacity={0.6} />

      {nodes.map(node => (
        <Marker 
          key={node.id} 
          position={[28.6139 + node.km * 0.005, 77.2090 + node.km * 0.005]}
        >
          <Popup>
            <div style={{ color: '#333' }}>
              <strong>{node.id}</strong><br />
              KM: {node.km}<br />
              Risk: {node.risk}%<br />
              Status: {node.status}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapView;
