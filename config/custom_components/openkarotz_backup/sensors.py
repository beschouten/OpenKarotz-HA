"""OpenKarotz sensors."""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import ATTR_DEVICE_ID

from .api import OpenKarotzAPI
from .coordinator import OpenKarotzCoordinator
from .const import SENSOR_TYPES, ATTR_API_VERSION, ATTR_CONNECTION_STATUS, ATTR_ERROR_MESSAGE, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenKarotz sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []

    # Informational sensors
    entities.append(OpenKarotzInfoSensor(coordinator))
    entities.append(OpenKarotzStateSensor(coordinator))
    entities.append(OpenKarotzMemoryUsageSensor(coordinator))
    entities.append(OpenKarotzUptimeSensor(coordinator))

    async_add_entities(entities)


class OpenKarotzSensor(CoordinatorEntity[OpenKarotzCoordinator]):
    """Base sensor for OpenKarotz devices."""

    _attr_has_entity_name = True
    _attr_device_info = None

    def __init__(self, coordinator: OpenKarotzCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info


class OpenKarotzInfoSensor(OpenKarotzSensor):
    """Device information sensor."""

    _attr_name = "Device Name"
    _attr_unique_id = f"{coordinator.data.get(ATTR_DEVICE_ID, 'unknown')}_info"

    @property
    def native_value(self):
        """Return device name."""
        return self.coordinator.data.get("info", {}).get("name", "Unknown")


class OpenKarotzStateSensor(OpenKarotzSensor):
    """Device state sensor."""

    _attr_name = "Device State"
    _attr_unique_id = f"{coordinator.data.get(ATTR_DEVICE_ID, 'unknown')}_state"

    @property
    def native_value(self):
        """Return device state."""
        return self.coordinator.data.get("state", {}).get("state", "Unknown")


class OpenKarotzMemoryUsageSensor(OpenKarotzSensor):
    """Memory usage sensor."""

    _attr_name = "Memory Usage"
    _attr_unique_id = f"{coordinator.data.get(ATTR_DEVICE_ID, 'unknown')}_memory_usage"

    @property
    def native_value(self):
        """Return memory usage."""
        return self.coordinator.data.get("state", {}).get("memory", {}).get("usage", 0)

    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""
        return "%" if isinstance(self.native_value, (int, float)) else None

    @property
    def device_state_attributes(self):
        """Return device attributes."""
        state = self.coordinator.data.get("state", {})
        memory = state.get("memory", {})
        return {
            "total": memory.get("total", 0),
            "used": memory.get("used", 0),
            "free": memory.get("free", 0),
        }


class OpenKarotzUptimeSensor(OpenKarotzSensor):
    """Device uptime sensor."""

    _attr_name = "Device Uptime"
    _attr_unique_id = f"{coordinator.data.get(ATTR_DEVICE_ID, 'unknown')}_uptime"

    @property
    def native_value(self):
        """Return device uptime in seconds."""
        return self.coordinator.data.get("state", {}).get("uptime", 0)

    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""
        return "seconds"