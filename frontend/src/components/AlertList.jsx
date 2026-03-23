import React from 'react';

const AlertList = ({ alerts }) => {
  return (
    <div style={{ paddingBottom: '20px' }}>
      {alerts.length === 0 ? (
        <div style={{ padding: '20px', color: '#64748b', fontSize: '0.8rem', textAlign: 'center' }}>
          No active threats detected.
        </div>
      ) : (
        alerts.map(alert => (
          <div key={alert.id} className={`alert-item ${alert.severity}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontWeight: 600, color: alert.severity === 'critical' ? '#ef4444' : '#3b82f6' }}>
                {alert.type}
              </span>
              <span style={{ fontSize: '0.7rem', color: '#64748b' }}>{alert.time}</span>
            </div>
            <div style={{ color: '#94a3b8' }}>{alert.msg}</div>
            
            {alert.severity === 'critical' && (
              <button 
                onClick={() => window.open(`http://localhost:8000/api/v1/alerts/${alert.id}/report`, '_blank')}
                style={{
                  marginTop: '8px',
                  background: 'rgba(59, 130, 246, 0.2)',
                  border: '1px solid var(--accent-blue)',
                  color: 'white',
                  fontSize: '0.7rem',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                📥 Download Forensic Report
              </button>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default AlertList;
