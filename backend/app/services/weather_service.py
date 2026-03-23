import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Delhi weather patterns by month (simulated)
DELHI_WEATHER_PATTERNS = {
    1: {"temp_range": (5, 20), "humidity_range": (40, 70), "conditions": ["Fog", "Clear", "Haze"]},
    2: {"temp_range": (8, 25), "humidity_range": (35, 65), "conditions": ["Clear", "Haze", "Partly Cloudy"]},
    3: {"temp_range": (15, 33), "humidity_range": (25, 50), "conditions": ["Clear", "Partly Cloudy", "Dusty"]},
    4: {"temp_range": (22, 40), "humidity_range": (15, 35), "conditions": ["Clear", "Hot", "Dusty"]},
    5: {"temp_range": (28, 45), "humidity_range": (15, 30), "conditions": ["Hot", "Clear", "Dust Storm"]},
    6: {"temp_range": (30, 43), "humidity_range": (40, 70), "conditions": ["Hot", "Pre-Monsoon", "Thunderstorm"]},
    7: {"temp_range": (27, 38), "humidity_range": (60, 90), "conditions": ["Rain", "Heavy Rain", "Thunderstorm", "Cloudy"]},
    8: {"temp_range": (26, 36), "humidity_range": (65, 92), "conditions": ["Rain", "Heavy Rain", "Cloudy", "Humid"]},
    9: {"temp_range": (25, 35), "humidity_range": (55, 85), "conditions": ["Rain", "Partly Cloudy", "Clear"]},
    10: {"temp_range": (18, 33), "humidity_range": (30, 60), "conditions": ["Clear", "Haze", "Partly Cloudy"]},
    11: {"temp_range": (10, 28), "humidity_range": (35, 65), "conditions": ["Fog", "Clear", "Haze", "Smog"]},
    12: {"temp_range": (5, 22), "humidity_range": (45, 75), "conditions": ["Fog", "Cold", "Clear", "Haze"]},
}

WIND_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

class WeatherService:
    def __init__(self):
        self._last_weather = None
        self._base_temp = None
        self._trend = 0

    def get_current(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        month = now.month
        hour = now.hour
        pattern = DELHI_WEATHER_PATTERNS.get(month, DELHI_WEATHER_PATTERNS[3])

        t_min, t_max = pattern["temp_range"]
        # Diurnal variation: cooler at night, peak at 14:00
        diurnal = math.sin((hour - 6) * math.pi / 12) if 6 <= hour <= 18 else -0.3
        temp = t_min + (t_max - t_min) * (0.5 + 0.5 * diurnal) + random.uniform(-1.5, 1.5)
        temp = round(temp, 1)

        h_min, h_max = pattern["humidity_range"]
        humidity = round(random.uniform(h_min, h_max), 1)

        condition = random.choice(pattern["conditions"])
        wind_speed = round(random.uniform(2, 25), 1)
        wind_dir = random.choice(WIND_DIRECTIONS)

        # Visibility based on condition
        vis_map = {"Fog": 0.5, "Haze": 2, "Smog": 1.5, "Rain": 4, "Heavy Rain": 2,
                   "Dust Storm": 0.3, "Clear": 10, "Hot": 8, "Dusty": 3}
        visibility = vis_map.get(condition, 6) + random.uniform(-0.5, 0.5)

        rail_temp = round(temp + random.uniform(5, 15), 1)  # Rails absorb heat

        self._last_weather = {
            "timestamp": now.isoformat(),
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_direction": wind_dir,
            "visibility": round(max(0.1, visibility), 1),
            "condition": condition,
            "rail_temp": rail_temp,
            "pressure": round(random.uniform(1005, 1020), 1),
            "uv_index": round(max(0, diurnal * 8 + random.uniform(-1, 1)), 1),
        }
        return self._last_weather

    def get_forecast(self) -> List[Dict[str, Any]]:
        forecast = []
        now = datetime.utcnow()
        for h in range(1, 25):
            future = now + timedelta(hours=h)
            month = future.month
            pattern = DELHI_WEATHER_PATTERNS.get(month, DELHI_WEATHER_PATTERNS[3])
            t_min, t_max = pattern["temp_range"]
            diurnal = math.sin((future.hour - 6) * math.pi / 12) if 6 <= future.hour <= 18 else -0.3
            temp = round(t_min + (t_max - t_min) * (0.5 + 0.5 * diurnal) + random.uniform(-2, 2), 1)
            forecast.append({
                "hour": future.strftime("%H:00"),
                "temperature": temp,
                "condition": random.choice(pattern["conditions"]),
                "wind_speed": round(random.uniform(2, 20), 1),
                "humidity": round(random.uniform(*pattern["humidity_range"]), 1),
            })
        return forecast

    def get_rail_impact(self) -> Dict[str, Any]:
        w = self._last_weather or self.get_current()
        impacts = []
        risk_level = "LOW"
        score = 0

        if w["rail_temp"] > 55:
            impacts.append({"type": "THERMAL_EXPANSION", "severity": "HIGH",
                          "detail": f"Rail temp {w['rail_temp']}°C exceeds safe limit. Risk of rail buckling."})
            score += 35
        elif w["rail_temp"] > 45:
            impacts.append({"type": "THERMAL_STRESS", "severity": "MEDIUM",
                          "detail": f"Rail temp {w['rail_temp']}°C approaching stress threshold."})
            score += 15

        if w["visibility"] < 1:
            impacts.append({"type": "LOW_VISIBILITY", "severity": "HIGH",
                          "detail": f"Visibility {w['visibility']}km. Signal sighting distance compromised."})
            score += 25
        elif w["visibility"] < 3:
            impacts.append({"type": "REDUCED_VISIBILITY", "severity": "MEDIUM",
                          "detail": f"Visibility {w['visibility']}km. Enhanced vigilance required."})
            score += 10

        if w["condition"] in ["Heavy Rain", "Thunderstorm"]:
            impacts.append({"type": "FLOOD_RISK", "severity": "HIGH",
                          "detail": "Heavy precipitation. Monitor drainage and embankment stability."})
            score += 30
        elif w["condition"] == "Rain":
            impacts.append({"type": "WET_RAILS", "severity": "MEDIUM",
                          "detail": "Wet conditions. Braking distance increased by ~40%."})
            score += 10

        if w["wind_speed"] > 20:
            impacts.append({"type": "HIGH_WIND", "severity": "MEDIUM",
                          "detail": f"Wind {w['wind_speed']}km/h. OHE wire sway risk."})
            score += 15

        if not impacts:
            impacts.append({"type": "ALL_CLEAR", "severity": "LOW",
                          "detail": "No weather-related operational risks detected."})

        if score >= 40:
            risk_level = "HIGH"
        elif score >= 20:
            risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "risk_score": min(100, score),
            "impacts": impacts,
            "recommendation": self._get_recommendation(score),
            "weather": w,
        }

    def _get_recommendation(self, score):
        if score >= 40:
            return "IMPOSE SPEED RESTRICTIONS. Alert all section controllers. Deploy inspection trolley."
        elif score >= 20:
            return "Enhanced monitoring active. Patrol identified vulnerable sections."
        return "Normal operations. Continue routine monitoring."

weather_service = WeatherService()
