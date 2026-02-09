"""Open Karotz Home Assistant Integration."""
from __future__ import annotations

import asyncio
import logging
import yaml

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.service import async_register_admin_service
import voluptuous as vol

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
    # Load services.yaml using async executor to avoid blocking
    services_path = hass.config.path("custom_components/open_karotz/services.yaml")
    try:
        services_config = await hass.async_add_executor_job(
            lambda: yaml.safe_load(open(services_path, "r", encoding="utf-8"))
        )
    except FileNotFoundError:
        _LOGGER.error("services.yaml not found at %s", services_path)
        return False
    except yaml.YAMLError as err:
        _LOGGER.error("Error parsing services.yaml: %s", err)
        return False

    # Service handlers
    async def async_open_karotz_tts_service(service_call: ServiceCall) -> None:
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

    async def async_open_karotz_play_sound_service(service_call: ServiceCall) -> None:
        """Handle play_sound service call."""
        sound_id = service_call.data.get("sound_id")

        if not sound_id:
            raise HomeAssistantError("sound_id is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.play_sound(sound_id)
        except Exception as err:
            raise HomeAssistantError(f"Failed to play sound: {err}")

    async def async_open_karotz_set_volume_service(service_call: ServiceCall) -> None:
        """Handle set_volume service call."""
        volume = service_call.data.get("volume")

        if volume is None:
            raise HomeAssistantError("volume is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.set_volume(volume)
        except Exception as err:
            raise HomeAssistantError(f"Failed to set volume: {err}")

    async def async_open_karotz_set_led_color_service(service_call: ServiceCall) -> None:
        """Handle set_led_color service call."""
        rgb_color = service_call.data.get("rgb_color")

        if rgb_color is None:
            raise HomeAssistantError("rgb_color is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.set_led_color(rgb_color)
        except Exception as err:
            raise HomeAssistantError(f"Failed to set LED color: {err}")

    async def async_open_karotz_set_ear_position_service(service_call: ServiceCall) -> None:
        """Handle set_ear_position service call."""
        position = service_call.data.get("position")

        if position is None:
            raise HomeAssistantError("position is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.set_ear_position_single(position)
        except Exception as err:
            raise HomeAssistantError(f"Failed to set ear position: {err}")

    async def async_open_karotz_set_mood_service(service_call: ServiceCall) -> None:
        """Handle set_mood service call."""
        mood_id = service_call.data.get("mood_id")

        if mood_id is None:
            raise HomeAssistantError("mood_id is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.set_mood(mood_id)
        except Exception as err:
            raise HomeAssistantError(f"Failed to set mood: {err}")

    async def async_open_karotz_wake_up_service(service_call: ServiceCall) -> None:
        """Handle wake_up service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.wake_up()
        except Exception as err:
            raise HomeAssistantError(f"Failed to wake up: {err}")

    async def async_open_karotz_sleep_service(service_call: ServiceCall) -> None:
        """Handle sleep service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.sleep()
        except Exception as err:
            raise HomeAssistantError(f"Failed to put to sleep: {err}")

    async def async_open_karotz_clear_cache_service(service_call: ServiceCall) -> None:
        """Handle clear_cache service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.clear_cache()
        except Exception as err:
            raise HomeAssistantError(f"Failed to clear cache: {err}")

    # Register all services with schemas from services.yaml
    if services_config:
        for service_name, service_config in services_config.items():
            # Build voluptuous schema from fields
            fields = service_config.get("fields", {})
            schema = {}
            for field_name, field_config in fields.items():
                required = field_config.get("required", False)
                # Use the field name as the schema key
                if required:
                    schema[vol.Required(field_name)] = str
                else:
                    schema[vol.Optional(field_name)] = str
            
            # Create voluptuous schema
            service_schema = vol.Schema(schema)
            
            if service_name == "tts":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_tts_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "play_sound":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_play_sound_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "set_volume":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_set_volume_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "set_led_color":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_set_led_color_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "set_ear_position":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_set_ear_position_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "set_mood":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_set_mood_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "wake_up":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_wake_up_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "sleep":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_sleep_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "clear_cache":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_clear_cache_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
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