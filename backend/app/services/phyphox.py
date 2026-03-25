"""
Phyphox Phone Sensor Integration Service
Connects to a real smartphone running Phyphox app via its HTTP REST API.
Reads raw accelerometer data (X, Y, Z) for vibration analysis.
"""
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)


class PhyphoxService:
    def __init__(self):
        self.base_url = None
        self.is_connected = False
        self.last_data = {"x": 0.0, "y": 0.0, "z": 0.0}

    async def connect(self, ip_address: str):
        """Attempt to connect to a Phyphox instance.
        Accepts formats: 192.168.1.58, 192.168.1.58:8080, http://192.168.1.58
        """
        clean_ip = ip_address.replace("http://", "").replace("https://", "").strip().rstrip("/")
        # Fix common typo where user types a space instead of a colon for the port
        clean_ip = clean_ip.replace(" ", ":")
        
        self.base_url = f"http://{clean_ip}"

        test_url = f"{self.base_url}/get?accX&accY&accZ"
        timeout = aiohttp.ClientTimeout(total=8)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        # Verify it's a valid Phyphox response
                        if "buffer" in data or "status" in data:
                            self.is_connected = True
                            logger.info(f"Phyphox connected at {self.base_url}")
                            return True, "Connected successfully"
                        return False, f"Unexpected response format: {list(data.keys())}"
                    return False, f"HTTP {resp.status}"
        except asyncio.TimeoutError:
            self.is_connected = False
            return False, "Connection timed out after 8s"
        except aiohttp.ClientConnectorError as e:
            self.is_connected = False
            return False, f"Cannot reach {clean_ip}: {e}"
        except Exception as e:
            logger.error(f"Phyphox connection error: {e}")
            self.is_connected = False
            return False, f"{type(e).__name__}: {e}"

    async def fetch_data(self):
        """Fetch latest accelerometer reading from the connected phone."""
        if not self.is_connected or not self.base_url:
            return self.last_data

        timeout = aiohttp.ClientTimeout(total=3)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/get?accX&accY&accZ") as resp:
                    data = await resp.json(content_type=None)
                    buf = data.get("buffer", {})

                    # Phyphox response format: {"buffer": {"accX": {"buffer": [...], ...}}}
                    def extract(key):
                        entry = buf.get(key, {})
                        # Handle both "buffer" and "value" keys (varies by Phyphox version)
                        vals = entry.get("buffer", entry.get("value", [0.0]))
                        return vals[-1] if vals else 0.0

                    self.last_data = {
                        "x": round(extract("accX"), 6),
                        "y": round(extract("accY"), 6),
                        "z": round(extract("accZ"), 6),
                    }
                    return self.last_data
        except Exception as e:
            logger.warning(f"Phyphox fetch error: {e}")
            self.is_connected = False
            return self.last_data


phyphox_service = PhyphoxService()
