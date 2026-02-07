"""OpenKarotz media player."""

import logging

from homeassistant.components.media_player import (
    ATTR_MEDIA_DURATION,
    ATTR_MEDIA_POSITION,
    ATTR_MEDIA_TITLE,
    ATTR_MEDIA_URI,
    MEDIA_TYPE_MUSIC,
    MEDIA_TYPE_UNKNOWN,
    MediaPlayerEntity,
    MediaPlayerEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import OpenKarotzAPI
from .coordinator import OpenKarotzCoordinator
from .const import DOMAIN, MEDIA_PLAYER_ATTRIBUTES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenKarotz media players."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []

    # Get ears (audio player) state
    ears_state = coordinator.ears_state or {}
    ears = ears_state.get("ears", [])
    if not ears:
        ears = [{"id": 1, "name": "Main Speaker", "enabled": True}]

    for ear in ears:
        entities.append(OpenKarotzMediaPlayer(coordinator, ear))

    async_add_entities(entities)


class OpenKarotzMediaPlayer(CoordinatorEntity[OpenKarotzCoordinator], MediaPlayerEntity):
    """Media player entity for OpenKarotz ears."""

    entity_description = MediaPlayerEntityDescription(
        key="ear",
        name="Audio Player",
    )

    def __init__(self, coordinator: OpenKarotzCoordinator, ear_data: dict) -> None:
        """Initialize media player entity."""
        super().__init__(coordinator)
        self.ear_data = ear_data
        ear_id = ear_data.get("id", 1)
        self._attr_unique_id = f"{coordinator.data.get('info', {}).get('id', 'unknown')}_audio_{ear_id}"
        self._attr_name = ear_data.get("name", f"Audio Player {ear_id}")
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Check if entity is available."""
        return self.coordinator.data.get(ATTR_CONNECTION_STATUS) == "connected"

    @property
    def supported_features(self) -> int:
        """Return supported features."""
        features = 0
        ears_state = self.coordinator.ears_state or {}
        if ears_state.get("volume"):
            features |= self.SUPPORT_VOLUME_SET | self.SUPPORT_VOLUME_STEP
        if ears_state.get("playback"):
            features |= self.SUPPORT_PLAY_PAUSE | self.SUPPORT_STOP
        return features

    @property
    def state(self):
        """Return playback state."""
        ears_state = self.coordinator.ears_state or {}
        playback_state = ears_state.get("playback", {}).get("state", "stopped")
        return playback_state

    @property
    def media_title(self) -> str | None:
        """Return current media title."""
        ears_state = self.coordinator.ears_state or {}
        return ears_state.get("current", {}).get("title")

    @property
    def media_artist(self) -> str | None:
        """Return current media artist."""
        ears_state = self.coordinator.ears_state or {}
        return ears_state.get("current", {}).get("artist")

    @property
    def media_album_name(self) -> str | None:
        """Return current media album."""
        ears_state = self.coordinator.ears_state or {}
        return ears_state.get("current", {}).get("album")

    @property
    def media_duration(self) -> float | None:
        """Return media duration."""
        ears_state = self.coordinator.ears_state or {}
        return ears_state.get("current", {}).get("duration")

    @property
    def media_position(self) -> float | None:
        """Return media position."""
        ears_state = self.coordinator.ears_state or {}
        return ears_state.get("current", {}).get("position")

    @property
    def media_uri(self) -> str | None:
        """Return media URI."""
        ears_state = self.coordinator.ears_state or {}
        return ears_state.get("current", {}).get("uri")

    @property
    def media_type(self) -> str:
        """Return media type."""
        ears_state = self.coordinator.ears_state or {}
        current = ears_state.get("current", {})
        if current.get("type") == "music":
            return MEDIA_TYPE_MUSIC
        return MEDIA_TYPE_UNKNOWN

    @property
    def volume_level(self) -> float | None:
        """Return volume level."""
        ears_state = self.coordinator.ears_state or {}
        volume = ears_state.get("volume", 0)
        return volume / 100 if volume else None

    @property
    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self.state == "playing"

    @property
    def is_muted(self) -> bool:
        """Check if muted."""
        ears_state = self.coordinator.ears_state or {}
        return ears_state.get("muted", False)

    @property
    def device_state_attributes(self) -> dict[str, str]:
        """Return device state attributes."""
        ears_state = self.coordinator.ears_state or {}
        current = ears_state.get("current", {})
        return {
            "category": ears_state.get("category"),
            "source": ears_state.get("source"),
            "volume": ears_state.get("volume"),
            "playback_state": ears_state.get("playback", {}).get("state"),
        }

    async def async_volume_up(self) -> None:
        """Increase volume."""
        ears_state = self.coordinator.ears_state or {}
        current_volume = ears_state.get("volume", 50)
        new_volume = min(100, current_volume + 5)
        await self.coordinator.api.set_volume(new_volume)

    async def async_volume_down(self) -> None:
        """Decrease volume."""
        ears_state = self.coordinator.ears_state or {}
        current_volume = ears_state.get("volume", 50)
        new_volume = max(0, current_volume - 5)
        await self.coordinator.api.set_volume(new_volume)

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level."""
        await self.coordinator.api.set_volume(int(volume * 100))

    async def async_play_media(
        self,
        media_type: str,
        media_id: str,
        **kwargs,
    ) -> None:
        """Play media."""
        await self.coordinator.api.play_audio(
            source=media_id,
            category=kwargs.get("category"),
            volume=kwargs.get("volume"),
        )

    async def async_mute(self, mute: bool) -> None:
        """Mute/unmute."""
        ears_state = self.coordinator.ears_state or {}
        # Note: API might need mute/unmute endpoints
        _LOGGER.debug(f"Mute requested: {mute}")

    async def async_stop(self) -> None:
        """Stop playback."""
        await self.coordinator.api.stop_audio()

    async def async_pause(self) -> None:
        """Pause playback."""
        # Note: API might need pause endpoint
        _LOGGER.debug("Pause requested")

    async def async_play_pause(self) -> None:
        """Play/pause."""
        ears_state = self.coordinator.ears_state or {}
        playback_state = ears_state.get("playback", {}).get("state", "stopped")
        if playback_state == "playing":
            await self.async_pause()
        else:
            await self.async_play_media(
                media_type=MEDIA_TYPE_UNKNOWN,
                media_id="play",
            )