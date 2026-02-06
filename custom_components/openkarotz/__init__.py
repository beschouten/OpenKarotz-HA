"""OpenKarotz Home Assistant Integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .api import OpenKarotzAPI
from .const import DOMAIN
from .coordinator import OpenKarotzCoordinator
from .services import async_setup_services
from .config_flow import OpenKarotzConfigFlow

__all__ = ["OpenKarotzConfigFlow"]

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = [
    Platform.SENSOR,
    Platform.LIGHT,
    Platform.MEDIA_PLAYER,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenKarotz from a config entry."""
    _LOGGER.info("Setting up OpenKarotz integration: %s", entry.entry_id)

    host = entry.data.get("host", "192.168.1.201")
    port = entry.data.get("port", 80)

    api = OpenKarotzAPI(host, port)

    try:
        await api.async_connect()
    except Exception as e:
        _LOGGER.error("Failed to connect to OpenKarotz: %s", e)
        return False

    coordinator = OpenKarotzCoordinator(hass, api)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenKarotz config entry."""
    _LOGGER.info("Unloading OpenKarotz integration: %s", entry.entry_id)

    if entry.entry_id in hass.data.get(DOMAIN, {}):
        api = hass.data[DOMAIN][entry.entry_id].get("api")
        if api:
            await api.async_disconnect()
        del hass.data[DOMAIN][entry.entry_id]

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old config entry to new format."""
    _LOGGER.info("Migrating configuration entry: %s from version %s", config_entry.entry_id, config_entry.version)

    if config_entry.version <= 1:
        new_data = {**config_entry.data}
        config_entry.version = 2

    return True
