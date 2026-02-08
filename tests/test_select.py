"""Tests for Open Karotz select platform."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.open_karotz.select import OpenKarotzMood


@pytest.fixture
def entry():
    """Create a config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


def test_mood_initial_state():
    """Test mood initial state."""
    mood = OpenKarotzMood("192.168.1.70", "test_id")
    
    assert mood.current_option == "1"
    assert len(mood.options) == 50


async def test_mood_select_option():
    """Test mood select option."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        mood = OpenKarotzMood("192.168.1.70", "test_id")
        await mood.async_select_option("5")
        
        assert mood.current_option == "5"


async def test_mood_select_invalid_option():
    """Test mood select invalid option."""
    mood = OpenKarotzMood("192.168.1.70", "test_id")
    
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        await mood.async_select_option("999")
        
        assert mood.current_option == "1"


async def test_mood_play_random():
    """Test mood play random."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        mood = OpenKarotzMood("192.168.1.70", "test_id")
        await mood.async_play_random()
        
        assert mood.current_option is not None