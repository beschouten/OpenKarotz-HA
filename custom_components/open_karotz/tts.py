"""TTS entity for OpenKarotz (device-side Acapela synthesis).

The Karotz synthesizes and plays locally, so async_speak is overridden to
drive the device directly (no audio stream is produced for media players).
"""
from __future__ import annotations

import logging

from homeassistant.components.tts import Voice
from homeassistant.components.tts.entity import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KarotzRuntime
from .api import OpenKarotzError
from .entity import OpenKarotzEntity

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


class KarotzTTS(OpenKarotzEntity, TextToSpeechEntity):
    """Speak text through the Karotz speaker."""

    _attr_translation_key = "tts"
    _attr_supported_languages = ["en", "fr"]  # noqa: RUF012
    _attr_default_language = "en"
    _attr_supported_options = ["voice"]  # noqa: RUF012
    _attr_default_options = {"voice": DEFAULT_VOICE}  # noqa: RUF012

    def __init__(
        self, entry: ConfigEntry, runtime: KarotzRuntime, voices: list[dict]
    ) -> None:
        super().__init__(entry, runtime, "tts")
        self._voices = [
            Voice(voice_id=v["id"], name=v.get("lang", v["id"])) for v in voices
        ]

    def async_get_supported_voices(self, language: str) -> list[Voice] | None:
        return self._voices or None

    async def async_speak(
        self,
        media_player_entity_id: list[str],
        message: str,
        cache: bool,
        language: str | None = None,
        options: dict | None = None,
    ) -> None:
        """Speak on the Karotz itself (device-side synthesis)."""
        voice = (options or {}).get("voice") or DEFAULT_VOICE
        try:
            await self._runtime.api.tts(message, voice=voice)
        except OpenKarotzError as err:
            raise HomeAssistantError(f"TTS failed: {err}") from err

    def async_get_tts_audio(self, message, language, options):
        """No audio stream: the device plays the audio itself."""
        return None, None
