"""Camera platform for Open Karotz snapshot."""
from __future__ import annotations

import logging

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz camera entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzCamera(host, entry.entry_id)])


class OpenKarotzCamera(Camera):
    """Representation of the Open Karotz camera."""

    _attr_name = "Open Karotz Camera"
    _attr_translation_key = "camera"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the camera."""
        super().__init__()
        self._host = host
        self._attr_unique_id = f"{entry_id}_camera"
        self._last_image = None

    async def _async_capture_snapshot(self) -> bytes | None:
        """Capture a snapshot from Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        import json

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/snapshot?silent=1") as resp:
                if resp.status == 200:
                    content_type = resp.headers.get("content-type", "")
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

    def camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return the current image."""
        return self._last_image

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return the current image."""
        self._last_image = await self._async_capture_snapshot()
        return self._last_image

    async def async_enable_motion_detection(self) -> None:
        """Enable motion detection."""
        pass

    async def async_disable_motion_detection(self) -> None:
        """Disable motion detection."""
        pass

    @property
    def motion_detection_enabled(self) -> bool:
        """Return the motion detection status."""
        return False
