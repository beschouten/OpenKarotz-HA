"""Button platform: maintenance actions."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import KarotzRuntime
from .api import OpenKarotzError
from .entity import OpenKarotzEntity


@dataclass(frozen=True, kw_only=True)
class KarotzButtonDescription(ButtonEntityDescription):
    """Button bound to an API coroutine."""

    action: Callable = lambda api: api.clear_cache()


DESCRIPTIONS: tuple[KarotzButtonDescription, ...] = (
    KarotzButtonDescription(
        key="setclock",
        translation_key="setclock",
        action=lambda api: api.setclock(),
    ),
    KarotzButtonDescription(
        key="clear_cache",
        translation_key="clear_cache",
        action=lambda api: api.clear_cache(),
    ),
    KarotzButtonDescription(
        key="reboot",
        translation_key="reboot",
        action=lambda api: api.reboot(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up buttons from a config entry."""
    runtime: KarotzRuntime = entry.runtime_data
    async_add_entities(
        [KarotzButton(entry, runtime, desc) for desc in DESCRIPTIONS]
    )


class KarotzButton(OpenKarotzEntity, ButtonEntity):
    """One-shot maintenance action."""

    entity_description: KarotzButtonDescription

    def __init__(
        self, entry: ConfigEntry, runtime: KarotzRuntime,
        description: KarotzButtonDescription,
    ) -> None:
        super().__init__(entry, runtime, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        try:
            await self.entity_description.action(self._runtime.api)
        except OpenKarotzError as err:
            raise HomeAssistantError(
                f"{self.entity_description.key} failed: {err}"
            ) from err
