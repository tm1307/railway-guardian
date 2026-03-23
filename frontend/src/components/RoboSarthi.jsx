import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Bot } from 'lucide-react';
import { sendChatMessage } from '../services/api';

const RoboSarthi = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'नमस्ते! I am Robo Sarthi, your Railway Guardian AI assistant. Ask me about SOPs, sensor data, alerts, weather impact, or system commands.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text) => {
    const msg = text || input.trim();
    if (!msg) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: msg }]);
    setLoading(true);
    try {
      const res = await sendChatMessage(msg);
      setMessages(prev => [...prev, { role: 'bot', text: res.data.response || res.data.message || 'No response.' }]);
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: 'Connection error. Please check backend.' }]);
    }
    setLoading(false);
  };

  const quickActions = ['System status', 'Emergency SOP', 'Sensor thresholds', 'Weather impact'];

  return (
    <>
      {/* Floating Button */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          style={{
            position: 'fixed', bottom: 24, right: 24, zIndex: 9999,
            width: 56, height: 56, borderRadius: '50%',
            background: 'linear-gradient(135deg, #FF9933, #138808)',
            border: '2px solid rgba(255,255,255,0.2)',
            color: '#fff', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 20px rgba(255,153,51,0.4)',
            transition: 'all 0.3s ease',
          }}
          title="Robo Sarthi - AI Assistant"
        >
          <Bot size={28} />
        </button>
      )}

      {/* Chat Panel */}
      {open && (
        <div style={{
          position: 'fixed', bottom: 24, right: 24, zIndex: 9999,
          width: 380, height: 520, borderRadius: 16,
          background: '#0f172a',
          border: '1px solid rgba(255,153,51,0.3)',
          boxShadow: '0 8px 40px rgba(0,0,0,0.5)',
          display: 'flex', flexDirection: 'column',
          overflow: 'hidden',
          animation: 'slideUp 0.3s ease',
        }}>
          {/* Header */}
          <div style={{
            padding: '12px 16px',
            background: 'linear-gradient(135deg, rgba(255,153,51,0.15), rgba(19,136,8,0.15))',
            borderBottom: '1px solid rgba(255,153,51,0.2)',
            display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <div style={{
              width: 36, height: 36, borderRadius: '50%',
              background: 'linear-gradient(135deg, #FF9933, #138808)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Bot size={20} color="#fff" />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: '0.85rem' }}>Robo Sarthi</div>
              <div style={{ fontSize: '0.65rem', color: '#10b981' }}>● Railway AI Assistant</div>
            </div>
            <button onClick={() => setOpen(false)}
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: 4 }}>
              <X size={18} />
            </button>
          </div>

          {/* Messages */}
          <div style={{
            flex: 1, overflowY: 'auto', padding: '12px 14px',
            display: 'flex', flexDirection: 'column', gap: 10,
          }}>
            {messages.map((m, i) => (
              <div key={i} style={{
                alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '85%',
                padding: '8px 12px',
                borderRadius: m.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                background: m.role === 'user'
                  ? 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(59,130,246,0.1))'
                  : 'rgba(148,163,184,0.08)',
                border: `1px solid ${m.role === 'user' ? 'rgba(59,130,246,0.2)' : 'rgba(148,163,184,0.1)'}`,
                fontSize: '0.78rem',
                lineHeight: 1.45,
                color: '#e2e8f0',
              }}>
                {m.text}
              </div>
            ))}
            {loading && (
              <div style={{ alignSelf: 'flex-start', padding: '8px 12px', fontSize: '0.78rem', color: '#64748b' }}>
                Thinking...
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Quick Actions */}
          {messages.length <= 2 && (
            <div style={{ padding: '4px 14px 8px', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {quickActions.map(q => (
                <button key={q} onClick={() => handleSend(q)}
                  style={{
                    padding: '4px 10px', fontSize: '0.68rem', borderRadius: 20,
                    background: 'rgba(255,153,51,0.08)', border: '1px solid rgba(255,153,51,0.2)',
                    color: '#fbbf24', cursor: 'pointer',
                  }}>{q}</button>
              ))}
            </div>
          )}

          {/* Input */}
          <form
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            style={{
              padding: '8px 12px', borderTop: '1px solid rgba(148,163,184,0.1)',
              display: 'flex', gap: 8,
            }}
          >
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask Robo Sarthi..."
              style={{
                flex: 1, background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(148,163,184,0.15)', borderRadius: 8,
                padding: '8px 12px', color: '#e2e8f0', fontSize: '0.78rem',
                outline: 'none',
              }}
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}
              style={{
                background: 'linear-gradient(135deg, #FF9933, #138808)',
                border: 'none', borderRadius: 8, padding: '0 14px',
                color: '#fff', cursor: 'pointer', opacity: !input.trim() ? 0.4 : 1,
              }}>
              <Send size={16} />
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default RoboSarthi;
