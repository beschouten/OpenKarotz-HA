"""TTS entity platform for Open Karotz."""
from __future__ import annotations

import logging

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA as TTS_PLATFORM_SCHEMA,
    Provider,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz TTS entity."""
    host = entry.data[CONF_HOST]
    api = hass.data[DOMAIN][entry.entry_id]
    
    entity = OpenKarotzTTSEntity(entry.entry_id, host, api)
    async_add_entities([entity])


class OpenKarotzTTSEntity(Provider):
    """TTS provider for Open Karotz."""

    def __init__(self, entry_id: str, host: str, api) -> None:
        """Initialize TTS provider."""
        self._entry_id = entry_id
        self._host = host
        self._api = api
        self._attr_name = "Open Karotz TTS"
        self._attr_icon = "mdi:speaker-message"
        self._attr_supported_languages = [
            "fr", "en", "de", "es", "it", "nl", "pt", "ru", "tr",
            "ar", "zh", "ja", "ko", "th", "vi"
        ]
        self._attr_default_language = "en"
        self._attr_supported_options = [CONF_LANG]

    @property
    def name(self) -> str:
        """Return provider name."""
        return self._attr_name

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict | None = None
    ):
        """Get TTS audio."""
        voice = options.get(CONF_LANG, "6")
        
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        
        session = async_get_clientsession(self.hass)
        try:
            import urllib.parse
            encoded_text = urllib.parse.quote(message)
            async with session.get(
                f"http://{self._host}/cgi-bin/tts?text={encoded_text}&voice={voice}"
            ) as resp:
                if resp.status == 200:
                    audio = await resp.read()
                    return ("mp3", audio)
        except Exception as err:
            _LOGGER.error("Error getting TTS audio: %s", err)
        
        return (None, None)
