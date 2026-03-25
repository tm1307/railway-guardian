"""
Weather Service — Real-time via Open-Meteo API (100% FREE, no API key)
Falls back to Delhi-specific simulation if network is unavailable.
"""
import math
import random
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Delhi coordinates
DELHI_LAT = 28.6139
DELHI_LON = 77.2090

# WMO Weather Code → Condition mapping
WMO_CODES = {
    0: "Clear", 1: "Mostly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime Fog", 51: "Light Drizzle", 53: "Drizzle",
    55: "Heavy Drizzle", 61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
    71: "Light Snow", 73: "Snow", 75: "Heavy Snow", 77: "Snow Grains",
    80: "Light Showers", 81: "Showers", 82: "Heavy Showers",
    85: "Snow Showers", 86: "Heavy Snow Showers",
    95: "Thunderstorm", 96: "Thunderstorm with Hail", 99: "Heavy Thunderstorm",
}

# Fallback simulation data
DELHI_WEATHER_PATTERNS = {
    1: {"temp_range": (5, 20), "humidity_range": (40, 70), "conditions": ["Fog", "Clear", "Haze"]},
    2: {"temp_range": (8, 25), "humidity_range": (35, 65), "conditions": ["Clear", "Haze", "Partly Cloudy"]},
    3: {"temp_range": (15, 33), "humidity_range": (25, 50), "conditions": ["Clear", "Partly Cloudy", "Dusty"]},
    4: {"temp_range": (22, 40), "humidity_range": (15, 35), "conditions": ["Clear", "Hot", "Dusty"]},
    5: {"temp_range": (28, 45), "humidity_range": (15, 30), "conditions": ["Hot", "Clear", "Dust Storm"]},
    6: {"temp_range": (30, 43), "humidity_range": (40, 70), "conditions": ["Hot", "Pre-Monsoon", "Thunderstorm"]},
    7: {"temp_range": (27, 38), "humidity_range": (60, 90), "conditions": ["Rain", "Heavy Rain", "Thunderstorm"]},
    8: {"temp_range": (26, 36), "humidity_range": (65, 92), "conditions": ["Rain", "Heavy Rain", "Cloudy"]},
    9: {"temp_range": (25, 35), "humidity_range": (55, 85), "conditions": ["Rain", "Partly Cloudy", "Clear"]},
    10: {"temp_range": (18, 33), "humidity_range": (30, 60), "conditions": ["Clear", "Haze", "Partly Cloudy"]},
    11: {"temp_range": (10, 28), "humidity_range": (35, 65), "conditions": ["Fog", "Clear", "Haze", "Smog"]},
    12: {"temp_range": (5, 22), "humidity_range": (45, 75), "conditions": ["Fog", "Cold", "Clear", "Haze"]},
}

WIND_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


class WeatherService:
    def __init__(self):
        self._last_weather = None
        self._last_fetch_time = None
        self._cache_seconds = 120

    async def _fetch_from_open_meteo(self) -> Dict[str, Any]:
        """Fetch real weather from Open-Meteo (FREE, no API key needed)."""
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={DELHI_LAT}&longitude={DELHI_LON}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,"
            f"wind_direction_10m,weather_code,surface_pressure"
            f"&timezone=Asia/Kolkata"
        )
        timeout = aiohttp.ClientTimeout(total=5)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        current = data.get("current", {})

                        temp = current.get("temperature_2m", 30)
                        humidity = current.get("relative_humidity_2m", 50)
                        wind_speed = current.get("wind_speed_10m", 5)
                        wind_deg = current.get("wind_direction_10m", 0)
                        weather_code = current.get("weather_code", 0)
                        pressure = current.get("surface_pressure", 1013)

                        wind_dir = WIND_DIRECTIONS[int((wind_deg + 22.5) / 45) % 8]
                        condition = WMO_CODES.get(weather_code, "Clear")

                        # Rail temp = air temp + solar heating (higher in day)
                        hour = datetime.now().hour
                        solar_bonus = 10 if 10 <= hour <= 16 else 5
                        rail_temp = round(temp + solar_bonus, 1)

                        # Estimate visibility from weather code
                        if weather_code in (45, 48):
                            visibility = 0.5
                        elif weather_code >= 95:
                            visibility = 3
                        elif weather_code >= 61:
                            visibility = 5
                        elif weather_code >= 51:
                            visibility = 7
                        else:
                            visibility = 10

                        return {
                            "timestamp": datetime.utcnow().isoformat(),
                            "temperature": round(temp, 1),
                            "humidity": round(humidity, 1),
                            "wind_speed": round(wind_speed, 1),
                            "wind_direction": wind_dir,
                            "visibility": visibility,
                            "condition": condition,
                            "rail_temp": rail_temp,
                            "pressure": round(pressure, 1),
                            "uv_index": 0,
                            "source": "OPEN_METEO_LIVE",
                        }
                    else:
                        logger.warning(f"Open-Meteo returned {resp.status}")
                        return None
        except Exception as e:
            logger.warning(f"Open-Meteo error: {e}")
            return None

    def _generate_simulation(self) -> Dict[str, Any]:
        """Delhi-calibrated simulation fallback."""
        now = datetime.utcnow()
        month, hour = now.month, now.hour
        pattern = DELHI_WEATHER_PATTERNS.get(month, DELHI_WEATHER_PATTERNS[3])
        t_min, t_max = pattern["temp_range"]
        diurnal = math.sin((hour - 6) * math.pi / 12) if 6 <= hour <= 18 else -0.3
        temp = round(t_min + (t_max - t_min) * (0.5 + 0.5 * diurnal) + random.uniform(-1.5, 1.5), 1)
        h_min, h_max = pattern["humidity_range"]
        humidity = round(random.uniform(h_min, h_max), 1)
        condition = random.choice(pattern["conditions"])
        wind_speed = round(random.uniform(2, 25), 1)

        vis_map = {"Fog": 0.5, "Haze": 2, "Smog": 1.5, "Rain": 4, "Heavy Rain": 2,
                   "Dust Storm": 0.3, "Clear": 10, "Hot": 8, "Dusty": 3}
        visibility = round(max(0.1, vis_map.get(condition, 6) + random.uniform(-0.5, 0.5)), 1)
        rail_temp = round(temp + random.uniform(5, 15), 1)

        return {
            "timestamp": now.isoformat(),
            "temperature": temp, "humidity": humidity,
            "wind_speed": wind_speed, "wind_direction": random.choice(WIND_DIRECTIONS),
            "visibility": visibility, "condition": condition,
            "rail_temp": rail_temp,
            "pressure": round(random.uniform(1005, 1020), 1),
            "uv_index": round(max(0, diurnal * 8 + random.uniform(-1, 1)), 1),
            "source": "DELHI_SIMULATION",
        }

    async def get_current(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        if self._last_weather and self._last_fetch_time:
            if (now - self._last_fetch_time).total_seconds() < self._cache_seconds:
                return self._last_weather

        result = await self._fetch_from_open_meteo()
        if result:
            self._last_weather = result
            self._last_fetch_time = now
            return result

        self._last_weather = self._generate_simulation()
        self._last_fetch_time = now
        return self._last_weather

    def get_current_sync(self) -> Dict[str, Any]:
        if self._last_weather:
            return self._last_weather
        self._last_weather = self._generate_simulation()
        self._last_fetch_time = datetime.utcnow()
        return self._last_weather

    async def get_forecast(self) -> List[Dict[str, Any]]:
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={DELHI_LAT}&longitude={DELHI_LON}"
                f"&hourly=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m"
                f"&forecast_hours=24&timezone=Asia/Kolkata"
            )
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        hourly = data.get("hourly", {})
                        times = hourly.get("time", [])
                        temps = hourly.get("temperature_2m", [])
                        codes = hourly.get("weather_code", [])
                        winds = hourly.get("wind_speed_10m", [])
                        hums = hourly.get("relative_humidity_2m", [])
                        forecast = []
                        for i in range(min(24, len(times))):
                            forecast.append({
                                "hour": times[i][-5:] if times[i] else f"{i:02d}:00",
                                "temperature": round(temps[i], 1) if i < len(temps) else 30,
                                "condition": WMO_CODES.get(codes[i], "Clear") if i < len(codes) else "Clear",
                                "wind_speed": round(winds[i], 1) if i < len(winds) else 5,
                                "humidity": round(hums[i], 1) if i < len(hums) else 50,
                                "source": "OPEN_METEO_LIVE",
                            })
                        return forecast
        except Exception as e:
            logger.warning(f"Open-Meteo forecast error: {e}")

        # Fallback
        forecast = []
        now = datetime.utcnow()
        for h in range(1, 25):
            future = now + timedelta(hours=h)
            pattern = DELHI_WEATHER_PATTERNS.get(future.month, DELHI_WEATHER_PATTERNS[3])
            t_min, t_max = pattern["temp_range"]
            diurnal = math.sin((future.hour - 6) * math.pi / 12) if 6 <= future.hour <= 18 else -0.3
            temp = round(t_min + (t_max - t_min) * (0.5 + 0.5 * diurnal) + random.uniform(-2, 2), 1)
            forecast.append({
                "hour": future.strftime("%H:00"), "temperature": temp,
                "condition": random.choice(pattern["conditions"]),
                "wind_speed": round(random.uniform(2, 20), 1),
                "humidity": round(random.uniform(*pattern["humidity_range"]), 1),
                "source": "DELHI_SIMULATION",
            })
        return forecast

    async def get_rail_impact(self) -> Dict[str, Any]:
        w = self._last_weather or await self.get_current()
        impacts = []
        score = 0

        if w["rail_temp"] > 55:
            impacts.append({"type": "THERMAL_EXPANSION", "severity": "HIGH",
                          "detail": f"Rail temp {w['rail_temp']}°C exceeds safe limit (55°C). Risk of rail buckling per RDSO guidelines."})
            score += 35
        elif w["rail_temp"] > 45:
            impacts.append({"type": "THERMAL_STRESS", "severity": "MEDIUM",
                          "detail": f"Rail temp {w['rail_temp']}°C approaching RDSO stress threshold."})
            score += 15

        if w["visibility"] < 1:
            impacts.append({"type": "LOW_VISIBILITY", "severity": "HIGH",
                          "detail": f"Visibility {w['visibility']}km. Signal sighting distance compromised per GR 3.62."})
            score += 25
        elif w["visibility"] < 3:
            impacts.append({"type": "REDUCED_VISIBILITY", "severity": "MEDIUM",
                          "detail": f"Visibility {w['visibility']}km. Enhanced vigilance required."})
            score += 10

        if w["condition"] in ["Heavy Rain", "Thunderstorm", "Heavy Thunderstorm", "Heavy Showers"]:
            impacts.append({"type": "FLOOD_RISK", "severity": "HIGH",
                          "detail": "Heavy precipitation. Monitor drainage and embankment stability per IRPWM Para 812."})
            score += 30
        elif w["condition"] in ["Rain", "Light Rain", "Drizzle", "Showers"]:
            impacts.append({"type": "WET_RAILS", "severity": "MEDIUM",
                          "detail": "Wet conditions. Braking distance increased by ~40%."})
            score += 10

        if w["wind_speed"] > 20:
            impacts.append({"type": "HIGH_WIND", "severity": "MEDIUM",
                          "detail": f"Wind {w['wind_speed']}km/h. OHE wire sway risk per AC Traction Manual."})
            score += 15

        if not impacts:
            impacts.append({"type": "ALL_CLEAR", "severity": "LOW",
                          "detail": "No weather-related operational risks detected."})

        risk_level = "HIGH" if score >= 40 else "MEDIUM" if score >= 20 else "LOW"

        return {
            "risk_level": risk_level,
            "risk_score": min(100, score),
            "impacts": impacts,
            "recommendation": self._get_recommendation(score),
            "weather": w,
        }

    def _get_recommendation(self, score):
        if score >= 40:
            return "IMPOSE SPEED RESTRICTIONS per IRPWM. Alert all section controllers. Deploy inspection trolley."
        elif score >= 20:
            return "Enhanced monitoring active. Patrol identified vulnerable sections."
        return "Normal operations. Continue routine monitoring."


weather_service = WeatherService()
