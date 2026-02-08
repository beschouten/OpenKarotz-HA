"""Tests for Open Karotz switch platform."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.open_karotz.switch import OpenKarotzSleepSwitch


@pytest.fixture
def entry():
    """Create a config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


def test_switch_initial_state():
    """Test switch initial state."""
    switch = OpenKarotzSleepSwitch("192.168.1.70", "test_id")
    
    assert switch.is_on is False


async def test_switch_turn_on():
    """Test switch turn on."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        switch = OpenKarotzSleepSwitch("192.168.1.70", "test_id")
        await switch.async_turn_on()
        
        assert switch.is_on is True


async def test_switch_turn_off():
    """Test switch turn off."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        switch = OpenKarotzSleepSwitch("192.168.1.70", "test_id")
        switch._is_on = True
        await switch.async_turn_off()
        
        assert switch.is_on is False


async def test_switch_turn_on_failure():
    """Test switch turn on with failed response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        switch = OpenKarotzSleepSwitch("192.168.1.70", "test_id")
        await switch.async_turn_on()
        
        assert switch.is_on is True


async def test_switch_turn_off_failure():
    """Test switch turn off with failed response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        switch = OpenKarotzSleepSwitch("192.168.1.70", "test_id")
        switch._is_on = True
        await switch.async_turn_off()
        
        assert switch.is_on is False