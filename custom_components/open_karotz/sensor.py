"""Sensor platform for Open Karotz."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, STORAGE_KAROTZ, STORAGE_USB

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz sensor entities."""
    host = entry.data[CONF_HOST]
    coordinator = OpenKarotzCoordinator(hass, host)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            KarotzStorageSensor(coordinator, entry),
            UsbStorageSensor(coordinator, entry),
        ]
    )


class OpenKarotzCoordinator(DataUpdateCoordinator):
    """Class to manage data updates for Open Karotz."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Open Karotz",
            update_method=self._async_update_data,
            update_interval=None,
        )
        self.host = host

    async def _async_update_data(self):
        """Fetch data from Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        import json

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self.host}/cgi-bin/get_free_space") as resp:
                if resp.status == 200:
                    text = await resp.text()
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        _LOGGER.error("Failed to parse JSON from get_free_space: %s", text)
                        return None
                _LOGGER.error("Failed to fetch free space: %s", resp.status)
                return None
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            return None


class KarotzStorageSensor(CoordinatorEntity, SensorEntity):
    """Representation of the Karotz storage sensor."""

    _attr_translation_key = "karotz_storage"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: OpenKarotzCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Karotz Storage"
        self._attr_unique_id = f"{entry.entry_id}_{STORAGE_KAROTZ}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("karotz", {}).get("percent_used_space")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:memory"


class UsbStorageSensor(CoordinatorEntity, SensorEntity):
    """Representation of the USB storage sensor."""

    _attr_translation_key = "usb_storage"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: OpenKarotzCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "USB Storage"
        self._attr_unique_id = f"{entry.entry_id}_{STORAGE_USB}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("usb", {}).get("percent_used_space")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:usb"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self.coordinator.data is None:
            return False
        return self.coordinator.data.get("usb", {}).get("percent_used_space", -1) >= 0
