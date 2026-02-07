"""OpenKarotz binary sensors."""

import logging
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import ATTR_CONNECTION_STATUS

from .api import OpenKarotzAPI
from .coordinator import OpenKarotzCoordinator
from .const import DOMAIN, RFID_ATTRIBUTES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenKarotz binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []

    # Get RFID state
    rfid_state = coordinator.rfid_state or {}
    if rfid_state.get("rfid_enabled", False):
        entities.append(OpenKarotzRFIDSensor(coordinator))

    # Add any other binary sensor entities as needed
    async_add_entities(entities)


class OpenKarotzBinarySensor(CoordinatorEntity[OpenKarotzCoordinator], BinarySensorEntity):
    """Base binary sensor for OpenKarotz devices."""

    _attr_has_entity_name = True
    _attr_device_info = None

    def __init__(self, coordinator: OpenKarotzCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info


class OpenKarotzRFIDSensor(OpenKarotzBinarySensor):
    """RFID detection sensor."""

    _attr_name = "RFID Detection"
    _attr_unique_id = "rfid_detection"
    """RFID detection sensor."""

    _attr_name = "RFID Detection"
    _attr_unique_id = "rfid_detection"

    @property
    def is_on(self) -> bool:
        """Check if RFID is detected."""
        rfid_state = self.coordinator.rfid_state or {}
        return rfid_state.get("rfid_enabled", False)

    @property
    def available(self) -> bool:
        """Check if entity is available."""
        return self.coordinator.data.get(ATTR_CONNECTION_STATUS) == "connected"

    @property
    def device_state_attributes(self) -> dict[str, str]:
        """Return device state attributes."""
        rfid_state = self.coordinator.rfid_state or {}
        return {
            "detected_id": rfid_state.get("detected_id"),
            "detected_time": rfid_state.get("detected_time"),
            "event_type": rfid_state.get("event_type"),
            "previous_id": rfid_state.get("previous_id"),
        }