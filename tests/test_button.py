"""Tests for Open Karotz button platform."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.open_karotz.button import OpenKarotzClearCacheButton


@pytest.fixture
def entry():
    """Create a config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


def test_button_initial_state():
    """Test button initial state."""
    button = OpenKarotzClearCacheButton("192.168.1.70", "test_id")
    
    assert button.name == "Open Karotz Clear Cache"


async def test_button_press_success():
    """Test button press with success."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        button = OpenKarotzClearCacheButton("192.168.1.70", "test_id")
        await button.async_press()
        
        assert button.name == "Open Karotz Clear Cache"


async def test_button_press_failure():
    """Test button press with failure."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        button = OpenKarotzClearCacheButton("192.168.1.70", "test_id")
        await button.async_press()
        
        assert button.name == "Open Karotz Clear Cache"