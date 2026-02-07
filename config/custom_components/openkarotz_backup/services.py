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
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.set_led(
                color=service.data.get("color"),
                brightness=service.data.get("brightness"),
                color_temperature=service.data.get("color_temperature"),
                preset=service.data.get("preset"),
                rgb_value=service.data.get("rgb_value"),
            )
        except Exception as e:
            _LOGGER.error(f"Error setting LED: {e}")

    async def handle_play_audio(service: ServiceCall) -> None:
        """Handle play audio service."""
        try:
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.play_audio(
                source=service.data.get("source"),
                category=service.data.get("category"),
                volume=service.data.get("volume"),
            )
        except Exception as e:
            _LOGGER.error(f"Error playing audio: {e}")

    async def handle_stop_audio(service: ServiceCall) -> None:
        """Handle stop audio service."""
        try:
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.stop_audio(source=service.data.get("source"))
        except Exception as e:
            _LOGGER.error(f"Error stopping audio: {e}")

    async def handle_set_volume(service: ServiceCall) -> None:
        """Handle set volume service."""
        try:
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.set_volume(service.data.get("volume", 50))
        except Exception as e:
            _LOGGER.error(f"Error setting volume: {e}")

    async def handle_play_tts(service: ServiceCall) -> None:
        """Handle play TTS service."""
        try:
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.play_tts(
                text=service.data.get("text"),
                voice=service.data.get("voice"),
                category=service.data.get("category"),
            )
        except Exception as e:
            _LOGGER.error(f"Error playing TTS: {e}")

    async def handle_play_sound(service: ServiceCall) -> None:
        """Handle play sound service."""
        try:
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.play_sound(
                sound=service.data.get("sound"),
                volume=service.data.get("volume"),
            )
        except Exception as e:
            _LOGGER.error(f"Error playing sound: {e}")

    async def handle_display_picture(service: ServiceCall) -> None:
        """Handle display picture service."""
        try:
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.display_picture(
                picture=service.data.get("picture"),
                duration=service.data.get("duration"),
            )
        except Exception as e:
            _LOGGER.error(f"Error displaying picture: {e}")

    async def handle_move_ears(service: ServiceCall) -> None:
        """Handle move ears service."""
        try:
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.move_ears(
                left=service.data.get("left"),
                right=service.data.get("right"),
            )
        except Exception as e:
            _LOGGER.error(f"Error moving ears: {e}")

    async def handle_ear_mode(service: ServiceCall) -> None:
        """Handle ear mode service."""
        try:
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.ears_mode(mode=service.data.get("mode"))
        except Exception as e:
            _LOGGER.error(f"Error setting ear mode: {e}")

    async def handle_ear_reset(service: ServiceCall) -> None:
        """Handle ear reset service."""
        try:
            coordinator = hass.data[DOMAIN][service.data.get("config_entry_id")]
            api = coordinator["api"]
            await api.ears_reset()
        except Exception as e:
            _LOGGER.error(f"Error resetting ears: {e}")

    # Register services using hass.services.async_register
    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["SET_LED"],
        handle_set_led,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["set_led"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["PLAY_AUDIO"],
        handle_play_audio,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["play_audio"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["STOP_AUDIO"],
        handle_stop_audio,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["stop_audio"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["SET_VOLUME"],
        handle_set_volume,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["set_volume"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["PLAY_TTS"],
        handle_play_tts,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["play_tts"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["PLAY_SOUND"],
        handle_play_sound,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["play_sound"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["DISPLAY_PICTURE"],
        handle_display_picture,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["display_picture"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["MOVE_EARS"],
        handle_move_ears,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["move_ears"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["EAR_MODE"],
        handle_ear_mode,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["ear_mode"]),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_NAMES["EAR_RESET"],
        handle_ear_reset,
        schema=vol.Schema(SERVICE_DATA_SCHEMAS["ear_reset"]),
    )

    _LOGGER.info("OpenKarotz services registered")
