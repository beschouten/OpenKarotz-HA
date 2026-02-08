"""Switch platform for Open Karotz system controls."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
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
    """Set up Open Karotz switch entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzSleepSwitch(host, entry.entry_id)])


class OpenKarotzSleepSwitch(SwitchEntity):
    """Representation of the Open Karotz sleep switch."""

    _attr_name = "Open Karotz Sleep"
    _attr_translation_key = "sleep"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the sleep switch."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_sleep"
        self._is_on = False

    async def _async_send_command(self, endpoint: str) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}{endpoint}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to send command: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch (wake up)."""
        self._is_on = True
        await self._async_send_command("/cgi-bin/wake_up")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch (sleep)."""
        self._is_on = False
        await self._async_send_command("/cgi-bin/sleep")
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state(force_refresh=True)