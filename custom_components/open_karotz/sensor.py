"""Sensor platform for OpenKarotz."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KarotzRuntime
from .entity import OpenKarotzEntity


def _int(value: str | None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True, kw_only=True)
class KarotzSensorDescription(SensorEntityDescription):
    """Sensor description bound to a status key."""

    value: Callable[[dict], object] = lambda s: s  # noqa: E731


DESCRIPTIONS: tuple[KarotzSensorDescription, ...] = (
    KarotzSensorDescription(
        key="karotz_storage",
        translation_key="karotz_storage",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value=lambda s: _int(s.get("karotz_percent_used_space")),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KarotzSensorDescription(
        key="usb_storage",
        translation_key="usb_storage",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        # "" or "-1" when no USB drive mounted -> unavailable
        value=lambda s: (
            v if (v := _int(s.get("usb_percent_used_space"))) not in (None, -1) else None
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KarotzSensorDescription(
        key="karotz_free_space",
        translation_key="karotz_free_space",
        value=lambda s: s.get("karotz_free_space") or None,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KarotzSensorDescription(
        key="tts_cache_size",
        translation_key="tts_cache_size",
        state_class=SensorStateClass.MEASUREMENT,
        value=lambda s: _int(s.get("tts_cache_size")),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KarotzSensorDescription(
        key="sleep_time",
        translation_key="sleep_time",
        value=lambda s: _int(s.get("sleep_time")),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KarotzSensorDescription(
        key="nb_moods",
        translation_key="nb_moods",
        state_class=SensorStateClass.TOTAL,
        value=lambda s: _int(s.get("nb_moods")),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KarotzSensorDescription(
        key="nb_sounds",
        translation_key="nb_sounds",
        state_class=SensorStateClass.TOTAL,
        value=lambda s: _int(s.get("nb_sounds")),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KarotzSensorDescription(
        key="nb_stories",
        translation_key="nb_stories",
        state_class=SensorStateClass.TOTAL,
        value=lambda s: _int(s.get("nb_stories")),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KarotzSensorDescription(
        key="nb_tags",
        translation_key="nb_tags",
        state_class=SensorStateClass.TOTAL,
        value=lambda s: _int(s.get("nb_tags")),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    runtime: KarotzRuntime = entry.runtime_data
    async_add_entities(
        [
            KarotzSensor(entry, runtime, desc)
            for desc in DESCRIPTIONS
        ]
        + [
            KarotzVersionSensor(entry, runtime, "web_version", "version", "Web"),
            KarotzVersionSensor(
                entry, runtime, "rootfs_version", "rootfs_version", "Rootfs"
            ),
            KarotzVersionSensor(
                entry, runtime, "patch_version", "patch_version", "Patch"
            ),
        ]
    )


class KarotzSensor(OpenKarotzEntity, SensorEntity):
    """Sensor fed by a key of the status payload."""

    entity_description: KarotzSensorDescription

    def __init__(
        self, entry, runtime: KarotzRuntime, description: KarotzSensorDescription
    ) -> None:
        super().__init__(entry, runtime, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        return self.entity_description.value(self.status)


class KarotzVersionSensor(OpenKarotzEntity, SensorEntity):
    """Firmware version sensors (static, from get_version)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, entry, runtime: KarotzRuntime, key: str, version_key: str, label: str
    ) -> None:
        super().__init__(entry, runtime, key)
        self._version_key = version_key
        self._attr_translation_key = key
        self._attr_translation_placeholders = {"label": label}

    @property
    def available(self) -> bool:
        return bool(self._runtime.version)

    @property
    def native_value(self):
        return (self._runtime.version or {}).get(self._version_key)
