"""Light platform for the OpenKarotz nose LED."""
from __future__ import annotations

import logging

from homeassistant.components.light import (
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import OpenKarotzError
from .const import EFFECT_BLINK, EFFECT_OFF, EFFECT_PULSE, EFFECTS
from .entity import OpenKarotzEntity
from . import KarotzRuntime

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the LED light from a config entry."""
    runtime: KarotzRuntime = entry.runtime_data
    async_add_entities([KarotzLed(entry, runtime)])


class KarotzLed(OpenKarotzEntity, LightEntity):
    """RGB nose LED with pulse/blink effects.

    State truth: status.led_color / status.led_pulse. Blink is not reported
    by status, so the last-applied effect is tracked optimistically.
    """

    _attr_translation_key = "led"
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = EFFECTS

    def __init__(self, entry: ConfigEntry, runtime: KarotzRuntime) -> None:
        super().__init__(entry, runtime, "led")
        self._effect = EFFECT_OFF

    @staticmethod
    def _effect_params(effect: str) -> tuple[int | None, int | None]:
        """Map effect to (pulse, blink). CGI rejects pulse+blink together and
        treats a present-but-zero param as active, so omit the inactive one."""
        if effect == EFFECT_PULSE:
            return 1, None
        if effect == EFFECT_BLINK:
            return None, 1
        return None, None

    @property
    def is_on(self) -> bool:
        return self.status.get("led_color", "000000") not in ("000000", "", None)

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        raw = self.status.get("led_color") or ""
        if len(raw) != 6:
            return None
        try:
            return (int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16))
        except ValueError:
            return None

    @property
    def effect(self) -> str:
        if self.status.get("led_pulse") == "1":
            return EFFECT_PULSE
        return EFFECT_OFF

    async def async_turn_on(self, **kwargs) -> None:
        rgb = kwargs.get(ATTR_RGB_COLOR) or self.rgb_color or (255, 255, 255)
        effect = kwargs.get(ATTR_EFFECT, EFFECT_OFF)
        pulse, blink = self._effect_params(effect)
        self._effect = effect
        color = "%02x%02x%02x" % tuple(rgb)
        try:
            await self._runtime.api.set_led(color, pulse=pulse, blink=blink)
        except OpenKarotzError as err:
            self._effect = EFFECT_OFF
            raise HomeAssistantError(f"LED command failed: {err}") from err
        self.async_write_ha_state()
        self.coordinator.async_update_listeners()

    async def async_turn_off(self, **kwargs) -> None:
        self._effect = EFFECT_OFF
        try:
            await self._runtime.api.set_led("000000")
        except OpenKarotzError as err:
            raise HomeAssistantError(f"LED command failed: {err}") from err
        self.async_write_ha_state()
        self.coordinator.async_update_listeners()
