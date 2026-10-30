"""Media player platform for OpenKarotz (play-only, D2).

The firmware has no stop/pause/volume (sound_control is dead), so this
player supports SELECT_SOURCE (moods + sounds) and PLAY_MEDIA (TTS text)
only. Playback endpoints are synchronous: state is 'playing' while the
CGI call is in flight, then back to 'idle'.
"""
from __future__ import annotations

import html
import logging

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import OpenKarotzError
from .entity import OpenKarotzEntity
from . import KarotzRuntime

_LOGGER = logging.getLogger(__name__)

SOUND_PREFIX = "sound: "
MOOD_MAX_SECONDS = 120  # mood audio length cap for the playing-state timer


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the media player from a config entry."""
    runtime: KarotzRuntime = entry.runtime_data
    moods: list[dict] = []
    sounds: list[dict] = []
    try:
        moods = await runtime.api.moods_list()
        sounds = await runtime.api.sound_list()
    except OpenKarotzError as err:
        _LOGGER.warning("Could not load moods/sounds: %s", err)
    async_add_entities([KarotzPlayer(entry, runtime, moods, sounds)])


class KarotzPlayer(OpenKarotzEntity, MediaPlayerEntity):
    """Play-only media player backed by moods/sounds/TTS CGIs."""

    _attr_translation_key = "player"
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY_MEDIA
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(
        self, entry: ConfigEntry, runtime: KarotzRuntime,
        moods: list[dict], sounds: list[dict],
    ) -> None:
        super().__init__(entry, runtime, "player")
        self._moods = {
            html.unescape(m.get("text", m.get("id", ""))): m["id"] for m in moods
        }
        self._sounds = [s["id"] for s in sounds]
        self._attr_source_list = [
            *[SOUND_PREFIX + s for s in self._sounds],
            *self._moods.keys(),
        ]
        self._state = MediaPlayerState.IDLE
        self._title: str | None = None
        self._idle_timer = None

    @property
    def state(self) -> MediaPlayerState:
        return self._state

    @property
    def media_title(self) -> str | None:
        return self._title

    @property
    def source(self) -> str | None:
        return self._title if self._title in (self._attr_source_list or []) else None

    async def async_select_source(self, source: str) -> None:
        api = self._runtime.api
        if source.startswith(SOUND_PREFIX):
            sound_id = source[len(SOUND_PREFIX):]
            self._title = source
            self._state = MediaPlayerState.PLAYING
            self.async_write_ha_state()
            try:
                await api.play_sound(sound_id)
            except OpenKarotzError as err:
                raise HomeAssistantError(f"Playback failed: {err}") from err
            finally:
                self._state = MediaPlayerState.IDLE
                self.async_write_ha_state()
            return
        if source not in self._moods:
            raise HomeAssistantError(f"Unknown source: {source}")
        # Moods hang server-side after audio (EarsReset family) -> FAF.
        self._title = source
        self._state = MediaPlayerState.PLAYING
        self.async_write_ha_state()
        await api.play_mood(self._moods[source])
        if self._idle_timer is not None:
            self._idle_timer()
        self._idle_timer = self.hass.async_call_later(
            MOOD_MAX_SECONDS, self._async_finish_mood
        )

    def _async_finish_mood(self, _now=None) -> None:
        self._idle_timer = None
        self._state = MediaPlayerState.IDLE
        self.async_write_ha_state()

    async def async_play_media(self, media_type: str, media_id: str, **kwargs) -> None:
        """Play: media_id is TTS text (default), or 'sound:<id>' / 'mood:<name>'."""
        if media_id.startswith("sound:"):
            await self.async_select_source(
                SOUND_PREFIX + media_id.split(":", 1)[1].strip()
            )
            return
        if media_id.startswith("mood:"):
            await self.async_select_source(media_id.split(":", 1)[1].strip())
            return
        self._title = media_id[:80]
        self._state = MediaPlayerState.PLAYING
        self.async_write_ha_state()
        try:
            await self._runtime.api.tts(media_id)
        except OpenKarotzError as err:
            raise HomeAssistantError(f"TTS failed: {err}") from err
        finally:
            self._state = MediaPlayerState.IDLE
            self.async_write_ha_state()
