import aiohttp
import asyncio
import logging

class PhyphoxService:
    def __init__(self):
        self.base_url = None
        self.is_connected = False
        self.last_data = {"linear_acceleration_x": 0.0, "linear_acceleration_y": 0.0, "linear_acceleration_z": 0.0}

    async def connect(self, ip_address: str):
        self.base_url = f"http://{ip_address}/get?"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}accX&accY&accZ") as resp:
                    if resp.status == 200:
                        self.is_connected = True
                        return True
        except Exception as e:
            logging.error(f"Phyphox connection error: {e}")
        self.is_connected = False
        return False

    async def fetch_data(self):
        if not self.is_connected or not self.base_url:
            return self.last_data

        try:
            # Phyphox buffers data, we take the latest
            async with aiohttp.ClientSession() as session:
                # Assuming the user has a "Linear Acceleration" or "Accelerometer" experiment open
                async with session.get(f"{self.base_url}accX&accY&accZ") as resp:
                    data = await resp.json()
                    # Example format: {"buffer": {"accX": {"value": [0.1]}, ...}}
                    if "buffer" in data:
                        self.last_data = {
                            "x": data["buffer"].get("accX", {}).get("value", [0.0])[-1],
                            "y": data["buffer"].get("accY", {}).get("value", [0.0])[-1],
                            "z": data["buffer"].get("accZ", {}).get("value", [0.0])[-1],
                        }
                    return self.last_data
        except Exception as e:
            logging.error(f"Phyphox fetch error: {e}")
            return self.last_data

phyphox_service = PhyphoxService()
