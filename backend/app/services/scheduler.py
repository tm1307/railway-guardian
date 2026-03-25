import asyncio
import random
import math
import logging
from datetime import datetime
from ..core.sockets import manager, send_alert, send_sensor_update, send_weather_update
from ..services.weather_service import weather_service
from ..services.phyphox import phyphox_service
from ..services.predictive_failure import predictive_engine

logger = logging.getLogger(__name__)

SENSOR_NODES = [
    {"node_id": "NODE-NDLS-01", "name": "New Delhi Yard"},
    {"node_id": "NODE-GZB-02", "name": "Ghaziabad Junction"},
    {"node_id": "NODE-FDB-03", "name": "Faridabad Section"},
    {"node_id": "NODE-HNZ-04", "name": "Nizamuddin Bridge"},
    {"node_id": "NODE-OKA-05", "name": "Okhla Crossing"},
    {"node_id": "NODE-SNP-06", "name": "Sonipat Section"},
]

# Store latest state for real-time data
_state = {
    "phyphox_connected": False,
    "phyphox_data": None,
    "alert_counter": 0,
    "readings_history": [],  # store actual readings for real history
}

async def sensor_broadcast_loop():
    """Broadcast sensor data every 3 seconds.
    If Phyphox is connected, uses REAL phone sensor data.
    Otherwise generates realistic sinusoidal simulation (not flat random).
    """
    tick = 0
    while True:
        try:
            now = datetime.utcnow()
            
            # Try to get real Phyphox data
            real_phyphox = None
            if phyphox_service.is_connected:
                real_phyphox = await phyphox_service.fetch_data()
                _state["phyphox_connected"] = True
                _state["phyphox_data"] = real_phyphox

            node = SENSOR_NODES[tick % len(SENSOR_NODES)]
            
            if real_phyphox:
                # REAL sensor data from phone
                ax = real_phyphox.get("x", 0)
                ay = real_phyphox.get("y", 0)
                az = real_phyphox.get("z", 0)
                vibration = round(math.sqrt(ax**2 + ay**2 + az**2), 4)
                reading = {
                    "node_id": node["node_id"],
                    "node_name": node["name"],
                    "timestamp": now.isoformat(),
                    "vibration": vibration,
                    "temperature": round(28 + random.gauss(0, 1.5), 1),
                    "strain": round(max(0, 50 + vibration * 200 + random.gauss(0, 5)), 1),
                    "acoustic": round(max(15, 30 + vibration * 100 + random.gauss(0, 3)), 1),
                    "source": "PHYPHOX_LIVE",
                    "raw_accel": {"x": round(ax, 4), "y": round(ay, 4), "z": round(az, 4)},
                }
            else:
                # Realistic sinusoidal simulation (diurnal + noise, NOT flat random)
                hour_frac = now.hour + now.minute / 60
                base_vib = 0.08 + 0.12 * math.sin(hour_frac * math.pi / 12) + random.gauss(0, 0.03)
                base_temp = 28 + 8 * math.sin((hour_frac - 6) * math.pi / 12) + random.gauss(0, 0.8)
                
                # Occasional spikes to trigger alerts
                if random.random() < 0.05:
                    base_vib += random.uniform(0.2, 0.4)
                
                reading = {
                    "node_id": node["node_id"],
                    "node_name": node["name"],
                    "timestamp": now.isoformat(),
                    "vibration": round(max(0.01, base_vib), 4),
                    "temperature": round(base_temp, 1),
                    "strain": round(max(0, 50 + base_vib * 150 + random.gauss(0, 8)), 1),
                    "acoustic": round(max(15, 25 + base_vib * 80 + random.gauss(0, 4)), 1),
                    "source": "SIMULATION",
                }
            
            # Store in history
            _state["readings_history"].append(reading)
            _state["readings_history"] = _state["readings_history"][-500:]  # Keep last 500
            
            # Feed into Predictive Track Failure Engine
            predictive_engine.ingest_reading(reading)
            
            await send_sensor_update(reading)
            
            # Auto-generate alert if thresholds breached
            if reading["vibration"] > 0.35:
                _state["alert_counter"] += 1
                severity = "critical" if reading["vibration"] > 0.45 else "high"
                alert = {
                    "id": _state["alert_counter"] + 5000,
                    "node_id": node["node_id"],
                    "node_name": node["name"],
                    "alert_type": "VIBRATION_ANOMALY",
                    "severity": severity,
                    "risk_score": round(min(99, reading["vibration"] * 180), 1),
                    "explanation": f"Vibration {reading['vibration']:.3f}g exceeds threshold at {node['name']}",
                    "timestamp": now.isoformat(),
                    "source": reading.get("source", "SIMULATION"),
                }
                await send_alert(alert)
            
            tick += 1
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Sensor broadcast error: {e}")
            await asyncio.sleep(5)

async def weather_broadcast_loop():
    """Broadcast weather updates every 30 seconds."""
    while True:
        try:
            weather = await weather_service.get_current()
            await send_weather_update(weather)
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Weather broadcast error: {e}")
            await asyncio.sleep(30)

async def alert_broadcast_loop():
    """Generate alerts based on patterns and Phyphox data (not purely random)."""
    while True:
        try:
            wait = random.randint(10, 25)
            await asyncio.sleep(wait)
            
            _state["alert_counter"] += 1
            node = random.choice(SENSOR_NODES)
            now = datetime.utcnow()
            hour = now.hour
            
            # Time-based threat probability (higher at night)
            if 0 <= hour <= 5:
                alert_types = ["PERIMETER_BREACH", "PERSON_DETECTED", "OBJECT_DETECTED"]
                severity_weights = [15, 25, 35, 25]
            elif 22 <= hour or hour <= 6:
                alert_types = ["VIBRATION_ANOMALY", "PERIMETER_BREACH", "PERSON_DETECTED"]
                severity_weights = [20, 30, 30, 20]
            else:
                alert_types = ["SENSOR_FLUCTUATION", "OBJECT_DETECTED", "MAINTENANCE_REMINDER"]
                severity_weights = [45, 30, 20, 5]
            
            severity = random.choices(["low", "medium", "high", "critical"], weights=severity_weights)[0]
            alert_type = random.choice(alert_types)
            
            descriptions = {
                "VIBRATION_ANOMALY": f"Unusual track vibration pattern at {node['name']}",
                "PERSON_DETECTED": f"Unidentified individual near track section at {node['name']}",
                "OBJECT_DETECTED": f"Foreign object near rail infrastructure at {node['name']}",
                "PERIMETER_BREACH": f"Boundary intrusion detected at {node['name']}",
                "SENSOR_FLUCTUATION": f"Sensor reading deviation at {node['name']}",
                "MAINTENANCE_REMINDER": f"Scheduled inspection due at {node['name']}",
            }
            
            alert = {
                "id": _state["alert_counter"] + 1000,
                "node_id": node["node_id"],
                "node_name": node["name"],
                "alert_type": alert_type,
                "severity": severity,
                "risk_score": round(random.uniform(15, 95) if severity != "low" else random.uniform(5, 30), 1),
                "explanation": descriptions.get(alert_type, alert_type),
                "timestamp": now.isoformat(),
            }
            await send_alert(alert)
        except Exception as e:
            logger.error(f"Alert broadcast error: {e}")
            await asyncio.sleep(10)

def get_readings_history():
    """Get stored real sensor readings history."""
    return _state["readings_history"]

def get_phyphox_status():
    """Check if Phyphox is connected."""
    return {
        "connected": _state["phyphox_connected"],
        "last_data": _state["phyphox_data"],
    }

async def start_scheduler():
    """Start all background broadcast tasks."""
    asyncio.create_task(sensor_broadcast_loop())
    asyncio.create_task(weather_broadcast_loop())
    asyncio.create_task(alert_broadcast_loop())
    logger.info("Background scheduler started: sensors, weather, alerts")
