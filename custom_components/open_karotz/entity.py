"""Base entity for OpenKarotz devices."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import KarotzCoordinator, KarotzRuntime
from .const import DEFAULT_NAME, DOMAIN


def karotz_device_info(entry: ConfigEntry, runtime: KarotzRuntime) -> DeviceInfo:
    """Build the shared DeviceInfo from entry unique_id + version data."""
    version = runtime.version or {}
    mac = entry.unique_id or ""
    sw = " / ".join(
        str(v)
        for v in (
            version.get("version"),
            version.get("rootfs_version"),
            version.get("patch_version"),
        )
        if v
    )
    info = DeviceInfo(
        identifiers={(DOMAIN, mac or entry.entry_id)},
        manufacturer="Parrot",
        model="Karotz",
        name=entry.data.get("name", DEFAULT_NAME),
    )
    if sw:
        info["sw_version"] = sw
    if mac:
        info["connections"] = {(CONNECTION_NETWORK_MAC, mac)}
    return info


class OpenKarotzEntity(CoordinatorEntity[KarotzCoordinator]):
    """Coordinator-backed base entity."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, runtime: KarotzRuntime, key: str) -> None:
        super().__init__(runtime.coordinator)
        self._entry = entry
        self._runtime = runtime
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_{key}"
        self._attr_device_info = karotz_device_info(entry, runtime)

    @property
    def status(self) -> dict:
        return self.coordinator.data or {}
