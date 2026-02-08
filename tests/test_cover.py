"""Tests for Open Karotz cover platform."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.open_karotz.cover import OpenKarotzEars


@pytest.fixture
def entry():
    """Create a config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


def test_ears_initial_state():
    """Test ears initial state."""
    ears = OpenKarotzEars("192.168.1.70", "test_id")
    
    assert ears.current_cover_position == 50
    assert ears.is_closed is False


async def test_ears_open():
    """Test ears open."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        ears = OpenKarotzEars("192.168.1.70", "test_id")
        await ears.async_open_cover()
        
        assert ears.current_cover_position == 100


async def test_ears_close():
    """Test ears close."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        ears = OpenKarotzEars("192.168.1.70", "test_id")
        await ears.async_close_cover()
        
        assert ears.current_cover_position == 0


async def test_ears_set_position():
    """Test ears set position."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        ears = OpenKarotzEars("192.168.1.70", "test_id")
        await ears.async_set_cover_position(position=75)
        
        assert ears.current_cover_position == 75


async def test_ears_reset():
    """Test ears reset."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        ears = OpenKarotzEars("192.168.1.70", "test_id")
        await ears.async_reset_ears()
        
        assert ears.current_cover_position == 50


async def test_ears_random():
    """Test ears random."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        ears = OpenKarotzEars("192.168.1.70", "test_id")
        await ears.async_random_ears()
        
        assert ears.current_cover_position is not None


async def test_ears_open_tilt():
    """Test ears open tilt."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        ears = OpenKarotzEars("192.168.1.70", "test_id")
        await ears.async_open_cover_tilt()
        
        assert ears.current_cover_position is not None


async def test_ears_close_tilt():
    """Test ears close tilt."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        ears = OpenKarotzEars("192.168.1.70", "test_id")
        await ears.async_close_cover_tilt()
        
        assert ears.current_cover_position is not None