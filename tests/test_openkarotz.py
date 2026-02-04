"""Integration tests for OpenKarotz Home Assistant component."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.openkarotz.api import OpenKarotzAPI, OpenKarotzConnectionError
from custom_components.openkarotz.coordinator import OpenKarotzCoordinator


@pytest.fixture
def mock_api():
    """Create a mock API instance."""
    return MagicMock(spec=OpenKarotzAPI)


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry"
    entry.data = {
        "host": "192.168.1.201",
        "port": 80
    }
    return entry


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    return hass


@pytest.mark.asyncio
async def test_api_connection_success(mock_api):
    """Test successful API connection."""
    mock_api.async_connect.return_value = True
    
    api = OpenKarotzAPI("192.168.1.201", 80)
    with patch.object(api, '_async_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"status": "ok"}
        
        connected = await api.async_connect()
        
        assert connected is True
        mock_api.async_connect.assert_called_once()


@pytest.mark.asyncio
async def test_api_connection_failure(mock_api):
    """Test failed API connection."""
    mock_api.async_connect.return_value = False
    
    api = OpenKarotzAPI("192.168.1.201", 80)
    connected = await api.async_connect()
    
    assert connected is False


@pytest.mark.asyncio
async def test_api_get_info(mock_api):
    """Test getting device information."""
    mock_api.get_info.return_value = {
        "name": "Test Device",
        "model": "OpenKarotz v1.0",
        "serial": "ABC123"
    }
    
    info = await mock_api.get_info()
    
    assert info["name"] == "Test Device"
    assert info["model"] == "OpenKarotz v1.0"
    mock_api.get_info.assert_called_once()


@pytest.mark.asyncio
async def test_api_set_led(mock_api):
    """Test setting LED configuration."""
    mock_api.set_led.return_value = {"status": "ok", "led": "red"}
    
    result = await mock_api.set_led(color="red", brightness=80)
    
    assert result["status"] == "ok"
    mock_api.set_led.assert_called_once_with(color="red", brightness=80)


@pytest.mark.asyncio
async def test_api_play_audio(mock_api):
    """Test playing audio."""
    mock_api.play_audio.return_value = {"status": "ok", "source": "alarm"}
    
    result = await mock_api.play_audio(source="alarm", category="notification")
    
    assert result["status"] == "ok"
    mock_api.play_audio.assert_called_once_with(source="alarm", category="notification")


@pytest.mark.asyncio
async def test_api_stop_audio(mock_api):
    """Test stopping audio."""
    mock_api.stop_audio.return_value = {"status": "ok"}
    
    result = await mock_api.stop_audio(source="alarm")
    
    assert result["status"] == "ok"
    mock_api.stop_audio.assert_called_once_with(source="alarm")


@pytest.mark.asyncio
async def test_api_set_volume(mock_api):
    """Test setting volume."""
    mock_api.set_volume.return_value = {"status": "ok", "volume": 75}
    
    result = await mock_api.set_volume(75)
    
    assert result["volume"] == 75
    mock_api.set_volume.assert_called_once_with(75)


@pytest.mark.asyncio
async def test_coordinator_update(mock_api):
    """Test coordinator data update."""
    coordinator = OpenKarotzCoordinator(MagicMock(), mock_api)
    
    mock_api.get_info.return_value = {"name": "Test"}
    mock_api.get_state.return_value = {"state": "running"}
    mock_api.get_leds.return_value = {"leds": [{"id": 1, "name": "Main"}]}
    mock_api.get_ears.return_value = {"ears": [{"id": 1, "name": "Speaker"}]}
    mock_api.get_rfid.return_value = {"rfid_enabled": True}
    mock_api.get_tts.return_value = {"tts_enabled": True}
    mock_api.get_pictures.return_value = {"pictures": []}
    mock_api.get_sounds.return_value = {"sounds": []}
    mock_api.get_apps.return_value = {"apps": []}
    
    data = await coordinator._async_update_data()
    
    assert data["info"]["name"] == "Test"
    assert data["state"]["state"] == "running"


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_coordinator_device_info(mock_api):
    """Test coordinator device info property."""
    mock_api.get_info.return_value = {
        "name": "Test Device",
        "model": "OpenKarotz",
        "serial": "ABC123"
    }
    
    coordinator = OpenKarotzCoordinator(MagicMock(), mock_api)
    await coordinator._async_update_data()
    
    device_info = coordinator.device_info
    
    assert device_info["name"] == "Test Device"
    assert device_info["model"] == "OpenKarotz"
    assert device_info["manufacturer"] == "OpenKarotz"


@pytest.mark.asyncio
def test_constants_defined():
    """Test that all required constants are defined."""
    from custom_components.openkarotz import const
    
    assert hasattr(const, 'DOMAIN')
    assert hasattr(const, 'DEFAULT_PORT')
    assert hasattr(const, 'DEFAULT_TIMEOUT')
    assert hasattr(const, 'SERVICE_NAMES')
    assert hasattr(const, 'SERVICE_DATA_SCHEMAS')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])