"""Diagnostics support for OpenKarotz."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from . import KarotzRuntime

type OpenKarotzConfigEntry = ConfigEntry[KarotzRuntime]

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: OpenKarotzConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime: KarotzRuntime | None = getattr(entry, "runtime_data", None)
    if runtime is None:
        return {"state": "not_loaded"}
    coord = runtime.coordinator
    ts = getattr(coord, "last_successful_update", None) or getattr(
        coord, "last_update_time", None
    )
    return {
        "host": entry.data[CONF_HOST],
        "poll_interval_seconds": (
            coord.update_interval.total_seconds() if coord.update_interval else None
        ),
        "last_update_success": coord.last_update_success,
        "poll_count": coord.poll_count,
        "last_update_time": ts.isoformat() if ts else None,
        "last_status": coord.data,
        "version_info": runtime.version,
    }
