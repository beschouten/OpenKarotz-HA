"""OpenKarotz integration setup."""
from __future__ import annotations

import functools
import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any
from urllib.parse import quote

import voluptuous as vol
from aiohttp import web
from aiohttp.web_request import Request
from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
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
    Platform.BUTTON,
    Platform.CAMERA,
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
    _register_rfid_webhook(hass, entry, runtime)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    _register_services(hass)
    _register_rfid_services(hass)
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


# --------------------------------------------------------------------- rfid
EVENT_RFID_TAG_SCANNED = f"{DOMAIN}_tag_scanned"

_DEVICE_SCHEMA = vol.Schema({vol.Required("device_id"): str})
_TAG_SCHEMA = _DEVICE_SCHEMA.extend({vol.Required("tag"): vol.All(str, vol.Length(min=1))})
_RENAME_SCHEMA = _TAG_SCHEMA.extend(
    {vol.Optional("name"): str, vol.Optional("color"): vol.All(str, vol.Length(min=2, max=2))}
)


def _register_rfid_webhook(
    hass: HomeAssistant, entry: OpenKarotzConfigEntry, runtime: KarotzRuntime
) -> None:
    """Register the per-entry RFID webhook.

    Tags are pointed here with rfid_assign_url; when a tag is scanned the
    Karotz GETs the URL and we re-fire it as an HA event. Dormant until a
    tag is assigned — zero cost otherwise.
    """
    webhook_id = entry.entry_id

    async def handle_scan(
        hass: HomeAssistant, webhook_id: str, request: Request
    ) -> web.Response:
        tag = request.query.get("tag", "")
        name = ""
        if tag:
            try:
                info = await runtime.api.rfid_info(tag)
                name = str(info.get("name") or "")
            except OpenKarotzError:
                pass
        device_id = None
        mac = entry.unique_id
        if mac:
            dev = async_get_device_registry(hass).async_get_device_by_identifier(
                (DOMAIN, mac), entry.entry_id
            )
            device_id = dev.id if dev else None
        hass.bus.async_fire(
            EVENT_RFID_TAG_SCANNED,
            {
                "tag_id": tag,
                "name": name,
                "host": runtime.api.host,
                "config_entry_id": entry.entry_id,
                "device_id": device_id,
            },
        )
        return web.Response(text="ok")

    webhook.async_register(
        hass, DOMAIN, f"OpenKarotz RFID {runtime.api.host}", webhook_id, handle_scan,
        allowed_methods={"GET", "POST"},  # the Karotz GETs the assigned URL on scan
    )
    entry.async_on_unload(functools.partial(webhook.async_unregister, hass, webhook_id))


def _runtime_for_device(hass: HomeAssistant, device_id: str) -> KarotzRuntime:
    """Resolve a device_id selector to the entry runtime."""
    dev = async_get_device_registry(hass).async_get(device_id)
    if dev is None:
        raise HomeAssistantError(f"Unknown device: {device_id}")
    entry = hass.config_entries.async_get_entry(dev.config_entry_id or "")
    if entry and entry.domain == DOMAIN and getattr(entry, "runtime_data", None):
        return entry.runtime_data
    raise HomeAssistantError(f"Device {device_id} is not an OpenKarotz device")


def _guard(fn):
    """Surface device refusals as clean service errors (400, not 500)."""

    @functools.wraps(fn)
    async def wrapper(call: ServiceCall) -> None:
        try:
            await fn(call)
        except OpenKarotzError as err:
            raise HomeAssistantError(str(err)) from err

    return wrapper


def _register_rfid_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, "rfid_start_record"):
        return

    async def handle_start_record(call: ServiceCall) -> None:
        runtime = _runtime_for_device(hass, call.data["device_id"])
        await runtime.api.rfid_start_record()  # fire-and-forget (EarsReset family)

    @_guard
    async def handle_stop_record(call: ServiceCall) -> None:
        runtime = _runtime_for_device(hass, call.data["device_id"])
        await runtime.api.rfid_stop_record()

    @_guard
    async def handle_rename(call: ServiceCall) -> None:
        runtime = _runtime_for_device(hass, call.data["device_id"])
        await runtime.api.rfid_rename(
            call.data["tag"], name=call.data.get("name"), color=call.data.get("color")
        )

    @_guard
    async def handle_delete(call: ServiceCall) -> None:
        runtime = _runtime_for_device(hass, call.data["device_id"])
        await runtime.api.rfid_delete(call.data["tag"])

    @_guard
    async def handle_assign_webhook(call: ServiceCall) -> None:
        """Point a tag's action at our webhook so scans fire events."""
        runtime = _runtime_for_device(hass, call.data["device_id"])
        entry = next(
            e for e in hass.config_entries.async_entries(DOMAIN)
            if getattr(e, "runtime_data", None) is runtime
        )
        url = (
            webhook.async_generate_url(hass, entry.entry_id)
            + f"?tag={quote(call.data['tag'])}"
        )
        await runtime.api.rfid_assign_url(
            tag=call.data["tag"], url=url, name=call.data.get("name")
        )

    hass.services.async_register(
        DOMAIN, "rfid_start_record", handle_start_record, schema=_DEVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "rfid_stop_record", handle_stop_record, schema=_DEVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "rfid_rename", handle_rename, schema=_RENAME_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "rfid_delete", handle_delete, schema=_TAG_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        "rfid_assign_webhook",
        handle_assign_webhook,
        schema=_TAG_SCHEMA.extend({vol.Optional("name"): str}),
    )

