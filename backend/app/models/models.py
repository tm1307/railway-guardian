from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String)  # admin, operator, viewer
    is_active = Column(Boolean, default=True)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    node_id = Column(String, index=True)
    alert_type = Column(String)
    severity = Column(String)
    risk_score = Column(Float)
    vibration_level = Column(Float)
    detections = Column(String)
    explanation = Column(String)
    evidence_path = Column(String)
    evidence_hash = Column(String)
    gps_km = Column(Float)
    is_verified = Column(Boolean, default=False)
    maintenance_status = Column(String)
    confidence_score = Column(Float)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = Column(String)
    action = Column(String)
    details = Column(String)
    ip_address = Column(String)

class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedules"
    id = Column(Integer, primary_key=True, index=True)
    section = Column(String)
    task = Column(String)
    team = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)

class EdgeNode(Base):
    __tablename__ = "edge_nodes"
    id = Column(String, primary_key=True, index=True)
    location_name = Column(String)
    km_marker = Column(Float)
    status = Column(String)
    last_seen = Column(DateTime)
    capabilities = Column(JSON)

# ─── New Models ──────────────────────────────────────────────────────

class WeatherData(Base):
    __tablename__ = "weather_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    temperature = Column(Float)       # Celsius
    humidity = Column(Float)          # %
    wind_speed = Column(Float)        # km/h
    wind_direction = Column(String)
    visibility = Column(Float)        # km
    condition = Column(String)        # Clear, Fog, Rain, Storm
    rail_temp = Column(Float)         # Rail surface temp
    pressure = Column(Float)          # hPa
    uv_index = Column(Float)

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    node_id = Column(String, index=True)
    sensor_type = Column(String)      # vibration, temperature, strain, acoustic
    value = Column(Float)
    unit = Column(String)
    status = Column(String)           # normal, warning, critical

class InfrastructureAsset(Base):
    __tablename__ = "infrastructure_assets"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String, unique=True, index=True)
    name = Column(String)
    asset_type = Column(String)       # track, signal, bridge, switch, station
    location = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    km_marker = Column(Float)
    health_score = Column(Float)      # 0-100
    last_inspection = Column(DateTime)
    next_maintenance = Column(DateTime)
    status = Column(String)           # operational, degraded, critical, offline
    notes = Column(Text)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = Column(String)
    message = Column(Text)
    response = Column(Text)
    category = Column(String)

class RiskZone(Base):
    __tablename__ = "risk_zones"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(String, unique=True, index=True)
    name = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    radius = Column(Float)            # meters
    risk_score = Column(Float)        # 0-100
    factors = Column(JSON)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class IntentPrediction(Base):
    __tablename__ = "intent_predictions"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    zone_id = Column(String, index=True)
    zone_name = Column(String)
    predicted_threat = Column(String)  # tampering, theft, vandalism, safe
    confidence = Column(Float)         # 0-1
    time_window = Column(String)       # 1h, 3h, 6h
    reasoning = Column(Text)
    factors = Column(JSON)
    recommended_action = Column(String)
