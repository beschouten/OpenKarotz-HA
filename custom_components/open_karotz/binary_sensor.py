"""Binary sensor platform for Open Karotz RFID."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Set up Open Karotz binary sensor entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzRfidSensor(host, entry.entry_id)])


class OpenKarotzRfidSensor(BinarySensorEntity):
    """Representation of the Open Karotz RFID sensor."""

    _attr_name = "Open Karotz RFID"
    _attr_device_class = "presence"
    _attr_translation_key = "rfid"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the RFID sensor."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_rfid"
        self._is_on = False
        self._tag_id = None

    async def _async_get_rfid_list(self) -> dict | None:
        """Get RFID list from Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/rfid_list") as resp:
                if resp.status == 200:
                    return await resp.json()
                _LOGGER.error("Failed to get RFID list: %s", resp.status)
                return None
        except Exception as err:
            _LOGGER.error("Error getting RFID list: %s", err)
            return None

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self._is_on

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return the state attributes."""
        return {"tag_id": self._tag_id}

    async def async_update(self) -> None:
        """Update the entity status."""
        data = await self._async_get_rfid_list()
        if data and "rfids" in data and len(data["rfids"]) > 0:
            self._is_on = True
            self._tag_id = data["rfids"][0].get("tag")
        else:
            self._is_on = False
            self._tag_id = None