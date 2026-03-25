import React, { useState, useEffect, useRef } from 'react';
import { Upload, Video, FileVideo, AlertTriangle, CheckCircle, Moon, Sun, Volume2, Eye } from 'lucide-react';
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
  const [nightMode, setNightMode] = useState(false);

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
          const ctx = hc.getContext('2d');

          // Night vision pre-processing: boost contrast + green tint
          if (nightMode) {
            ctx.filter = 'brightness(1.8) contrast(1.6) saturate(0)';
            ctx.drawImage(v, 0, 0);
            ctx.filter = 'none';
            // Apply green tint overlay for IR-style look
            const imgData = ctx.getImageData(0, 0, hc.width, hc.height);
            const px = imgData.data;
            for (let i = 0; i < px.length; i += 4) {
              const lum = px[i] * 0.299 + px[i+1] * 0.587 + px[i+2] * 0.114;
              px[i] = lum * 0.15;     // R (minimal)
              px[i+1] = lum * 0.95;   // G (amplified: IR green channel)
              px[i+2] = lum * 0.15;   // B (minimal)
            }
            ctx.putImageData(imgData, 0, 0);
          } else {
            ctx.drawImage(v, 0, 0);
          }

          ws.send(hc.toDataURL('image/jpeg', 0.7));
          lastSend = time;
        }
      }
      animId = requestAnimationFrame(process);
    };
    animId = requestAnimationFrame(process);
    return () => cancelAnimationFrame(animId);
  }, [cameraAccess, mode, nightMode]);

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
      const conf = d.confidence;

      // Threat-level coloring: red for non-persons, amber for 'person' at night, blue for 'person' in day
      let color;
      if (!isPerson) color = '#ef4444';
      else if (nightMode) color = '#f59e0b';
      else color = '#3b82f6';

      // Outer glow
      ctx.shadowColor = color;
      ctx.shadowBlur = 12;
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, w, h);

      // Corner brackets (tactical style)
      ctx.shadowBlur = 0;
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2.5;
      const bLen = Math.min(22, w / 3, h / 3);
      // Top-left
      ctx.beginPath(); ctx.moveTo(x, y + bLen); ctx.lineTo(x, y); ctx.lineTo(x + bLen, y); ctx.stroke();
      // Top-right
      ctx.beginPath(); ctx.moveTo(x + w - bLen, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + bLen); ctx.stroke();
      // Bottom-left
      ctx.beginPath(); ctx.moveTo(x, y + h - bLen); ctx.lineTo(x, y + h); ctx.lineTo(x + bLen, y + h); ctx.stroke();
      // Bottom-right
      ctx.beginPath(); ctx.moveTo(x + w - bLen, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - bLen); ctx.stroke();

      // Label with confidence bar
      const labelText = `${d.label.toUpperCase()} ${(conf * 100).toFixed(0)}%`;
      ctx.font = 'bold 13px Inter, sans-serif';
      const tw = ctx.measureText(labelText).width + 14;
      const lh = 26;

      // Label background
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.92;
      ctx.beginPath();
      ctx.roundRect(x, y - lh - 4, tw, lh, [4, 4, 0, 0]);
      ctx.fill();

      // Confidence bar inside label
      const barW = tw - 4;
      ctx.fillStyle = 'rgba(0,0,0,0.3)';
      ctx.fillRect(x + 2, y - 6, barW, 3);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(x + 2, y - 6, barW * conf, 3);

      ctx.globalAlpha = 1;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(labelText, x + 7, y - 12);

      // Distance estimate line (center-bottom to bottom of frame)
      if (isPerson) {
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = 'rgba(255,255,255,0.2)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x + w / 2, y + h);
        ctx.lineTo(x + w / 2, c.height);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // Timestamp overlay
    ctx.font = '11px Inter, sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.6)';
    const ts = new Date().toLocaleTimeString('en-IN', { hour12: false });
    ctx.fillText(`${ts} IST | ${nightMode ? 'NIGHT VISION' : 'STANDARD'} | ${detections.length} OBJ`, 8, c.height - 8);
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

  const nightVideoStyle = nightMode ? {
    filter: 'brightness(1.6) contrast(1.4) saturate(0) sepia(1) hue-rotate(70deg)',
  } : {};

  return (
    <div className="animate-in">
      <div className="page-title">Intelligent Surveillance System</div>
      <div className="page-subtitle">YOLOv8 AI Detection • Night Vision Enhancement • Audio Anomaly Detection</div>

      {/* Mode Toggle + Night Vision Toggle */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, alignItems: 'center' }}>
        <button className="quick-action-btn"
          style={mode === 'live' ? { background: 'rgba(59,130,246,0.2)', borderColor: '#3b82f6' } : {}}
          onClick={() => setMode('live')}>
          <Video size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} /> Live Webcam
        </button>
        <button className="quick-action-btn"
          style={mode === 'upload' ? { background: 'rgba(59,130,246,0.2)', borderColor: '#3b82f6' } : {}}
          onClick={() => setMode('upload')}>
          <Upload size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} /> Upload Video
        </button>
        {mode === 'live' && (
          <button className="quick-action-btn"
            style={nightMode ? { background: 'rgba(16,185,129,0.2)', borderColor: '#10b981', color: '#34d399' } : {}}
            onClick={() => setNightMode(!nightMode)}>
            {nightMode ? <Sun size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} /> : <Moon size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} />}
            {nightMode ? 'Day Mode' : 'Night Vision'}
          </button>
        )}
      </div>

      {mode === 'live' ? (
        /* ─── LIVE WEBCAM MODE ─────────────────────────────── */
        <div className="surveillance-grid">
          <div className="video-feed-container" style={nightMode ? { border: '1px solid rgba(16,185,129,0.3)' } : {}}>
            <div className="feed-badge live" style={nightMode ? { background: 'rgba(16,185,129,0.9)' } : {}}>
              ● {nightMode ? 'NIGHT VISION AI' : 'LIVE AI'}
            </div>
            {cameraAccess === 'PENDING' && <CameraMsg color="#f59e0b">Requesting camera access...</CameraMsg>}
            {cameraAccess === 'DENIED' && <CameraMsg color="#ef4444">Camera access denied. Enable in browser settings.</CameraMsg>}
            <video ref={videoRef} autoPlay playsInline muted
              style={{
                display: cameraAccess === 'GRANTED' ? 'block' : 'none',
                width: '100%', height: '100%', objectFit: 'cover',
                ...nightVideoStyle,
              }} />
            <canvas ref={canvasRef} style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }} />
            <canvas ref={hiddenCanvasRef} style={{ display: 'none' }} />
            <div style={{ position: 'absolute', bottom: 12, left: 12, display: 'flex', gap: 8 }}>
              <span className="badge medium">Detections: {detectionCount}</span>
              <span className="badge low">AI FPS: {fps}</span>
              {nightMode && <span className="badge" style={{ background: 'rgba(16,185,129,0.15)', color: '#34d399', border: '1px solid rgba(16,185,129,0.3)' }}>🌙 IR ENHANCED</span>}
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div className="card" style={{ flex: '0 0 auto' }}>
              <div className="card-header">
                <span className="card-title"><Eye size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />Live Detections</span>
                <span className="badge medium">{detectionCount} objects</span>
              </div>
              <div style={{ maxHeight: 150, overflowY: 'auto' }}>
                {lastDetections.length === 0 ? (
                  <div style={{ color: '#64748b', fontSize: '0.78rem', padding: 8 }}>Point camera at objects for AI detection...</div>
                ) : lastDetections.map((d, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 8px', borderBottom: '1px solid rgba(148,163,184,0.08)', fontSize: '0.78rem' }}>
                    <span style={{ color: d.label === 'person' ? '#3b82f6' : '#ef4444', fontWeight: 700 }}>{d.label.toUpperCase()}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <div style={{ width: 40, height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 2, overflow: 'hidden' }}>
                        <div style={{ width: `${d.confidence * 100}%`, height: '100%', background: d.confidence > 0.8 ? '#10b981' : d.confidence > 0.5 ? '#f59e0b' : '#ef4444', borderRadius: 2 }} />
                      </div>
                      <span style={{ color: '#94a3b8', fontSize: '0.72rem', fontVariantNumeric: 'tabular-nums' }}>{(d.confidence * 100).toFixed(1)}%</span>
                    </div>
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
                  {uploading ? 'Analyzing video with YOLOv8 + Audio...' : 'Click to upload MP4, AVI, MOV'}
                </span>
                <span style={{ fontSize: '0.7rem', color: '#64748b', marginTop: 4 }}>
                  AI samples frames for visual detection + MoviePy for audio anomalies
                </span>
                <input type="file" accept="video/*" onChange={handleVideoUpload} disabled={uploading}
                  style={{ display: 'none' }} />
              </label>
              {uploading && (
                <div style={{ textAlign: 'center', marginTop: 12, color: '#3b82f6', fontSize: '0.82rem' }}>
                  Processing... YOLOv8 visual + MoviePy audio analysis ⏳
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
                Upload a video for combined visual + audio analysis.
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

                {/* Audio Analysis Section */}
                {uploadResult.audio_analysis && (
                  <div style={{ padding: 12, background: 'rgba(139,92,246,0.06)', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 8, marginBottom: 12 }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#a78bfa', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                      <Volume2 size={14} /> Audio Analysis (MoviePy)
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, fontSize: '0.74rem' }}>
                      <div><span style={{ color: '#64748b' }}>Avg Volume: </span><span style={{ fontWeight: 600 }}>{uploadResult.audio_analysis.avg_volume_db} dB</span></div>
                      <div><span style={{ color: '#64748b' }}>Peak Volume: </span><span style={{ fontWeight: 600 }}>{uploadResult.audio_analysis.peak_volume_db} dB</span></div>
                      <div><span style={{ color: '#64748b' }}>Anomalies: </span><span style={{ fontWeight: 600, color: uploadResult.audio_analysis.anomaly_count > 0 ? '#f59e0b' : '#10b981' }}>{uploadResult.audio_analysis.anomaly_count} detected</span></div>
                      <div><span style={{ color: '#64748b' }}>Has Audio: </span><span style={{ fontWeight: 600 }}>{uploadResult.audio_analysis.has_audio ? 'Yes' : 'No'}</span></div>
                    </div>
                    {uploadResult.audio_analysis.anomalies?.length > 0 && (
                      <div style={{ marginTop: 8 }}>
                        {uploadResult.audio_analysis.anomalies.map((a, i) => (
                          <div key={i} style={{ fontSize: '0.72rem', color: '#fbbf24', padding: '2px 0' }}>
                            ⚠ {a.type} at {a.timestamp}s — {a.description}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

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
                      <CheckCircle size={14} /> No visual threats detected
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
