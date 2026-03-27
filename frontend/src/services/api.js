import axios from 'axios';

// Use environment variable if deployed, otherwise fallback to localhost
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE_URL });

// Attach JWT token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('rg_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('rg_token');
      localStorage.removeItem('rg_user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// Auth
export const loginUser = (username, password) =>
  api.post('/api/v1/auth/login', new URLSearchParams({ username, password }), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
export const getMe = () => api.get('/api/v1/auth/me');

// Alerts
export const getAlerts = () => api.get('/api/v1/alerts/');

// Weather
export const getWeather = () => api.get('/api/v1/weather/current');
export const getForecast = () => api.get('/api/v1/weather/forecast');
export const getRailImpact = () => api.get('/api/v1/weather/rail-impact');

// Chatbot
export const sendChatMessage = (message) => api.post('/api/v1/chatbot/message', { message });

// Risk
export const getHeatmap = () => api.get('/api/v1/risk/heatmap');
export const getRiskScores = () => api.get('/api/v1/risk/scores');

// Intent
export const getPredictions = () => api.get('/api/v1/intent/predictions');
export const getPredictionTimeline = () => api.get('/api/v1/intent/timeline');

// Infrastructure
export const getAssets = () => api.get('/api/v1/infrastructure/assets');
export const getRecommendations = () => api.get('/api/v1/infrastructure/recommendations');

// Sensors + Phyphox
export const getSensorLatest = () => api.get('/api/v1/sensors/latest');
export const getSensorHistory = (type = 'vibration', hours = 6) =>
  api.get(`/api/v1/sensors/history?sensor_type=${type}&hours=${hours}`);
export const connectPhyphox = (ip_address) =>
  api.post('/api/v1/sensors/phyphox/connect', { ip_address });
export const getPhyphoxStatus = () => api.get('/api/v1/sensors/phyphox/status');
export const getPhyphoxLive = () => api.get('/api/v1/sensors/phyphox/live');

// Vision - Video upload
export const analyzeVideo = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/v1/vision/analyze-video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000, // 2 min for large videos
  });
};

// Maintenance
export const getSchedules = () => api.get('/api/v1/maintenance/schedules');
export const getActiveMaintenance = () => api.get('/api/v1/maintenance/active');
export const createSchedule = (data) => api.post('/api/v1/maintenance/schedules', data);
export const deleteSchedule = (id) => api.delete(`/api/v1/maintenance/schedules/${id}`);
export const toggleSchedule = (id) => api.post(`/api/v1/maintenance/schedules/${id}/toggle`);

// Operator manual alert
export const sendManualAlert = (data) => api.post('/api/v1/maintenance/alert', data);

// WebSocket helper
export const createWS = (channel = 'general') => {
  const wsUrl = BASE_URL.replace('http', 'ws');
  return new WebSocket(`${wsUrl}/ws/${channel}`);
};

export default api;
