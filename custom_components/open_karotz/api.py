"""API module for Open Karotz integration."""
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import BASE_URL

if TYPE_CHECKING:
    from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)


class OpenKarotzAPI:
    """Class to interact with Open Karotz API."""

    def __init__(self, host: str, websession: ClientSession | None = None) -> None:
        """Initialize the API."""
        self._host = host
        self._websession = websession

    async def _async_get(self, endpoint: str) -> dict | None:
        """Perform GET request to Open Karotz."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}{endpoint}") as resp:
                content_type = resp.headers.get("Content-Type", "")
                if resp.status == 200:
                    if "application/json" in content_type:
                        return await resp.json()
                    text = await resp.text()
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        _LOGGER.error("Failed to parse JSON from %s: %s", endpoint, text[:200])
                        return None
                _LOGGER.error("Failed to fetch %s: %s", endpoint, resp.status)
                return None
        except Exception as err:
            _LOGGER.error("Error fetching %s: %s", endpoint, err)
            return None

    async def get_free_space(self) -> dict | None:
        """Get storage space information."""
        return await self._async_get("/cgi-bin/get_free_space")

    async def set_led_color(self, color: str) -> bool:
        """Set LED color."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/leds?color={color}") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error setting LED color: %s", err)
            return False

    async def set_ear_position(self, left: int, right: int) -> bool:
        """Set ear position."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/ears?left={left}&right={right}") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error setting ear position: %s", err)
            return False

    async def reset_ears(self) -> bool:
        """Reset ears to default position."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/ears_reset") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error resetting ears: %s", err)
            return False

    async def random_ears(self) -> bool:
        """Set ears to random position."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/ears_random") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error setting random ears: %s", err)
            return False

    async def play_sound(self, sound_id: str) -> bool:
        """Play local sound."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/sound?id={sound_id}") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error playing sound: %s", err)
            return False

    async def play_sound_url(self, url: str) -> bool:
        """Play sound from URL."""
        session = self._websession or async_get_clientsession(None)
        import urllib.parse
        encoded_url = urllib.parse.quote(url)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/sound?url={encoded_url}") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error playing URL: %s", err)
            return False

    async def play_tts(self, text: str, voice: str = "6") -> bool:
        """Play text-to-speech."""
        session = self._websession or async_get_clientsession(None)
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/tts?text={encoded_text}&voice={voice}") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error playing TTS: %s", err)
            return False

    async def play_mood(self, mood_id: int) -> bool:
        """Play mood."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/apps/moods?id={mood_id}") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error playing mood: %s", err)
            return False

    async def play_random_mood(self) -> bool:
        """Play random mood."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/apps/moods") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error playing random mood: %s", err)
            return False

    async def capture_snapshot(self) -> bytes | None:
        """Capture snapshot."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/snapshot?silent=1") as resp:
                if resp.status == 200:
                    content_type = resp.headers.get("Content-Type", "")
                    if "image" in content_type:
                        return await resp.read()
                    text = await resp.text()
                    try:
                        json_data = json.loads(text)
                        _LOGGER.error("Snapshot API returned JSON instead of image: %s", json_data)
                        return None
                    except json.JSONDecodeError:
                        _LOGGER.error("Snapshot API returned non-image content: %s", text[:100])
                        return None
                _LOGGER.error("Failed to capture snapshot: %s", resp.status)
                return None
        except Exception as err:
            _LOGGER.error("Error capturing snapshot: %s", err)
            return None

    async def sleep(self) -> bool:
        """Put Karotz to sleep."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/sleep") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error sleeping: %s", err)
            return False

    async def wake_up(self) -> bool:
        """Wake up Karotz."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/wake_up") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error waking up: %s", err)
            return False

    async def clear_cache(self) -> bool:
        """Clear cache."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/clear_cache") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error clearing cache: %s", err)
            return False

    async def get_rfid_list(self) -> dict | None:
        """Get RFID list."""
        return await self._async_get("/cgi-bin/rfid_list")

    async def stop(self) -> bool:
        """Stop playback."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/stop") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error stopping: %s", err)
            return False

    async def set_volume(self, volume: float) -> bool:
        """Set volume level."""
        session = self._websession or async_get_clientsession(None)
        try:
            # Volume is 0.0-1.0, convert to 0-100 for Karotz
            volume_percent = int(volume * 100)
            async with session.get(f"http://{self._host}/cgi-bin/volume?level={volume_percent}") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error setting volume: %s", err)
            return False

    async def set_mood(self, mood_id: int) -> bool:
        """Set mood."""
        session = self._websession or async_get_clientsession(None)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/apps/moods?id={mood_id}") as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error setting mood: %s", err)
            return False

    async def set_ear_position_single(self, position: int) -> bool:
        """Set ear position using a single position value (0-100)."""
        # Convert 0-100 position to 0-16 range
        ear_position = int(position * 16 / 100)
        return await self.set_ear_position(ear_position, ear_position)
