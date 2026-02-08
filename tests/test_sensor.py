"""Tests for Open Karotz sensor platform."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.open_karotz.sensor import (
    OpenKarotzCoordinator,
    KarotzStorageSensor,
    UsbStorageSensor,
)


@pytest.fixture
def coordinator(hass):
    """Create a coordinator instance."""
    return OpenKarotzCoordinator(hass, "192.168.1.70")


@pytest.fixture
def entry():
    """Create a config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {"host": "192.168.1.70", "name": "Open Karotz"}
    return entry


async def test_coordinator_async_update_data_success(coordinator):
    """Test coordinator data update with successful response."""
    mock_data = {
        "karotz": {"percent_used_space": 45},
        "usb": {"percent_used_space": 30}
    }
    
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_data)
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await coordinator._async_update_data()
        
        assert result is not None
        assert result["karotz"]["percent_used_space"] == 45


async def test_coordinator_async_update_data_failure(coordinator):
    """Test coordinator data update with failed response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await coordinator._async_update_data()
        
        assert result is None


async def test_coordinator_async_update_data_exception(coordinator):
    """Test coordinator data update with exception."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_session.return_value.get.return_value.__aenter__.side_effect = Exception("Connection error")
        
        result = await coordinator._async_update_data()
        
        assert result is None


def test_karotz_sensor_native_value(coordinator, entry):
    """Test Karotz sensor native value."""
    coordinator.data = {
        "karotz": {"percent_used_space": 45},
        "usb": {"percent_used_space": 30}
    }
    
    sensor = KarotzStorageSensor(coordinator, entry)
    
    assert sensor.native_value == 45


def test_karotz_sensor_no_data(coordinator, entry):
    """Test Karotz sensor with no data."""
    coordinator.data = None
    
    sensor = KarotzStorageSensor(coordinator, entry)
    
    assert sensor.native_value is None


def test_usb_sensor_native_value(coordinator, entry):
    """Test USB sensor native value."""
    coordinator.data = {
        "karotz": {"percent_used_space": 45},
        "usb": {"percent_used_space": 30}
    }
    
    sensor = UsbStorageSensor(coordinator, entry)
    
    assert sensor.native_value == 30


def test_usb_sensor_not_connected(coordinator, entry):
    """Test USB sensor when not connected."""
    coordinator.data = {
        "karotz": {"percent_used_space": 45},
        "usb": {"percent_used_space": -1}
    }
    
    sensor = UsbStorageSensor(coordinator, entry)
    
    assert sensor.native_value == -1
    assert sensor.available is False


def test_usb_sensor_available(coordinator, entry):
    """Test USB sensor when connected."""
    coordinator.data = {
        "karotz": {"percent_used_space": 45},
        "usb": {"percent_used_space": 30}
    }
    
    sensor = UsbStorageSensor(coordinator, entry)
    
    assert sensor.available is True