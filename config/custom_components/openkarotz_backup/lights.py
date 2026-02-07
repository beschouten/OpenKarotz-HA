"""OpenKarotz lights."""

import logging

from homeassistant.components.light import LightEntity, LightEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import OpenKarotzCoordinator
from .const import DOMAIN, LIGHT_ATTRIBUTES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenKarotz lights."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []

    # Get LED state
    led_state = coordinator.leds_state or {}
    led_groups = led_state.get("leds", [])
    if not led_groups:
        led_groups = [{"id": 1, "name": "Main LED", "enabled": True}]

    for led in led_groups:
        entities.append(OpenKarotzLight(coordinator, led))

    async_add_entities(entities)


class OpenKarotzLight(CoordinatorEntity[OpenKarotzCoordinator], LightEntity):
    """Light entity for OpenKarotz LEDs."""

    entity_description = LightEntityDescription(
        key="led",
        name="LED Light",
    )

    def __init__(self, coordinator: OpenKarotzCoordinator, led_data: dict) -> None:
        """Initialize light entity."""
        super().__init__(coordinator)
        self.led_data = led_data
        led_id = led_data.get("id", 1)
        self._attr_unique_id = f"{coordinator.data.get('info', {}).get('id', 'unknown')}_led_{led_id}"
        self._attr_name = led_data.get("name", f"LED {led_id}")
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Check if light is on."""
        led_state = self.coordinator.leds_state or {}
        return led_state.get("enabled", False)

    @property
    def color_mode(self) -> str | None:
        """Return color mode."""
        led_state = self.coordinator.leds_state or {}
        if led_state.get("color_temperature") is not None:
            return "color_temperature"
        if led_state.get("color") or led_state.get("rgb_value"):
            return "rgb"
        return None

    @property
    def supported_color_modes(self) -> set[str]:
        """Return supported color modes."""
        led_state = self.coordinator.leds_state or {}
        modes = set()
        if led_state.get("color") or led_state.get("rgb_value"):
            modes.add("rgb")
        if led_state.get("color_temperature") is not None:
            modes.add("color_temperature")
        if led_state.get("preset"):
            modes.add("rgb")
        return modes

    @property
    def color(self) -> tuple[int, int, int] | None:
        """Return current color."""
        led_state = self.coordinator.leds_state or {}
        if led_state.get("rgb_value"):
            try:
                return tuple(int(led_state["rgb_value"][i:i+2], 16) for i in (0, 2, 4))
            except (ValueError, IndexError):
                pass
        return None

    @property
    def brightness(self) -> int:
        """Return brightness level."""
        led_state = self.coordinator.leds_state or {}
        return led_state.get("brightness", 0)

    @property
    def color_temperature(self) -> int | None:
        """Return color temperature in Kelvin."""
        led_state = self.coordinator.leds_state or {}
        return led_state.get("color_temperature")

    async def async_turn_on(
        self,
        color: tuple[int, int, int] | None = None,
        **kwargs,
    ) -> None:
        """Turn on the light."""
        led_state = self.coordinator.leds_state or {}
        led_id = self.led_data.get("id", 1)

        data = {}
        if "brightness" in kwargs:
            data["brightness"] = kwargs["brightness"]
        if "color" in kwargs:
            rgb = kwargs["color"]
            data["rgb_value"] = f"{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        if "color_temperature" in kwargs:
            data["color_temperature"] = kwargs["color_temperature"]
        if "rgb" in kwargs:
            data["rgb_value"] = f"{kwargs['rgb'][0]:02x}{kwargs['rgb'][1]:02x}{kwargs['rgb'][2]:02x}"

        await self.coordinator.api.set_led(led_id=led_id, **data)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the light."""
        led_id = self.led_data.get("id", 1)
        await self.coordinator.api.set_led(led_id=led_id, brightness=0)

    @property
    def device_state_attributes(self) -> dict[str, str]:
        """Return device state attributes."""
        led_state = self.coordinator.leds_state or {}
        return {
            "preset": led_state.get("preset"),
            "color": led_state.get("color"),
            "rgb_value": led_state.get("rgb_value"),
        }