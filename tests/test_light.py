"""Tests for Open Karotz light platform."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.open_karotz.light import OpenKarotzLed


@pytest.fixture
def entry():
    """Create a config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


def test_led_initial_state():
    """Test LED initial state."""
    led = OpenKarotzLed("192.168.1.70", "test_id")
    
    assert led.is_on is False
    assert led.rgb_color == (0, 0, 0)


def test_led_rgb_color_property():
    """Test LED RGB color property."""
    led = OpenKarotzLed("192.168.1.70", "test_id")
    led._rgb_color = (255, 128, 64)
    
    assert led.rgb_color == (255, 128, 64)


async def test_led_turn_on():
    """Test LED turn on."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        led = OpenKarotzLed("192.168.1.70", "test_id")
        await led.async_turn_on(rgb_color=(255, 0, 0))
        
        assert led.is_on is True
        assert led.rgb_color == (255, 0, 0)


async def test_led_turn_off():
    """Test LED turn off."""
    led = OpenKarotzLed("192.168.1.70", "test_id")
    led._rgb_color = (255, 255, 255)
    led._attr_is_on = True
    
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        await led.async_turn_off()
        
        assert led.is_on is False
        assert led.rgb_color == (0, 0, 0)


async def test_led_turn_on_failure():
    """Test LED turn on with failed response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        led = OpenKarotzLed("192.168.1.70", "test_id")
        await led.async_turn_on(rgb_color=(255, 0, 0))
        
        assert led.is_on is True
        assert led.rgb_color == (255, 0, 0)