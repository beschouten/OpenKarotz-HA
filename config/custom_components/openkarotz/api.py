"""OpenKarotz API Client."""

import asyncio
import json
import logging
import time
from typing import Any, Callable, Dict, Optional
from urllib.parse import urljoin

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_RECONNECT_ATTEMPTS,
    DEFAULT_RECONNECT_DELAY,
)

_LOGGER = logging.getLogger(__name__)


class OpenKarotzAPIError(HomeAssistantError):
    """Base exception for OpenKarotz API errors."""

    pass


class OpenKarotzConnectionError(OpenKarotzAPIError):
    """Connection error occurred."""

    pass


class OpenKarotzAuthenticationError(OpenKarotzAPIError):
    """Authentication failed."""

    pass


class OpenKarotzAPI:
    """OpenKarotz API client for device communication."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Initialize OpenKarotz API client."""
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.session: Optional[aiohttp.ClientSession] = None
        self._is_connected = False

    async def async_connect(self) -> bool:
        """Establish connection to OpenKarotz device."""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

            try:
                await self._async_request("GET", "/api", skip_connection_check=True)
            except Exception as e:
                _LOGGER.error(f"Failed to connect to OpenKarotz: {e}")
                await self.async_disconnect()
                return False

            _LOGGER.info(f"Successfully connected to OpenKarotz at {self.base_url}")
            self._is_connected = True
            return True

        except Exception as e:
            _LOGGER.error(f"Connection error: {e}")
            return False

    async def async_disconnect(self) -> None:
        """Disconnect from OpenKarotz device."""
        if self.session:
            await self.session.close()
            self.session = None

        self._is_connected = False
        _LOGGER.info("Disconnected from OpenKarotz")

    async def _async_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
params: Optional[Dict[str, Any]] = None,
         skip_connection_check: bool = False,
     ) -> Dict[str, Any]:
        """Make HTTP request to OpenKarotz API.

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint
            data: Request body data
            params: URL parameters

        Returns:
            API response as dictionary

        Raises:
            OpenKarotzAPIError: On API errors
            OpenKarotzConnectionError: On connection errors
        """
        if not skip_connection_check and (not self._is_connected or not self.session):
            raise OpenKarotzConnectionError("Not connected to OpenKarotz")

        url = urljoin(self.base_url, endpoint)

        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
            ) as response:
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            _LOGGER.error(f"API request error: {e}")
            raise OpenKarotzConnectionError(f"API request failed: {e}")

        except json.JSONDecodeError as e:
            _LOGGER.error(f"Invalid JSON response: {e}")
            raise OpenKarotzAPIError(f"Invalid response format: {e}")

        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                raise OpenKarotzAuthenticationError("Authentication failed")
            raise OpenKarotzAPIError(f"API error: {e.status}")

    async def get_info(self) -> Dict[str, Any]:
        """Get device information.

        Returns:
            Dictionary with device information
        """
        return await self._async_request("GET", "/api", skip_connection_check=True)

    async def get_state(self) -> Dict[str, Any]:
        """Get device state.

        Returns:
            Dictionary with device state
        """
        return await self._async_request("GET", "/state")

    async def get_leds(self) -> Dict[str, Any]:
        """Get LED information and state.

        Returns:
            Dictionary with LED information
        """
        return await self._async_request("GET", "/leds")

    async def set_led(
        self,
        color: Optional[str] = None,
        brightness: Optional[int] = None,
        color_temperature: Optional[int] = None,
        preset: Optional[str] = None,
        rgb_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Set LED configuration.

        Args:
            color: Color name (e.g., "red", "blue")
            brightness: Brightness level (0-100)
            color_temperature: Color temperature in Kelvin
            preset: Preset color scheme name
            rgb_value: RGB color value (e.g., "FF0000")

        Returns:
            API response
        """
        data = {}
        if color is not None:
            data["color"] = color
        if brightness is not None:
            data["brightness"] = brightness
        if color_temperature is not None:
            data["color_temperature"] = color_temperature
        if preset is not None:
            data["preset"] = preset
        if rgb_value is not None:
            data["rgb_value"] = rgb_value

        return await self._async_request("POST", "/leds", data)

    async def get_ears(self) -> Dict[str, Any]:
        """Get audio player information and state.

        Returns:
            Dictionary with audio player information
        """
        return await self._async_request("GET", "/ears")

    async def set_volume(self, volume: int) -> Dict[str, Any]:
        """Set audio player volume.

        Args:
            volume: Volume level (0-100)

        Returns:
            API response
        """
        return await self._async_request("POST", "/ears", {"volume": volume})

    async def play_audio(
        self,
        source: str,
        category: Optional[str] = None,
        volume: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Play audio from specified source.

        Args:
            source: Audio source identifier
            category: Audio category (e.g., "alarm", "notification")
            volume: Audio volume (0-100)

        Returns:
            API response
        """
        data = {"source": source}
        if category is not None:
            data["category"] = category
        if volume is not None:
            data["volume"] = volume

        return await self._async_request("POST", "/ears", data)

    async def stop_audio(self, source: Optional[str] = None) -> Dict[str, Any]:
        """Stop playing audio.

        Args:
            source: Audio source to stop (optional)

        Returns:
            API response
        """
        data = {}
        if source is not None:
            data["source"] = source

        return await self._async_request("POST", "/ears", data)

    async def get_rfid(self) -> Dict[str, Any]:
        """Get RFID information and state.

        Returns:
            Dictionary with RFID information
        """
        return await self._async_request("GET", "/rfid")

    async def get_tts(self) -> Dict[str, Any]:
        """Get TTS information and state.

        Returns:
            Dictionary with TTS information
        """
        return await self._async_request("GET", "/tts")

    async def play_tts(
        self,
        text: str,
        voice: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Play text-to-speech.

        Args:
            text: Text to speak
            voice: Voice identifier
            category: TTS category (e.g., "notification")

        Returns:
            API response
        """
     
        data = {"text": text}
        if voice is not None:
            data["voice"] = voice
        if category is not None:
            data["category"] = category

        return await self._async_request("POST", "/tts", data)

    async def move_ears(self, left: int, right: int) -> Dict[str, Any]:
        """Move ears to specified positions.

        Args:
            left: Left ear position (0-180 degrees)
            right: Right ear position (0-180 degrees)

        Returns:
            API response
        """
        return await self._async_request("POST", "/ears", {"left": left, "right": right})

    async def ears_mode(self, mode: str) -> Dict[str, Any]:
        """Set ear mode.

        Args:
            mode: Ear mode ("disabled", "random")

        Returns:
            API response
        """
        return await self._async_request("POST", "/ears", {"mode": mode})

    async def ears_reset(self) -> Dict[str, Any]:
        """Reset ears to center position.

        Returns:
            API response
        """
        return await self._async_request("POST", "/ears", {"reset": True})

    async def play_sound(self, sound: str, volume: Optional[int] = None) -> Dict[str, Any]:
        """Play a sound.

        Args:
            sound: Sound identifier
            volume: Volume level (0-100)

        Returns:
            API response
        """
        data = {"sound": sound}
        if volume is not None:
            data["volume"] = volume

        return await self._async_request("POST", "/sounds", data)

    async def display_picture(self, picture: str, duration: Optional[int] = None) -> Dict[str, Any]:
        """Display a picture.

        Args:
            picture: Picture identifier
            duration: Display duration in seconds

        Returns:
            API response
        """
        data = {"picture": picture}
        if duration is not None:
            data["duration"] = duration

        return await self._async_request("POST", "/pictures", data)

    async def get_pictures(self) -> Dict[str, Any]:
        """Get pictures information.

        Returns:
            Dictionary with pictures information
        """
        return await self._async_request("GET", "/pictures")

    async def get_sounds(self) -> Dict[str, Any]:
        """Get sounds information.

        Returns:
            Dictionary with sounds information
        """
        return await self._async_request("GET", "/sounds")

    async def get_apps(self) -> Dict[str, Any]:
        """Get applications information.

        Returns:
            Dictionary with applications information
        """
        return await self._async_request("GET", "/apps")
