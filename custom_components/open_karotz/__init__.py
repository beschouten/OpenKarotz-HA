"""OpenKarotz integration setup."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OpenKarotzAPI, OpenKarotzConnectionError, OpenKarotzError
from .const import (
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Platforms are added in phases P2-P5 of the v4 plan.
PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.MEDIA_PLAYER,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TTS,
]

type OpenKarotzConfigEntry = ConfigEntry[KarotzRuntime]


@dataclass
class KarotzRuntime:
    """Runtime data per config entry."""

    api: OpenKarotzAPI
    coordinator: "KarotzCoordinator"
    version: dict[str, Any] = field(default_factory=dict)
    capabilities: dict[str, bool] = field(default_factory=dict)


class KarotzCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls /cgi-bin/status — the single source of device state."""

    config_entry: OpenKarotzConfigEntry

    def __init__(self, hass: HomeAssistant, api: OpenKarotzAPI, entry: OpenKarotzConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"OpenKarotz {api.host}",
            update_interval=None,  # set in async_setup_entry from options
        )
        self.api = api
        self.poll_count = 0

    async def _async_update_data(self) -> dict[str, Any]:
        self.poll_count += 1
        try:
            return await self.api.get_status()
        except OpenKarotzConnectionError as err:
            raise UpdateFailed(f"Karotz unreachable: {err}") from err
        except OpenKarotzError as err:
            raise UpdateFailed(f"Karotz error: {err}") from err


async def async_setup_entry(hass: HomeAssistant, entry: OpenKarotzConfigEntry) -> bool:
    """Set up OpenKarotz from a config entry."""
    host = entry.data[CONF_HOST]
    api = OpenKarotzAPI(host, async_get_clientsession(hass))

    coordinator = KarotzCoordinator(hass, api, entry)
    poll = entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
    coordinator.update_interval = timedelta(seconds=max(30, int(poll)))

    try:
        status = await api.get_status()
        version = await api.get_version()
    except OpenKarotzConnectionError as err:
        raise ConfigEntryNotReady(f"Karotz at {host} unreachable") from err

    runtime = KarotzRuntime(api=api, coordinator=coordinator, version=version)
    entry.runtime_data = runtime

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    _register_services(hass)
    _LOGGER.debug("OpenKarotz %s online: %s", host, status.get("version"))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: OpenKarotzConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: OpenKarotzConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate v1 -> v2: backfill unique_id from the device MAC."""
    if entry.version == 2 and entry.minor_version == 1:
        return True
    if entry.version > 2:
        return False

    host = entry.data.get(CONF_HOST)
    unique_id = entry.unique_id
    if host and not unique_id:
        api = OpenKarotzAPI(host, async_get_clientsession(hass))
        try:
            status = await api.get_status()
            mac = status.get("wlan_mac") or status.get("eth_mac")
            if mac and mac != "00:00:00:00:00:00":
                unique_id = mac
        except OpenKarotzError:
            _LOGGER.info("Migration: device offline, unique_id will be set on next reload")

    hass.config_entries.async_update_entry(
        entry, version=2, minor_version=1, unique_id=unique_id
    )
    _LOGGER.info("Config entry %s migrated to version 2", entry.entry_id)
    return True


# ----------------------------------------------------------------- services
_SERVICE_TTS_SCHEMA = vol.Schema(
    {
        vol.Required("text"): vol.All(str, vol.Length(min=1)),
        vol.Optional("voice"): str,
    }
)

def _register_services(hass: HomeAssistant) -> None:
    """Register the legacy-compatible tts service (idempotent).

    Kept for backward compatibility with v3 automations; entity-based
    targeting lands with the tts platform in P3.
    """
    if hass.services.has_service(DOMAIN, "tts"):
        return

    async def handle_tts(call: ServiceCall) -> None:
        text = call.data["text"]
        voice = call.data.get("voice")
        errors = []
        for entry in hass.config_entries.async_entries(DOMAIN):
            runtime: KarotzRuntime | None = getattr(entry, "runtime_data", None)
            if runtime is None:
                continue
            try:
                await runtime.api.tts(text, voice=voice)
            except OpenKarotzError as err:
                errors.append(str(err))
        if errors:
            raise HomeAssistantError("; ".join(errors))

    hass.services.async_register(DOMAIN, "tts", handle_tts, schema=_SERVICE_TTS_SCHEMA)

