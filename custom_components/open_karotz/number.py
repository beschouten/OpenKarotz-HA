"""Number entities for the write-only ear servos."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KarotzRuntime
from .api import OpenKarotzError
from .const import EAR_HORIZONTAL, EAR_MAX, EAR_MIN
from .entity import OpenKarotzEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up ear numbers from a config entry."""
    runtime: KarotzRuntime = entry.runtime_data
    async_add_entities(
        [KarotzEar(entry, runtime, "left"), KarotzEar(entry, runtime, "right")]
    )


class KarotzEar(OpenKarotzEntity, NumberEntity):
    """One ear servo.

    Ears are write-only on the device: position is tracked optimistically
    in this entity. Moves always use noreset=1 (EarsReset hangs on this
    firmware); the motor settles on its own.
    """

    _attr_native_min_value = EAR_MIN
    _attr_native_max_value = EAR_MAX
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:robot"

    def __init__(self, entry: ConfigEntry, runtime: KarotzRuntime, side: str) -> None:
        super().__init__(entry, runtime, f"ear_{side}")
        self._side = side
        self._position = EAR_HORIZONTAL
        self._other = EAR_HORIZONTAL

    @property
    def translation_key(self) -> str:
        return f"ear_{self._side}"

    @property
    def native_value(self) -> int:
        return self._position

    async def async_set_native_value(self, value: float) -> None:
        value = int(value)
        left = value if self._side == "left" else self._other
        right = value if self._side == "right" else self._other
        try:
            await self._runtime.api.ears_move(left, right)
        except OpenKarotzError as err:
            raise HomeAssistantError(f"Ear move failed: {err}") from err
        self._position = value
        self.async_write_ha_state()
