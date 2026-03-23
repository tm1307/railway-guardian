import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Shield, Activity, Video, Map, BarChart3, Cloud,
  Brain, Cpu, MessageSquare, Wrench, ClipboardList,
  LogOut, Radio, User
} from 'lucide-react';
import RoboSarthi from '../components/RoboSarthi';
import '../index.css';

const DashboardLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [clock, setClock] = useState('');

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setClock(now.toLocaleTimeString('en-IN', { hour12: false }) + ' IST');
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    {
      group: 'SECURITY',
      items: [
        { to: '/dashboard', icon: <Activity size={16} />, label: 'Dashboard' },
        { to: '/surveillance', icon: <Video size={16} />, label: 'Surveillance' },
      ]
    },
    {
      group: 'MONITORING',
      items: [
        { to: '/sensors', icon: <Radio size={16} />, label: 'Sensor Analytics' },
        { to: '/weather', icon: <Cloud size={16} />, label: 'Weather & Env' },
        { to: '/map', icon: <Map size={16} />, label: 'Railway Map' },
      ]
    },
    {
      group: 'INTELLIGENCE',
      items: [
        { to: '/risk', icon: <BarChart3 size={16} />, label: 'Risk Heatmap' },
      ]
    },
    {
      group: 'MAINTENANCE',
      items: [
        { to: '/infrastructure', icon: <Cpu size={16} />, label: 'Infrastructure' },
        { to: '/schedules', icon: <ClipboardList size={16} />, label: 'Maintenance' },
      ]
    },
  ];

  return (
    <div className="app-shell">
      {/* Header */}
      <header className="top-header">
        <div className="header-brand">
          <div className="tricolor-bar" />
          <div>
            <h1>Railway Guardian</h1>
            <div className="subtitle">Ministry of Railways • Directorate of Security</div>
          </div>
        </div>
        <div className="header-right">
          <span className="header-clock">{clock}</span>
          <div className="header-status-badge online">
            <div className="pulse-dot" />
            SYSTEM SECURE
          </div>
          <div className="user-badge">
            <User size={14} />
            {user?.username?.toUpperCase()} ({user?.role})
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside className="sidebar">
        <nav>
          {navItems.map((group) => (
            <div key={group.group}>
              <div className="nav-group-label">{group.group}</div>
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
                >
                  {item.icon}
                  {item.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button className="btn-logout" onClick={handleLogout}>
            <LogOut size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            TERMINATE SESSION
          </button>
        </div>
      </aside>

      {/* Content */}
      <main className="main-viewport">
      </main>

      {/* Floating Chatbot */}
      <RoboSarthi />
    </div>
  );
};

export default DashboardLayout;
