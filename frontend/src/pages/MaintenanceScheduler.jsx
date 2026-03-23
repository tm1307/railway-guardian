import React, { useState, useEffect } from 'react';
import { ClipboardList, Clock, Users, CheckCircle, Plus, Trash2, ToggleLeft, ToggleRight } from 'lucide-react';
import { getSchedules, createSchedule, deleteSchedule, toggleSchedule } from '../services/api';
import { useAuth } from '../context/AuthContext';

const MaintenanceScheduler = () => {
  const [schedules, setSchedules] = useState([]);
  const [filter, setFilter] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const { hasRole } = useAuth();

  // Form state
  const [form, setForm] = useState({
    section: '', task: '', team: '', start_time: '', end_time: '',
  });

  const loadSchedules = () => {
    getSchedules().then(r => setSchedules(r.data || [])).catch(() => {});
  };

  useEffect(() => { loadSchedules(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await createSchedule(form);
      setShowForm(false);
      setForm({ section: '', task: '', team: '', start_time: '', end_time: '' });
      loadSchedules();
    } catch (err) {
      alert('Failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this schedule?')) return;
    await deleteSchedule(id);
    loadSchedules();
  };

  const handleToggle = async (id) => {
    await toggleSchedule(id);
    loadSchedules();
  };

  const filtered = filter === 'all' ? schedules : schedules.filter(s => s.status === filter);
  const inProgress = schedules.filter(s => s.status === 'in_progress').length;
  const completed = schedules.filter(s => s.status === 'completed').length;
  const overdue = schedules.filter(s => s.status === 'inactive').length;
  const scheduled = schedules.filter(s => s.status === 'scheduled').length;

  const statusBadge = (s) => {
    if (s === 'completed') return 'operational';
    if (s === 'in_progress') return 'medium';
    if (s === 'inactive') return 'offline';
    return 'high'; // scheduled
  };

  const sections = [
    'NDLS-GZB (New Delhi – Ghaziabad)',
    'NDLS-NZM (New Delhi – Nizamuddin)',
    'NZM-FDB (Nizamuddin – Faridabad)',
    'NDLS-DEC (New Delhi – Delhi Cantt)',
    'DLI-SSB (Old Delhi – Shakurbasti)',
    'FDB-OKA (Faridabad – Okhla)',
    'ANVT-GZB (Anand Vihar – Ghaziabad)',
    'DSR-SSB (Sarai Rohilla – Shakurbasti)',
  ];

  const tasks = [
    'Ultrasonic Rail Testing', 'Signal Calibration', 'OHE Wire Tensioning',
    'Bridge Load Test', 'Track Polishing', 'Switch Lubrication',
    'Level Crossing Gate Service', 'Relay Room HVAC Check',
    'Catenary Dropper Inspection', 'Rail Weld Inspection',
    'Ballast Tamping', 'Drainage Clearing',
  ];

  return (
    <div className="animate-in">
      <div className="page-title">Maintenance Scheduler</div>
      <div className="page-subtitle">
        Create and manage maintenance windows.
        {inProgress > 0 && <span style={{ color: '#10b981', fontWeight: 600 }}> • {inProgress} active window(s) — person alerts suppressed in these zones</span>}
      </div>

      <div className="kpi-grid" style={{ marginBottom: 16 }}>
        <div className="kpi-card"><div className="kpi-icon blue"><ClipboardList size={20} /></div><div><div className="kpi-value">{schedules.length}</div><div className="kpi-label">Total Tasks</div></div></div>
        <div className="kpi-card"><div className="kpi-icon cyan"><Clock size={20} /></div><div><div className="kpi-value">{inProgress}</div><div className="kpi-label">In Progress</div></div></div>
        <div className="kpi-card"><div className="kpi-icon green"><CheckCircle size={20} /></div><div><div className="kpi-value">{completed}</div><div className="kpi-label">Completed</div></div></div>
        <div className="kpi-card"><div className="kpi-icon amber"><Clock size={20} /></div><div><div className="kpi-value">{scheduled}</div><div className="kpi-label">Scheduled</div></div></div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        {['all', 'scheduled', 'in_progress', 'completed', 'inactive'].map(f => (
          <button key={f} className="quick-action-btn"
            style={filter === f ? { background: 'rgba(59,130,246,0.2)', borderColor: '#3b82f6' } : {}}
            onClick={() => setFilter(f)}>
            {f.replace('_', ' ').toUpperCase()}
          </button>
        ))}
        {hasRole('admin', 'operator') && (
          <button className="btn btn-primary" style={{ marginLeft: 'auto' }} onClick={() => setShowForm(!showForm)}>
            <Plus size={14} /> New Schedule
          </button>
        )}
      </div>

      {/* Create Form */}
      {showForm && hasRole('admin', 'operator') && (
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card-header"><span className="card-title">Create Maintenance Schedule</span></div>
          <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Section</label>
              <select className="form-input" value={form.section} onChange={e => setForm({ ...form, section: e.target.value })} required>
                <option value="">Select section</option>
                {sections.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Task</label>
              <select className="form-input" value={form.task} onChange={e => setForm({ ...form, task: e.target.value })} required>
                <option value="">Select task</option>
                {tasks.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Team</label>
              <input className="form-input" value={form.team} onChange={e => setForm({ ...form, team: e.target.value })} placeholder="e.g. P-Way Gang Alpha" required />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Start Time (IST)</label>
              <input className="form-input" type="datetime-local" value={form.start_time} onChange={e => setForm({ ...form, start_time: e.target.value })} required />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">End Time (IST)</label>
              <input className="form-input" type="datetime-local" value={form.end_time} onChange={e => setForm({ ...form, end_time: e.target.value })} required />
            </div>
            <div style={{ display: 'flex', alignItems: 'end', gap: 8 }}>
              <button type="submit" className="btn btn-primary">Create Schedule</button>
              <button type="button" className="btn" style={{ color: '#64748b' }} onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Schedule Table */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><Users size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />Maintenance Activities</span>
        </div>
        <div style={{ maxHeight: 450, overflowY: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr><th>#</th><th>Task</th><th>Section</th><th>Team</th><th>Schedule</th><th>Status</th>{hasRole('admin','operator') && <th>Actions</th>}</tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={7} style={{ textAlign: 'center', color: '#64748b', padding: 20 }}>No schedules found. Create one above.</td></tr>
              ) : filtered.map(s => (
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td><div style={{ fontWeight: 600, fontSize: '0.78rem' }}>{s.task}</div></td>
                  <td style={{ fontSize: '0.75rem' }}>{s.section}</td>
                  <td style={{ fontSize: '0.75rem' }}>{s.team}</td>
                  <td style={{ fontSize: '0.72rem', fontVariantNumeric: 'tabular-nums' }}>
                    <div>{s.start_time ? new Date(s.start_time).toLocaleString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }) : '--'}</div>
                    <div style={{ color: '#64748b' }}>→ {s.end_time ? new Date(s.end_time).toLocaleString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }) : '--'}</div>
                  </td>
                  <td><span className={`badge ${statusBadge(s.status)}`}>{s.status?.replace('_', ' ')}</span></td>
                  {hasRole('admin','operator') && (
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button onClick={() => handleToggle(s.id)} title={s.is_active ? 'Deactivate' : 'Activate'}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 2 }}>
                          {s.is_active
                            ? <ToggleRight size={18} color="#10b981" />
                            : <ToggleLeft size={18} color="#64748b" />}
                        </button>
                        {hasRole('admin') && (
                          <button onClick={() => handleDelete(s.id)} title="Delete"
                            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 2 }}>
                            <Trash2 size={16} color="#ef4444" />
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MaintenanceScheduler;
