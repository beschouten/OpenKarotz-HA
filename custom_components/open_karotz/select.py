"""Select platform for Open Karotz mood control."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BASE_URL, DOMAIN, MOOD_IDS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz select entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzMood(host, entry.entry_id)])


class OpenKarotzMood(SelectEntity):
    """Representation of the Open Karotz mood select."""

    _attr_name = "Open Karotz Mood"
    _attr_options = MOOD_IDS
    _attr_translation_key = "mood"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the mood select."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_mood"
        self._current_mood = MOOD_IDS[0]

    async def _async_play_mood(self, mood_id: str) -> bool:
        """Play mood on Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/apps/moods?id={mood_id}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to play mood: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error playing mood: %s", err)
            return False

    async def _async_play_random_mood(self) -> bool:
        """Play random mood on Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/apps/moods") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to play random mood: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error playing random mood: %s", err)
            return False

    @property
    def current_option(self) -> str | None:
        """Return the current mood."""
        return self._current_mood

    async def async_select_option(self, option: str) -> None:
        """Select a mood."""
        if option in MOOD_IDS:
            self._current_mood = option
            await self._async_play_mood(option)

    async def async_play_random(self) -> None:
        """Play random mood."""
        await self._async_play_random_mood()