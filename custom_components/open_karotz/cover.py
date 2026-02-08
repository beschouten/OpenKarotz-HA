"""Cover platform for Open Karotz ear control."""
from __future__ import annotations

import logging

from homeassistant.components.cover import CoverDeviceClass, CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BASE_URL, DOMAIN, EAR_DOWN, EAR_HORIZONTAL, EAR_MAX, EAR_MIN, EAR_UP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz cover entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzEars(host, entry.entry_id)])


class OpenKarotzEars(CoverEntity):
    """Representation of the Open Karotz ears."""

    _attr_device_class = CoverDeviceClass.WINDOW
    _attr_name = "Open Karotz Ears"
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
    )
    _attr_translation_key = "ears"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the ears."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_ears"
        self._left_position = EAR_HORIZONTAL
        self._right_position = EAR_HORIZONTAL

    async def _async_send_command(self, left: int, right: int) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/ears?left={left}&right={right}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to set ear position: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    async def _async_send_reset(self) -> bool:
        """Send reset command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/ears_reset") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to reset ears: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    async def _async_send_random(self) -> bool:
        """Send random command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/ears_random") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to set random ear position: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        return False

    @property
    def current_cover_position(self) -> int | None:
        """Return the current position of the cover."""
        return int((self._left_position + self._right_position) / 2)

    async def async_open_cover(self, **kwargs) -> None:
        """Open the ears (up)."""
        self._left_position = EAR_UP
        self._right_position = EAR_UP
        await self._async_send_command(EAR_UP, EAR_UP)

    async def async_close_cover(self, **kwargs) -> None:
        """Close the ears (down)."""
        self._left_position = EAR_DOWN
        self._right_position = EAR_DOWN
        await self._async_send_command(EAR_DOWN, EAR_DOWN)

    async def async_set_cover_position(self, **kwargs) -> None:
        """Set the cover position."""
        position = kwargs.get("position", 50)
        left = int(position * EAR_MAX / 100)
        right = int(position * EAR_MAX / 100)
        self._left_position = left
        self._right_position = right
        await self._async_send_command(left, right)

    async def async_stop_cover(self, **kwargs) -> None:
        """Stop the cover."""
        pass

    async def async_open_cover_tilt(self, **kwargs) -> None:
        """Open the tilt."""
        self._left_position = EAR_UP
        self._right_position = EAR_DOWN
        await self._async_send_command(EAR_UP, EAR_DOWN)

    async def async_close_cover_tilt(self, **kwargs) -> None:
        """Close the tilt."""
        self._left_position = EAR_DOWN
        self._right_position = EAR_UP
        await self._async_send_command(EAR_DOWN, EAR_UP)

    async def async_stop_cover_tilt(self, **kwargs) -> None:
        """Stop the tilt."""
        pass

    async def async_reset_ears(self, **kwargs) -> None:
        """Reset the ears to default position."""
        self._left_position = EAR_HORIZONTAL
        self._right_position = EAR_HORIZONTAL
        await self._async_send_reset()

    async def async_random_ears(self, **kwargs) -> None:
        """Set ears to random position."""
        await self._async_send_random()