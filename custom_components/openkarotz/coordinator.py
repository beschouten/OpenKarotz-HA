"""OpenKarotz data coordinator for state management."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OpenKarotzAPI
from .const import (
    ATTR_API_VERSION,
    ATTR_CONNECTION_STATUS,
    ATTR_ERROR_MESSAGE,
    ATTR_DEVICE_ID,
    ATTR_LAST_UPDATE,
)

_LOGGER = logging.getLogger(__name__)


class OpenKarotzCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator for OpenKarotz data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: OpenKarotzAPI,
        update_interval: int = 30,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="OpenKarotz",
            update_interval=timedelta(seconds=update_interval),
        )
        self.api = api
        self._device_info: Optional[Dict[str, Any]] = None
        self._device_state: Optional[Dict[str, Any]] = None
        self._led_state: Optional[Dict[str, Any]] = None
        self._ears_state: Optional[Dict[str, Any]] = None
        self._rfid_state: Optional[Dict[str, Any]] = None
        self._tts_state: Optional[Dict[str, Any]] = None
        self._pictures: Optional[Dict[str, Any]] = None
        self._sounds: Optional[Dict[str, Any]] = None
        self._apps: Optional[Dict[str, Any]] = None

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from OpenKarotz API."""
        try:
            # Fetch only working data in parallel
            info_task = self.api.get_info()
            state_task = self.api.get_state()
            leds_task = self.api.get_leds()
            ears_task = self.api.get_ears()
            tts_task = self.api.get_tts()
            apps_task = self.api.get_apps()

            info, state, leds, ears, tts, apps = await asyncio.gather(
                info_task,
                state_task,
                leds_task,
                ears_task,
                tts_task,
                apps_task,
                return_exceptions=True,
            )

            # Handle any errors
            errors = {}
            if isinstance(info, Exception):
                errors["info"] = str(info)
                info = {}
            if isinstance(state, Exception):
                errors["state"] = str(state)
                state = {}
            if isinstance(leds, Exception):
                errors["leds"] = str(leds)
                leds = {}
            if isinstance(ears, Exception):
                errors["ears"] = str(ears)
                ears = {}
            if isinstance(rfid, Exception):
                errors["rfid"] = str(rfid)
                rfid = {}
            if isinstance(tts, Exception):
                errors["tts"] = str(tts)
                tts = {}
            if isinstance(pictures, Exception):
                errors["pictures"] = str(pictures)
                pictures = {}
            if isinstance(sounds, Exception):
                errors["sounds"] = str(sounds)
                sounds = {}
            if isinstance(apps, Exception):
                errors["apps"] = str(apps)
                apps = {}

            # Update state variables
            self._device_info = info
            # Use info for state since get_state returns same data
            self._device_state = info
            self._led_state = leds
            self._ears_state = ears
            self._tts_state = tts
            self._apps = apps

            # Check connection status
            connection_status = "connected" if not errors else "disconnected"

            # Build response data
            data = {
                "id": info.get("id", info.get("wlan_mac", "unknown")),
                "version": info.get("version", "unknown"),
                ATTR_LAST_UPDATE: datetime.now().isoformat(),
                ATTR_CONNECTION_STATUS: connection_status,
                ATTR_ERROR_MESSAGE: str(errors) if errors else None,
                "info": info,
                "state": state,
                "leds": leds,
                "ears": ears,
                "tts": tts,
                "moods": apps,
            }

            if errors:
                _LOGGER.warning(f"OpenKarotz data update had errors: {errors}")

            return data

        except Exception as e:
            _LOGGER.error(f"Error updating OpenKarotz data: {e}")
            raise UpdateFailed(f"Error updating OpenKarotz data: {e}") from e

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information."""
        if not self._device_info:
            return {}
        return {
            "name": self._device_info.get("name", "OpenKarotz"),
            "model": self._device_info.get("model", "Unknown"),
            "manufacturer": "OpenKarotz",
            "serial_number": self._device_info.get("serial", "Unknown"),
            "config_entry_id": self.config_entry.entry_id,
        }

    @property
    def device_state(self) -> Optional[Dict[str, Any]]:
        """Return current device state."""
        return self._device_state

    @property
    def leds_state(self) -> Optional[Dict[str, Any]]:
        """Return LED state."""
        return self._led_state

    @property
    def ears_state(self) -> Optional[Dict[str, Any]]:
        """Return audio player state."""
        return self._ears_state

    @property
    def rfid_state(self) -> Optional[Dict[str, Any]]:
        """Return RFID state."""
        return self._rfid_state

    @property
    def tts_state(self) -> Optional[Dict[str, Any]]:
        """Return TTS state."""
        return self._tts_state

    @property
    def pictures(self) -> Optional[Dict[str, Any]]:
        """Return pictures information."""
        return self._pictures

    @property
    def sounds(self) -> Optional[Dict[str, Any]]:
        """Return sounds information."""
        return self._sounds

    @property
    def apps(self) -> Optional[Dict[str, Any]]:
        """Return applications information."""
        return self._apps