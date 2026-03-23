from fastapi import WebSocket, WebSocketDisconnect
import json
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        self.channels: Dict[str, List[WebSocket]] = {
            "alerts": [],
            "sensors": [],
            "weather": [],
            "general": [],
        }

    async def connect(self, websocket: WebSocket, channel: str = "general"):
        await websocket.accept()
        if channel not in self.channels:
            self.channels[channel] = []
        self.channels[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "general"):
        if channel in self.channels and websocket in self.channels[channel]:
            self.channels[channel].remove(websocket)

    async def broadcast(self, message: str, channel: str = "general"):
        if channel in self.channels:
            dead = []
            for connection in self.channels[channel]:
                try:
                    await connection.send_text(message)
                except Exception:
                    dead.append(connection)
            for d in dead:
                self.channels[channel].remove(d)

    async def broadcast_json(self, data: dict, channel: str = "general"):
        await self.broadcast(json.dumps(data), channel)

manager = ConnectionManager()

async def send_alert(alert_data: dict):
    await manager.broadcast_json(alert_data, "alerts")
    await manager.broadcast_json({"type": "alert", **alert_data}, "general")

async def send_sensor_update(sensor_data: dict):
    await manager.broadcast_json(sensor_data, "sensors")

async def send_weather_update(weather_data: dict):
    await manager.broadcast_json(weather_data, "weather")
