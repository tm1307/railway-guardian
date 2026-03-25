import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { loginUser } from '../services/api';
import { Shield } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  if (isAuthenticated) {
    navigate('/dashboard');
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await loginUser(username, password);
      login(res.data.access_token, res.data.user_info);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="tricolor-bar" />
        <div style={{ textAlign: 'center', marginBottom: 8 }}>
          <Shield size={40} color="#3b82f6" />
        </div>
        <h2>RAILWAY GUARDIAN</h2>
        <div className="login-subtitle">INDIAN RAILWAYS • SECURE ACCESS PORTAL</div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Operative ID</label>
            <input
              className="form-input"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Authorization Key</label>
            <input
              className="form-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>
          {error && <div className="login-error">{error}</div>}
          <button className="btn-login" type="submit" disabled={loading}>
            {loading ? 'AUTHENTICATING...' : 'INITIATE SECURE SESSION'}
          </button>
        </form>

        <div style={{ marginTop: 20, textAlign: 'center', fontSize: '0.68rem', color: '#64748b' }}>
          <div>Authorized Personnel Only • Ministry of Railways</div>
          <div style={{ marginTop: 4 }}>Unauthorized access is a punishable offence under IT Act, 2000</div>
        </div>
      </div>
    </div>
  );
};

export default Login;
