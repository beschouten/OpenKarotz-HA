"""Tests for Open Karotz binary sensor platform."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.open_karotz.binary_sensor import OpenKarotzRfidSensor


@pytest.fixture
def entry():
    """Create a config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


def test_rfid_initial_state():
    """Test RFID sensor initial state."""
    sensor = OpenKarotzRfidSensor("192.168.1.70", "test_id")
    
    assert sensor.is_on is False
    assert sensor.extra_state_attributes == {"tag_id": None}


async def test_rfid_update_with_tag():
    """Test RFID sensor update with tag."""
    mock_response = {"rfids": [{"tag": "1234567890"}]}
    
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = MagicMock(return_value=mock_response)
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        sensor = OpenKarotzRfidSensor("192.168.1.70", "test_id")
        await sensor.async_update()
        
        assert sensor.is_on is True
        assert sensor.extra_state_attributes["tag_id"] == "1234567890"


async def test_rfid_update_no_tag():
    """Test RFID sensor update with no tag."""
    mock_response = {"rfids": []}
    
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = MagicMock(return_value=mock_response)
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        sensor = OpenKarotzRfidSensor("192.168.1.70", "test_id")
        await sensor.async_update()
        
        assert sensor.is_on is False
        assert sensor.extra_state_attributes is None


async def test_rfid_update_failure():
    """Test RFID sensor update with failure."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        sensor = OpenKarotzRfidSensor("192.168.1.70", "test_id")
        await sensor.async_update()
        
        assert sensor.is_on is False
        assert sensor.extra_state_attributes is None