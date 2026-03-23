import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

ASSET_TYPES = ["track", "signal", "bridge", "switch", "station", "crossing", "ohe", "relay_room"]

DELHI_ASSETS = [
    {"asset_id": "TRK-NDLS-001", "name": "Track Section NDLS-GZB Mainline", "asset_type": "track", "location": "New Delhi - Ghaziabad", "lat": 28.6425, "lng": 77.2195, "km_marker": 0.0},
    {"asset_id": "SIG-NDLS-001", "name": "Signal Post #14 NDLS Yard", "asset_type": "signal", "location": "New Delhi Station", "lat": 28.6430, "lng": 77.2200, "km_marker": 0.5},
    {"asset_id": "BRG-YMN-001", "name": "Yamuna Rail Bridge (Old)", "asset_type": "bridge", "location": "Delhi-Ghaziabad", "lat": 28.6550, "lng": 77.2450, "km_marker": 3.2},
    {"asset_id": "SWT-TKJ-001", "name": "Tilak Bridge Junction Switch", "asset_type": "switch", "location": "Tilak Bridge", "lat": 28.6355, "lng": 77.2434, "km_marker": 2.1},
    {"asset_id": "STN-HNZ-001", "name": "Hazrat Nizamuddin Station", "asset_type": "station", "location": "Nizamuddin", "lat": 28.5878, "lng": 77.2508, "km_marker": 5.0},
    {"asset_id": "XNG-OKA-001", "name": "Okhla Level Crossing #7", "asset_type": "crossing", "location": "Okhla", "lat": 28.5310, "lng": 77.2710, "km_marker": 8.5},
    {"asset_id": "OHE-FDB-001", "name": "OHE Mast Section Faridabad", "asset_type": "ohe", "location": "Faridabad", "lat": 28.4089, "lng": 77.3178, "km_marker": 15.0},
    {"asset_id": "RLY-GZB-001", "name": "Relay Room Ghaziabad Jn", "asset_type": "relay_room", "location": "Ghaziabad", "lat": 28.6706, "lng": 77.4381, "km_marker": 20.0},
    {"asset_id": "TRK-SNP-001", "name": "Track Section Sonipat Mainline", "asset_type": "track", "location": "Sonipat", "lat": 28.9951, "lng": 77.0200, "km_marker": 40.0},
    {"asset_id": "BRG-PNP-001", "name": "Panipat Canal Bridge", "asset_type": "bridge", "location": "Panipat", "lat": 29.3872, "lng": 76.9682, "km_marker": 80.0},
    {"asset_id": "SIG-DSS-001", "name": "Signal Post #3 Sarai Rohilla", "asset_type": "signal", "location": "Sarai Rohilla", "lat": 28.6607, "lng": 77.1756, "km_marker": 4.0},
    {"asset_id": "SWT-ANV-001", "name": "Anand Vihar Yard Switch #2", "asset_type": "switch", "location": "Anand Vihar", "lat": 28.6461, "lng": 77.3152, "km_marker": 12.0},
]

class InfrastructureService:
    def get_assets(self) -> List[Dict[str, Any]]:
        assets = []
        now = datetime.utcnow()
        for a in DELHI_ASSETS:
            health = round(random.uniform(45, 99), 1)
            days_since = random.randint(5, 90)
            days_until = random.randint(1, 60)
            
            if health > 80:
                status = "operational"
            elif health > 60:
                status = "degraded"
            elif health > 40:
                status = "critical"
            else:
                status = "offline"
            
            assets.append({
                **a,
                "health_score": health,
                "status": status,
                "last_inspection": (now - timedelta(days=days_since)).isoformat(),
                "next_maintenance": (now + timedelta(days=days_until)).isoformat(),
                "notes": self._generate_notes(a["asset_type"], health),
            })
        return assets

    def get_recommendations(self) -> List[Dict[str, Any]]:
        assets = self.get_assets()
        recs = []
        for a in assets:
            if a["health_score"] < 70:
                priority = "URGENT" if a["health_score"] < 50 else "HIGH"
                recs.append({
                    "asset_id": a["asset_id"],
                    "asset_name": a["name"],
                    "asset_type": a["asset_type"],
                    "health_score": a["health_score"],
                    "priority": priority,
                    "recommendation": self._generate_recommendation(a),
                    "estimated_hours": random.randint(2, 24),
                    "team_required": self._get_team(a["asset_type"]),
                })
        return sorted(recs, key=lambda x: x["health_score"])

    def _generate_notes(self, asset_type, health):
        notes_map = {
            "track": "Rail condition under monitoring. UTR inspection pending." if health < 70 else "Track in good condition.",
            "signal": "Signal calibration required." if health < 70 else "Signal functioning normally.",
            "bridge": "Structural monitoring active. Next underwater inspection due." if health < 70 else "Bridge integrity verified.",
            "switch": "Point machine oil levels to be checked." if health < 70 else "Switch mechanism operating smoothly.",
            "station": "Platform edge maintenance needed." if health < 70 else "Station infrastructure adequate.",
            "crossing": "Boom barrier motor service due." if health < 70 else "Level crossing equipment functional.",
            "ohe": "Catenary wire tension check overdue." if health < 70 else "OHE parameters within tolerance.",
            "relay_room": "Equipment cooling system needs servicing." if health < 70 else "Relay room operating normally.",
        }
        return notes_map.get(asset_type, "No notes.")

    def _generate_recommendation(self, asset):
        rec_map = {
            "track": f"Schedule ultrasonic rail testing for {asset['location']}. Check for internal rail defects.",
            "signal": f"Calibrate signal aspects and verify LED integrity at {asset['location']}.",
            "bridge": f"Conduct load test and pier inspection for {asset['name']}.",
            "switch": f"Replace point machine lubricant and test switch operation at {asset['location']}.",
            "station": f"Repair platform edge tiles and drainage at {asset['location']}.",
            "crossing": f"Service boom barrier motor and update electronics at {asset['name']}.",
            "ohe": f"Re-tension catenary wire and inspect droppers in {asset['location']} section.",
            "relay_room": f"Service HVAC and test battery backup at {asset['name']}.",
        }
        return rec_map.get(asset["asset_type"], f"General inspection recommended for {asset['name']}.")

    def _get_team(self, asset_type):
        teams = {
            "track": "P-Way Gang", "signal": "S&T Team", "bridge": "Bridge Unit",
            "switch": "S&T Team", "station": "Engg. Dept", "crossing": "S&T Team",
            "ohe": "OHE Team", "relay_room": "S&T Team",
        }
        return teams.get(asset_type, "Engineering")

infrastructure_service = InfrastructureService()
