import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import DashboardLayout from './layouts/DashboardLayout';
import Login from './pages/Login';
import SecurityDashboard from './pages/SecurityDashboard';
import Surveillance from './pages/Surveillance';
import SensorMonitoring from './pages/SensorMonitoring';
import WeatherDashboard from './pages/WeatherDashboard';
import RailwayMap from './pages/RailwayMap';
import RiskHeatmap from './pages/RiskHeatmap';
import IntentPrediction from './pages/IntentPrediction';

import InfraManagement from './pages/InfraManagement';
import MaintenanceScheduler from './pages/MaintenanceScheduler';
import './index.css';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const App = () => (
  <AuthProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<SecurityDashboard />} />
          <Route path="surveillance" element={<Surveillance />} />
          <Route path="sensors" element={<SensorMonitoring />} />
          <Route path="weather" element={<WeatherDashboard />} />
          <Route path="map" element={<RailwayMap />} />
          <Route path="risk" element={<RiskHeatmap />} />
          <Route path="prediction" element={<IntentPrediction />} />

          <Route path="infrastructure" element={<InfraManagement />} />
          <Route path="schedules" element={<MaintenanceScheduler />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </AuthProvider>
);

export default App;
