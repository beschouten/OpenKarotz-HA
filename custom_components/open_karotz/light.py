"""Light platform for Open Karotz LED control."""
from __future__ import annotations

import logging

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BASE_URL, DOMAIN, LED_COLORS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz light entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzLed(host, entry.entry_id)])


class OpenKarotzLed(LightEntity):
    """Representation of the Open Karotz LED."""

    _attr_name = "Open Karotz LED"
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_translation_key = "led"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the LED."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_led"
        self._attr_is_on = False
        self._rgb_color = (0, 0, 0)

    async def _async_send_command(self, color: str) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/leds?color={color}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to set LED color: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    async def async_update(self) -> None:
        """Update the entity status."""
        if self._rgb_color != (0, 0, 0):
            self._attr_is_on = True
        else:
            self._attr_is_on = False

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the color variable."""
        return self._rgb_color

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the LED."""
        rgb = kwargs.get("rgb_color", self._rgb_color)
        self._rgb_color = rgb
        self._attr_is_on = True

        hex_color = f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
        await self._async_send_command(hex_color)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the LED."""
        self._rgb_color = (0, 0, 0)
        self._attr_is_on = False
        await self._async_send_command("000000")

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state(force_refresh=True)