"""Button platform for Open Karotz actions."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BASE_URL, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz button entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([
        OpenKarotzClearCacheButton(host, entry.entry_id),
    ])


class OpenKarotzClearCacheButton(ButtonEntity):
    """Representation of the Open Karotz clear cache button."""

    _attr_name = "Open Karotz Clear Cache"
    _attr_translation_key = "clear_cache"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the clear cache button."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_clear_cache"

    async def _async_send_command(self, endpoint: str) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}{endpoint}") as resp:
                if resp.status == 200:
                    return True
                return False
        except Exception:
            return False

    async def async_press(self) -> None:
        """Press the button."""
        await self._async_send_command("/cgi-bin/clear_cache")