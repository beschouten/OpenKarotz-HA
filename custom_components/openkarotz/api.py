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
      API_ENDPOINTS,
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
                await self._async_request("GET", API_ENDPOINTS["GET_INFO"], skip_connection_check=True)
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
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await response.json()
                else:
                    text = await response.text()
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError as e:
                        _LOGGER.error(f"Invalid JSON response: {e}")
                        raise OpenKarotzAPIError(f"Invalid response format: {e}")

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
        return await self._async_request("GET", API_ENDPOINTS["GET_INFO"], skip_connection_check=True)

    async def get_version(self) -> Dict[str, Any]:
        """Get device firmware versions.

        Returns:
            Dictionary with firmware version information
        """
        return await self._async_request("GET", API_ENDPOINTS["GET_VERSION"], skip_connection_check=True)

    async def wakeup(self, silent: bool = False) -> Dict[str, Any]:
        """Wake up the device.

        Args:
            silent: If True, no sound is played

        Returns:
            API response
        """
        params = {"silent": 1 if silent else 0}
        return await self._async_request("GET", API_ENDPOINTS["WAKEUP"], params=params, skip_connection_check=True)

    async def sleep(self) -> Dict[str, Any]:
        """Put device to sleep.

        Returns:
            API response
        """
        return await self._async_request("GET", API_ENDPOINTS["SLEEP"], skip_connection_check=True)

    async def get_state(self) -> Dict[str, Any]:
        """Get device state.

        Returns:
            Dictionary with device state
        """
        return await self._async_request("GET", API_ENDPOINTS["GET_STATE"])

    async def get_leds(self) -> Dict[str, Any]:
        """Get LED information and state.

        Returns:
            Dictionary with LED information
        """
        return await self._async_request("GET", API_ENDPOINTS["GET_LEDS"])

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

        return await self._async_request("POST", API_ENDPOINTS["POST_LEDS"], data=data, skip_connection_check=True)

    async def get_tts(self) -> Dict[str, Any]:
        """Get TTS information and state.

        Returns:
            Dictionary with TTS information
        """
        return await self._async_request("GET", API_ENDPOINTS["GET_TTS"])

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

        return await self._async_request("POST", API_ENDPOINTS["GET_TTS"], data)

    async def get_apps(self) -> Dict[str, Any]:
        """Get applications information.

        Returns:
            Dictionary with applications information
        """
        return await self._async_request("GET", API_ENDPOINTS["GET_APPS"])