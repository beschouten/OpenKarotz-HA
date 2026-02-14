"""OpenKarotz lights."""

import logging

from homeassistant.components.light import LightEntity, LightEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import OpenKarotzCoordinator
from .const import DOMAIN, LIGHT_ATTRIBUTES


# Predefined colors for Karotz LED
PREDEFINED_COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}
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
        self._led_id = led_data.get("id", 1)
        self._led_name = led_data.get("name", f"LED {self._led_id}")
        
        device_id = coordinator.data.get('info', {}).get('id', 'unknown') if coordinator.data else 'unknown'
        self._attr_unique_id = f"{device_id}_led_{self._led_id}"
        self._attr_name = self._led_name
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Check if light is on."""
        led_state = self.coordinator.leds_state or {} if self.coordinator and self.coordinator.leds_state else {}
        return led_state.get("enabled", False) if led_state else False

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
        led_state = self.coordinator.leds_state or {} if self.coordinator else {}
        modes = set()
        if led_state.get("color") or led_state.get("rgb_value"):
            modes.add("rgb")
        if led_state.get("color_temperature") is not None:
            modes.add("color_temperature")
        if led_state.get("preset"):
            modes.add("rgb")
        if not modes:
            # Default to rgb if no state available yet
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
        
        # Handle color/RGB input - these are mutually exclusive with color_temperature
        if color is not None:
            rgb = color
            data["rgb_value"] = f"{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        elif "rgb" in kwargs:
            rgb = kwargs["rgb"]
            data["rgb_value"] = f"{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        elif "color_name" in kwargs:
            if kwargs["color_name"] in PREDEFINED_COLORS:
                rgb = PREDEFINED_COLORS[kwargs["color_name"]]
                data["rgb_value"] = f"{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        elif "color_temperature" in kwargs:
            # Color temperature mode - clear any RGB values
            data["color_temperature"] = kwargs["color_temperature"]
            data["rgb_value"] = None
        else:
            # No color specified, just turn on with default brightness
            if not data:
                data["brightness"] = kwargs.get("brightness", 100)

        if data:
            await self.coordinator.api.set_led(**data)
        else:
            # Just turn on without changing color
            await self.coordinator.api.set_led(brightness=100)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the light."""
        await self.coordinator.api.set_led(brightness=0)

    async def async_select_color(self, color_name: str) -> None:
        """Select a predefined color for the LED."""
        if color_name in PREDEFINED_COLORS:
            color = PREDEFINED_COLORS[color_name]
            await self.async_turn_on(color=color)
        else:
            _LOGGER.warning(f"Unknown color: {color_name}")

    @property
    def device_state_attributes(self) -> dict:
        """Return device state attributes."""
        led_state = self.coordinator.leds_state or {}
        return {
            "preset": led_state.get("preset"),
            "color": led_state.get("color"),
            "rgb_value": led_state.get("rgb_value"),
        }