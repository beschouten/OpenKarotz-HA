"""Open Karotz Home Assistant Integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .api import OpenKarotzAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.LIGHT,
    Platform.COVER,
    Platform.MEDIA_PLAYER,
    Platform.SELECT,
    Platform.CAMERA,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Open Karotz from a config entry."""
    host = entry.data["host"]

    api = OpenKarotzAPI(host)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Open Karotz integration."""
    from homeassistant.helpers.service import async_register_admin_service

    async def async_open_karotz_tts_service(service_call):
        """Handle TTS service call."""
        text = service_call.data.get("text", "")
        voice = service_call.data.get("voice", "6")

        if not text:
            raise HomeAssistantError("Text is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            import urllib.parse
            encoded_text = urllib.parse.quote(text)
            await api.play_tts(encoded_text, voice)
        except Exception as err:
            raise HomeAssistantError(f"Failed to play TTS: {err}")

    async_register_admin_service(
        hass, DOMAIN, "tts", async_open_karotz_tts_service
    )

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok