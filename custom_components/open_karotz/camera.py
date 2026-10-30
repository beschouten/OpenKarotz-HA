"""Camera platform: snapshots via snapshot -> snapshot_get (the snapshot CGI
returns JSON metadata, not image bytes)."""
from __future__ import annotations

import logging

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KarotzRuntime
from .api import OpenKarotzError
from .entity import OpenKarotzEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the camera from a config entry."""
    runtime: KarotzRuntime = entry.runtime_data
    async_add_entities([KarotzCamera(entry, runtime)])


class KarotzCamera(OpenKarotzEntity, Camera):
    """Still-camera: each image request triggers a fresh snapshot."""

    _attr_translation_key = "camera"

    def __init__(self, entry: ConfigEntry, runtime: KarotzRuntime) -> None:
        super().__init__(entry, runtime, "camera")
        Camera.__init__(self)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        # The snapshot CGI is flaky on this firmware (occasionally emits the
        # raw D-Bus reply instead of HTTP/JSON) — retry once.
        for attempt in (1, 2):
            try:
                meta = await self._runtime.api.snapshot()
                filename = meta.get("filename")
                if not filename:
                    _LOGGER.debug("Snapshot returned no filename: %s", meta)
                    continue
                return await self._runtime.api.snapshot_get(filename)
            except OpenKarotzError as err:
                _LOGGER.debug("Snapshot attempt %d failed: %s", attempt, err)
        return None
