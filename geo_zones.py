"""
Critical Infrastructure Protection Zones — Government-level restricted area monitoring.
Simulates GPS-based zone classification for sensitive railway infrastructure
such as bridges, tunnels, and defense-corridor stretches.

Aligned with:
  - Ministry of Railways Critical Infrastructure Protection Policy
  - NDMA (National Disaster Management Authority) vulnerability mapping
  - Defence corridor railway stretch monitoring requirements

Each zone type carries a different security clearance level and
automatically amplifies the risk score when threats are detected
in high-value infrastructure areas.
"""

import time

# ─── Zone Definitions ───────────────────────────────────────────────
# Modeled after actual Indian Railway critical infrastructure sections
ZONE_MAP = [
    {
        "id": "Z1",
        "name": "Standard Corridor",
        "type": "safe",
        "km_start": 0.0,
        "km_end": 3.5,
        "icon": "🟢",
        "risk_bonus": 0,
        "clearance": "General",
        "description": "Open track — standard monitoring protocol",
        "color": "#22c55e",
    },
    {
        "id": "Z2",
        "name": "Approach Zone — Bridge",
        "type": "buffer",
        "km_start": 3.5,
        "km_end": 5.0,
        "icon": "🟡",
        "risk_bonus": 10,
        "clearance": "Elevated",
        "description": "Approaching critical bridge infrastructure — heightened surveillance",
        "color": "#eab308",
    },
    {
        "id": "Z3",
        "name": "Critical — Yamuna Rail Bridge",
        "type": "restricted",
        "km_start": 5.0,
        "km_end": 7.5,
        "icon": "🔴",
        "risk_bonus": 20,
        "clearance": "Restricted / Defence",
        "description": "Critical bridge — maximum security, zero tolerance for unauthorized presence",
        "color": "#ef4444",
    },
    {
        "id": "Z4",
        "name": "Approach Zone — Exit",
        "type": "buffer",
        "km_start": 7.5,
        "km_end": 9.0,
        "icon": "🟡",
        "risk_bonus": 10,
        "clearance": "Elevated",
        "description": "Exiting critical infrastructure — surveillance active",
        "color": "#eab308",
    },
    {
        "id": "Z5",
        "name": "Standard Corridor",
        "type": "safe",
        "km_start": 9.0,
        "km_end": 12.0,
        "icon": "🟢",
        "risk_bonus": 0,
        "clearance": "General",
        "description": "Open track — standard monitoring protocol",
        "color": "#22c55e",
    },
]

TOTAL_KM = 12.0
SPEED_KM_PER_SEC = 0.05  # Simulated patrol speed

_start_time = None


def _get_elapsed():
    global _start_time
    if _start_time is None:
        _start_time = time.time()
    return time.time() - _start_time


def get_current_position():
    """
    Get simulated GPS position along the track (km marker).
    Cycles continuously to simulate patrol movement.
    """
    elapsed = _get_elapsed()
    distance = (elapsed * SPEED_KM_PER_SEC) % TOTAL_KM
    return round(distance, 2)


def get_current_zone():
    """
    Returns the active infrastructure zone based on GPS position.
    Includes clearance level and risk amplification bonus.
    """
    pos = get_current_position()

    for zone in ZONE_MAP:
        if zone["km_start"] <= pos < zone["km_end"]:
            return {
                **zone,
                "current_km": pos,
                "progress": (pos - zone["km_start"]) / (zone["km_end"] - zone["km_start"]),
            }

    return {**ZONE_MAP[0], "current_km": pos, "progress": 0.0}


def get_zone_risk_bonus():
    """Return the risk score bonus for the current zone."""
    zone = get_current_zone()
    return zone.get("risk_bonus", 0)


def get_zone_map_data():
    """
    Return zone map data for infrastructure visualization.
    Includes current position indicator for patrol tracking.
    """
    pos = get_current_position()
    return {
        "zones": ZONE_MAP,
        "current_km": pos,
        "total_km": TOTAL_KM,
    }


def reset():
    """Reset the GPS simulation timer."""
    global _start_time
    _start_time = time.time()
