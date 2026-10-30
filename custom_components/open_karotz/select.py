"""Select platform: quick sound picker (moods live on the media player —
the select integration caps at 100 options, moods number 305)."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KarotzRuntime
from .api import OpenKarotzError
from .entity import OpenKarotzEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up selects from a config entry."""
    runtime: KarotzRuntime = entry.runtime_data
    try:
        sounds = await runtime.api.sound_list()
    except OpenKarotzError as err:
        _LOGGER.warning("Could not load sound list: %s", err)
        sounds = []
    async_add_entities([KarotzSoundSelect(entry, runtime, [s["id"] for s in sounds])])


class KarotzSoundSelect(OpenKarotzEntity, SelectEntity):
    """Playing a sound by id. Selection triggers playback then resets."""

    _attr_translation_key = "sound"
    _attr_icon = "mdi:music-note"

    def __init__(self, entry: ConfigEntry, runtime: KarotzRuntime, ids: list[str]) -> None:
        super().__init__(entry, runtime, "sound")
        self._attr_options = ids
        self._current: str | None = None

    @property
    def current_option(self) -> str | None:
        return self._current

    async def async_select_option(self, option: str) -> None:
        try:
            await self._runtime.api.play_sound(option)
        except OpenKarotzError as err:
            raise HomeAssistantError(f"Sound playback failed: {err}") from err
        self._current = option
        self.async_write_ha_state()
