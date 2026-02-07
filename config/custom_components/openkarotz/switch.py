"""OpenKarotz switches."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import ATTR_DEVICE_ID

from .api import OpenKarotzAPI
from .coordinator import OpenKarotzCoordinator
from .const import DOMAIN, SWITCH_ATTRIBUTES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenKarotz switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []

    # Get device state
    device_state = coordinator.device_state or {}
    if device_state.get("enabled", True):
        entities.append(OpenKarotzMainSwitch(coordinator))

    async_add_entities(entities)


class OpenKarotzSwitch(CoordinatorEntity[OpenKarotzCoordinator], SwitchEntity):
    """Base switch for OpenKarotz devices."""

    _attr_has_entity_name = True
    _attr_device_info = None

    def __init__(self, coordinator: OpenKarotzCoordinator) -> None:
        """Initialize switch."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info


class OpenKarotzMainSwitch(OpenKarotzSwitch):
    """Main device enable/disable switch."""

    _attr_name = "Enable Device"
    _attr_unique_id = f"{coordinator.data.get(ATTR_DEVICE_ID, 'unknown')}_enable_switch"

    @property
    def is_on(self) -> bool:
        """Check if device is enabled."""
        device_state = self.coordinator.device_state or {}
        return device_state.get("enabled", True)

    @property
    def available(self) -> bool:
        """Check if entity is available."""
        return self.coordinator.data.get(ATTR_CONNECTION_STATUS) == "connected"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the device."""
        device_state = self.coordinator.device_state or {}
        device_id = device_state.get("id", 1)
        await self.coordinator.api.set_device(device_id=device_id, enabled=True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the device."""
        device_state = self.coordinator.device_state or {}
        device_id = device_state.get("id", 1)
        await self.coordinator.api.set_device(device_id=device_id, enabled=False)

    @property
    def device_state_attributes(self) -> dict[str, str]:
        """Return device state attributes."""
        device_state = self.coordinator.device_state or {}
        return {
            "state": device_state.get("state"),
            "last_action": device_state.get("last_action"),
        }