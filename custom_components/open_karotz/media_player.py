"""Media player platform for Open Karotz."""
from __future__ import annotations

import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BASE_URL, DOMAIN, SOUND_LIST

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz media player entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzMediaPlayer(host, entry.entry_id)])


class OpenKarotzMediaPlayer(MediaPlayerEntity):
    """Representation of the Open Karotz media player."""

    _attr_name = "Open Karotz"
    _attr_media_content_type = MediaType.MUSIC
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY_MEDIA
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.VOLUME_SET
    )
    _attr_translation_key = "media_player"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the media player."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_media_player"
        self._state = MediaPlayerState.IDLE
        self._volume = 0.5
        self._title = None
        self._source = None

    async def _async_send_command(self, endpoint: str) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}{endpoint}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to send command: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    async def _async_play_local(self, sound_id: str) -> bool:
        """Play local sound."""
        return await self._async_send_command(f"/cgi-bin/sound?id={sound_id}")

    async def _async_play_url(self, url: str) -> bool:
        """Play sound from URL."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/sound?url={url}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to play URL: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error playing URL: %s", err)
            return False

    async def _async_tts(self, text: str, voice: str = "1") -> bool:
        """Play text-to-speech."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/tts?text={text}&voice={voice}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to play TTS: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error playing TTS: %s", err)
            return False

    async def _async_stop(self) -> bool:
        """Stop playback."""
        return await self._async_send_command("/cgi-bin/stop")

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the media player."""
        return self._state

    @property
    def volume_level(self) -> float | None:
        """Return the volume level."""
        return self._volume

    @property
    def media_title(self) -> str | None:
        """Return the media title."""
        return self._title

    async def async_update(self) -> None:
        """Update the entity status."""
        pass

    async def async_media_play(self) -> None:
        """Play media."""
        self._state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_media_stop(self) -> None:
        """Stop media."""
        await self._async_stop()
        self._state = MediaPlayerState.IDLE
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level."""
        self._volume = volume

    async def async_play_media(
        self, media_type: str | None, media_id: str | None, **kwargs
    ) -> None:
        """Play media."""
        if media_type == MediaType.MUSIC and media_id:
            if media_id in SOUND_LIST:
                await self._async_play_local(media_id)
                self._title = f"Sound {media_id}"
                self._state = MediaPlayerState.PLAYING
                self.async_write_ha_state()
            else:
                _LOGGER.warning("Invalid sound ID: %s", media_id)

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        self._source = source
