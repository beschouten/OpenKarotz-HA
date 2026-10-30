"""Switch platform: ear motor enable/disable."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import OpenKarotzError
from .entity import OpenKarotzEntity
from . import KarotzRuntime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switches from a config entry."""
    runtime: KarotzRuntime = entry.runtime_data
    async_add_entities([KarotzEarsMode(entry, runtime), KarotzSleep(entry, runtime)])


class KarotzEarsMode(OpenKarotzEntity, SwitchEntity):
    """Ear motors enabled/disabled (ears_mode CGI).

    On = motors enabled (status ears_disabled == '0'). Re-enabling runs
    EarsReset on the device which hangs the CGI -> fire-and-forget; the
    coordinator confirms via ears_disabled.
    """

    _attr_translation_key = "ears_enabled"
    _attr_icon = "mdi:ear-hearing"

    def __init__(self, entry: ConfigEntry, runtime: KarotzRuntime) -> None:
        super().__init__(entry, runtime, "ears_enabled")

    @property
    def is_on(self) -> bool:
        return self.status.get("ears_disabled") == "0"

    async def async_turn_on(self, **kwargs) -> None:
        try:
            await self._runtime.api.ears_mode(disable=False)
        except OpenKarotzError as err:
            raise HomeAssistantError(f"Ears enable failed: {err}") from err
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        try:
            await self._runtime.api.ears_mode(disable=True)
        except OpenKarotzError as err:
            raise HomeAssistantError(f"Ears disable failed: {err}") from err
        await self.coordinator.async_refresh()


class KarotzSleep(OpenKarotzEntity, SwitchEntity):
    """Sleep mode. Both CGIs hang (EarsReset family) -> fire-and-forget;
    truth comes from status.sleep on the next coordinator poll."""

    _attr_translation_key = "sleep"
    _attr_icon = "mdi:power-sleep"

    def __init__(self, entry: ConfigEntry, runtime: KarotzRuntime) -> None:
        super().__init__(entry, runtime, "sleep")

    @property
    def is_on(self) -> bool:
        return self.status.get("sleep") == "1"

    async def async_turn_on(self, **kwargs) -> None:
        await self._runtime.api.sleep()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        await self._runtime.api.wakeup()
        self.async_write_ha_state()
