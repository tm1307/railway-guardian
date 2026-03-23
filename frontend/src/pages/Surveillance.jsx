import React, { useState, useEffect, useRef } from 'react';
import { Upload, Video, FileVideo, AlertTriangle, CheckCircle } from 'lucide-react';
import { createWS, analyzeVideo } from '../services/api';

const Surveillance = () => {
  const [logs, setLogs] = useState([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const hiddenCanvasRef = useRef(null);
  const wsVisionRef = useRef(null);
  const [cameraAccess, setCameraAccess] = useState('PENDING');
  const [detectionCount, setDetectionCount] = useState(0);
  const [lastDetections, setLastDetections] = useState([]);
  const [fps, setFps] = useState(0);
  const frameCountRef = useRef(0);

  // Video upload state
  const [uploadResult, setUploadResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [mode, setMode] = useState('live'); // 'live' or 'upload'

  useEffect(() => {
    const fpsInterval = setInterval(() => {
      setFps(frameCountRef.current);
      frameCountRef.current = 0;
    }, 1000);

    const wsAlerts = createWS('alerts');
    wsAlerts.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data);
        setLogs(prev => [{ ...d, time: new Date().toLocaleTimeString('en-IN', { hour12: false }) }, ...prev].slice(0, 30));
      } catch {}
    };

    wsVisionRef.current = new WebSocket('ws://localhost:8000/api/v1/vision/ws/vision-stream');
    wsVisionRef.current.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.detections && canvasRef.current && videoRef.current) {
          frameCountRef.current++;
          setDetectionCount(data.detections.length);
          setLastDetections(data.detections);
          drawBoxes(data.detections);
        }
      } catch {}
    };

    if (navigator.mediaDevices?.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
        .then(stream => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play();
            setCameraAccess('GRANTED');
          }
        })
        .catch(() => setCameraAccess('DENIED'));
    }

    return () => {
      clearInterval(fpsInterval);
      wsAlerts.close();
      wsVisionRef.current?.close();
      videoRef.current?.srcObject?.getTracks().forEach(t => t.stop());
    };
  }, []);

  useEffect(() => {
    if (cameraAccess !== 'GRANTED' || mode !== 'live') return;
    let animId;
    let lastSend = 0;
    const SEND_FPS = 4;
    const process = (time) => {
      if (time - lastSend > 1000 / SEND_FPS) {
        const v = videoRef.current;
        const hc = hiddenCanvasRef.current;
        const ws = wsVisionRef.current;
        if (v && hc && ws?.readyState === WebSocket.OPEN && v.videoWidth > 0) {
          hc.width = v.videoWidth;
          hc.height = v.videoHeight;
          hc.getContext('2d').drawImage(v, 0, 0);
          ws.send(hc.toDataURL('image/jpeg', 0.7));
          lastSend = time;
        }
      }
      animId = requestAnimationFrame(process);
    };
    animId = requestAnimationFrame(process);
    return () => cancelAnimationFrame(animId);
  }, [cameraAccess, mode]);

  const drawBoxes = (detections) => {
    const c = canvasRef.current;
    const v = videoRef.current;
    if (!c || !v) return;
    c.width = v.clientWidth;
    c.height = v.clientHeight;
    const ctx = c.getContext('2d');
    ctx.clearRect(0, 0, c.width, c.height);
    const sx = c.width / v.videoWidth;
    const sy = c.height / v.videoHeight;

    detections.forEach(d => {
      const [x1, y1, x2, y2] = d.box;
      const x = x1 * sx, y = y1 * sy, w = (x2 - x1) * sx, h = (y2 - y1) * sy;
      const isPerson = d.label === 'person';
      const color = isPerson ? '#3b82f6' : '#ef4444';

      ctx.shadowColor = color;
      ctx.shadowBlur = 8;
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.5;
      ctx.strokeRect(x, y, w, h);

      ctx.shadowBlur = 0;
      const bLen = Math.min(20, w / 3, h / 3);
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(x, y + bLen); ctx.lineTo(x, y); ctx.lineTo(x + bLen, y); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x + w - bLen, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + bLen); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x, y + h - bLen); ctx.lineTo(x, y + h); ctx.lineTo(x + bLen, y + h); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x + w - bLen, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - bLen); ctx.stroke();

      const labelText = `${d.label.toUpperCase()} ${(d.confidence * 100).toFixed(0)}%`;
      ctx.font = 'bold 12px Inter, sans-serif';
      const tw = ctx.measureText(labelText).width + 10;
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.9;
      ctx.fillRect(x, y - 24, tw, 22);
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(labelText, x + 5, y - 8);
    });
  };

  const handleVideoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadResult(null);
    try {
      const res = await analyzeVideo(file);
      setUploadResult(res.data);
    } catch (err) {
      setUploadResult({ error: err.response?.data?.detail || 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="animate-in">
      <div className="page-title">Live Surveillance & Video Analysis</div>
      <div className="page-subtitle">YOLOv8 AI Detection • Webcam Feed • Video Upload Analysis</div>

      {/* Mode Toggle */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button className={`quick-action-btn ${mode === 'live' ? '' : ''}`}
          style={mode === 'live' ? { background: 'rgba(59,130,246,0.2)', borderColor: '#3b82f6' } : {}}
          onClick={() => setMode('live')}>
          <Video size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} /> Live Webcam
        </button>
        <button className={`quick-action-btn`}
          style={mode === 'upload' ? { background: 'rgba(59,130,246,0.2)', borderColor: '#3b82f6' } : {}}
          onClick={() => setMode('upload')}>
          <Upload size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} /> Upload Video
        </button>
      </div>

      {mode === 'live' ? (
        /* ─── LIVE WEBCAM MODE ─────────────────────────────── */
        <div className="surveillance-grid">
          <div className="video-feed-container">
            <div className="feed-badge live">● LIVE AI</div>
            {cameraAccess === 'PENDING' && <CameraMsg color="#f59e0b">Requesting camera access...</CameraMsg>}
            {cameraAccess === 'DENIED' && <CameraMsg color="#ef4444">Camera access denied. Enable in browser settings.</CameraMsg>}
            <video ref={videoRef} autoPlay playsInline muted style={{ display: cameraAccess === 'GRANTED' ? 'block' : 'none', width: '100%', height: '100%', objectFit: 'cover' }} />
            <canvas ref={canvasRef} style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }} />
            <canvas ref={hiddenCanvasRef} style={{ display: 'none' }} />
            <div style={{ position: 'absolute', bottom: 12, left: 12, display: 'flex', gap: 8 }}>
              <span className="badge medium">Detections: {detectionCount}</span>
              <span className="badge low">AI FPS: {fps}</span>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="card" style={{ flex: '0 0 auto' }}>
              <div className="card-header">
                <span className="card-title">Live Detections</span>
                <span className="badge medium">{detectionCount} objects</span>
              </div>
              <div style={{ maxHeight: 150, overflowY: 'auto' }}>
                {lastDetections.length === 0 ? (
                  <div style={{ color: '#64748b', fontSize: '0.78rem', padding: 8 }}>Point camera at objects...</div>
                ) : lastDetections.map((d, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 8px', borderBottom: '1px solid rgba(148,163,184,0.08)', fontSize: '0.78rem' }}>
                    <span style={{ color: d.label === 'person' ? '#3b82f6' : '#ef4444', fontWeight: 600 }}>{d.label.toUpperCase()}</span>
                    <span style={{ color: '#94a3b8' }}>{(d.confidence * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div className="card-header">
                <span className="card-title">Alert Feed</span>
                <span className="badge critical" style={{ fontSize: '0.6rem' }}>● LIVE</span>
              </div>
              <div className="alert-feed" style={{ flex: 1 }}>
                {logs.length === 0 ? (
                  <div style={{ color: '#64748b', padding: 20, fontSize: '0.78rem', textAlign: 'center' }}>Waiting for alerts...</div>
                ) : logs.map((l, i) => (
                  <div key={i} className={`alert-item ${(l.severity || 'low').toLowerCase()}`}>
                    <span className="alert-time">{l.time}</span>
                    <span className="alert-type" style={{ marginLeft: 6 }}>[{l.alert_type}]</span>
                    <div className="alert-msg">{l.explanation || l.alert_type}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* ─── VIDEO UPLOAD MODE ────────────────────────────── */
        <div className="grid-2">
          <div className="card">
            <div className="card-header">
              <span className="card-title"><FileVideo size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />Upload Video for Analysis</span>
            </div>
            <div style={{ padding: '20px 0' }}>
              <label style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center', padding: 30,
                border: '2px dashed rgba(59,130,246,0.3)', borderRadius: 10, cursor: 'pointer',
                background: 'rgba(59,130,246,0.04)', transition: 'all 0.2s',
              }}>
                <Upload size={36} color="#3b82f6" />
                <span style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: 10, color: '#94a3b8' }}>
                  {uploading ? 'Analyzing video with YOLOv8...' : 'Click to upload MP4, AVI, MOV'}
                </span>
                <span style={{ fontSize: '0.7rem', color: '#64748b', marginTop: 4 }}>
                  AI will sample frames and detect objects/threats
                </span>
                <input type="file" accept="video/*" onChange={handleVideoUpload} disabled={uploading}
                  style={{ display: 'none' }} />
              </label>
              {uploading && (
                <div style={{ textAlign: 'center', marginTop: 12, color: '#3b82f6', fontSize: '0.82rem' }}>
                  Processing... Running YOLOv8 on sampled frames ⏳
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title">Analysis Results</span>
              {uploadResult && !uploadResult.error && (
                <span className={`badge ${uploadResult.risk_level === 'HIGH' ? 'critical' : uploadResult.risk_level === 'MEDIUM' ? 'high' : 'low'}`}>
                  {uploadResult.risk_level} RISK
                </span>
              )}
            </div>
            {!uploadResult ? (
              <div style={{ color: '#64748b', padding: 30, textAlign: 'center', fontSize: '0.82rem' }}>
                Upload a video to see YOLOv8 detection results here.
              </div>
            ) : uploadResult.error ? (
              <div style={{ color: '#ef4444', padding: 20, textAlign: 'center' }}>{uploadResult.error}</div>
            ) : (
              <div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 12 }}>
                  <Stat label="File" value={uploadResult.filename} />
                  <Stat label="Duration" value={`${uploadResult.duration_sec}s`} />
                  <Stat label="Frames Analyzed" value={uploadResult.frames_analyzed} />
                  <Stat label="Total Detections" value={uploadResult.total_detections} />
                </div>

                {uploadResult.threat_detected && (
                  <div style={{ padding: 10, background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 6, marginBottom: 12 }}>
                    <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#f87171', display: 'flex', alignItems: 'center', gap: 6 }}>
                      <AlertTriangle size={14} /> Threats Detected
                    </div>
                    {Object.entries(uploadResult.threat_objects || {}).map(([cls, count]) => (
                      <div key={cls} style={{ fontSize: '0.75rem', color: '#fca5a5', marginTop: 2 }}>
                        {cls}: {count} detections
                      </div>
                    ))}
                  </div>
                )}

                {!uploadResult.threat_detected && (
                  <div style={{ padding: 10, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 6, marginBottom: 12 }}>
                    <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#34d399', display: 'flex', alignItems: 'center', gap: 6 }}>
                      <CheckCircle size={14} /> No threats detected
                    </div>
                  </div>
                )}

                <div className="card-title" style={{ marginBottom: 6 }}>Detection Summary</div>
                {Object.entries(uploadResult.detection_summary || {}).map(([cls, count]) => (
                  <div key={cls} style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0', borderBottom: '1px solid rgba(148,163,184,0.08)', fontSize: '0.78rem' }}>
                    <span style={{ color: cls === 'person' ? '#60a5fa' : '#f87171', fontWeight: 600 }}>{cls}</span>
                    <span style={{ color: '#94a3b8' }}>{count}×</span>
                  </div>
                ))}

                <div className="card-title" style={{ marginTop: 12, marginBottom: 6 }}>Frame-by-Frame</div>
                <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                  {uploadResult.frame_results?.map((fr, i) => (
                    <div key={i} style={{ padding: '4px 0', borderBottom: '1px solid rgba(148,163,184,0.06)', fontSize: '0.75rem' }}>
                      <span style={{ color: '#64748b' }}>{fr.timestamp_display}</span>
                      <span style={{ marginLeft: 8 }}>
                        {fr.detection_count > 0 ? (
                          fr.detections.map(d => d.class).join(', ')
                        ) : (
                          <span style={{ color: '#475569' }}>No detections</span>
                        )}
                      </span>
                      <span style={{ float: 'right', color: fr.detection_count > 0 ? '#f59e0b' : '#475569' }}>
                        {fr.detection_count} objects
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const CameraMsg = ({ color, children }) => (
  <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', color, fontSize: '0.85rem', fontWeight: 600 }}>{children}</div>
);

const Stat = ({ label, value }) => (
  <div style={{ padding: 8, background: 'rgba(255,255,255,0.02)', borderRadius: 6 }}>
    <div style={{ fontSize: '0.62rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</div>
    <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: 2 }}>{value}</div>
  </div>
);

export default Surveillance;
