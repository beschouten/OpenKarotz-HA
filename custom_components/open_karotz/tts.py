"""TTS service for Open Karotz."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BASE_URL, DOMAIN, TTS_VOICES

_LOGGER = logging.getLogger(__name__)

SERVICE_TTS = "tts"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz TTS service."""
    host = entry.data[CONF_HOST]

    def play_tts(service: ServiceCall) -> None:
        """Play text-to-speech."""
        text = service.data.get("text", "")
        voice = service.data.get("voice", "6")

        if voice not in TTS_VOICES:
            voice = "1"

        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(hass)
        hass.async_create_task(
            _async_play_tts(hass, session, host, text, voice)
        )

    hass.services.register(DOMAIN, SERVICE_TTS, play_tts)


async def _async_play_tts(
    hass: HomeAssistant,
    session,
    host: str,
    text: str,
    voice: str,
) -> None:
    """Play TTS asynchronously."""
    import urllib.parse

    encoded_text = urllib.parse.quote(text)
    try:
        async with session.get(
            f"http://{host}/cgi-bin/tts?text={encoded_text}&voice={voice}"
        ) as resp:
            if resp.status == 200:
                _LOGGER.info("TTS played successfully")
            else:
                _LOGGER.error("Failed to play TTS: %s", resp.status)
    except Exception as err:
        _LOGGER.error("Error playing TTS: %s", err)