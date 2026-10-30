"""TTS entity for OpenKarotz (device-side Acapela synthesis)."""
from __future__ import annotations

import logging

from homeassistant.components.tts import ATTR_OPTIONS, TTSEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import OpenKarotzError
from .entity import OpenKarotzEntity
from . import KarotzRuntime

_LOGGER = logging.getLogger(__name__)

DEFAULT_VOICE = "6"  # English (US) Female on this firmware


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the TTS entity from a config entry."""
    runtime: KarotzRuntime = entry.runtime_data
    voices: list[dict] = []
    try:
        voices = await runtime.api.voice_list()
    except OpenKarotzError as err:
        _LOGGER.warning("Could not load voice list: %s", err)
    async_add_entities([KarotzTTS(entry, runtime, voices)])


class KarotzTTS(OpenKarotzEntity, TTSEntity):
    """Speak text through the Karotz speaker."""

    _attr_translation_key = "tts"

    def __init__(
        self, entry: ConfigEntry, runtime: KarotzRuntime, voices: list[dict]
    ) -> None:
        super().__init__(entry, runtime, "tts")
        self._attr_name = None  # device name + "text to speech"
        if voices:
            self._attr_supported_voices = {v["id"]: v.get("lang", v["id"]) for v in voices}
            self._attr_default_voice = DEFAULT_VOICE
            self._attr_default_language = None

    async def async_speak_text(
        self, media_id: str, language: str | None, options: dict | None
    ) -> None:
        voice = (options or {}).get(ATTR_OPTIONS) or self.default_voice
        try:
            await self._runtime.api.tts(media_id, voice=voice)
        except OpenKarotzError as err:
            raise HomeAssistantError(f"TTS failed: {err}") from err

    async def async_speak_text_stream(
        self, media_id: str, language: str | None, options: dict | None
    ) -> None:
        """Synthesis happens on-device; no audio stream is produced."""
        raise NotImplementedError("OpenKarotz synthesizes on-device; no stream")
