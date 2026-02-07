"""OpenKarotz services."""

import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN, SERVICE_NAMES, SERVICE_DATA_SCHEMAS

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up OpenKarotz services."""

    async def handle_set_led(service: ServiceCall) -> None:
        """Handle set LED service."""
        try:
            entry_id = service.data.get("config_entry_id")
            if not entry_id:
                _LOGGER.error("config_entry_id is required for set_led service")
                return
            
            entry_data = hass.data[DOMAIN].get(entry_id)
            if not entry_data:
                _LOGGER.error(f"OpenKarotz entry {entry_id} not found")
                return
            
            api = entry_data.get("api")
            if not api:
                _LOGGER.error("API not found for OpenKarotz entry")
                return
            
            await api.set_led(
                color=service.data.get("color"),
                brightness=service.data.get("brightness"),
                color_temperature=service.data.get("color_temperature"),
                preset=service.data.get("preset"),
                rgb_value=service.data.get("rgb_value"),
            )
        except Exception as e:
            _LOGGER.error(f"Error setting LED: {e}")

    async def handle_play_tts(service: ServiceCall) -> None:
        """Handle play TTS service."""
        try:
            entry_id = service.data.get("config_entry_id")
            if not entry_id:
                _LOGGER.error("config_entry_id is required for play_tts service")
                return
            
            entry_data = hass.data[DOMAIN].get(entry_id)
            if not entry_data:
                _LOGGER.error(f"OpenKarotz entry {entry_id} not found")
                return
            
            api = entry_data.get("api")
            if not api:
                _LOGGER.error("API not found for OpenKarotz entry")
                return
            
            await api.play_tts(
                text=service.data.get("text"),
                voice=service.data.get("voice"),
                category=service.data.get("category"),
            )
        except Exception as e:
            _LOGGER.error(f"Error playing TTS: {e}")

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["SET_LED"],
        handle_set_led,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["set_led"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["PLAY_TTS"],
        handle_play_tts,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["play_tts"]),
    )

    _LOGGER.info("OpenKarotz services registered")
