"""Tests for Open Karotz API."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.open_karotz.api import OpenKarotzAPI


@pytest.fixture
def api():
    """Create API instance."""
    return OpenKarotzAPI("192.168.1.70")


@pytest.mark.asyncio
async def test_get_free_space_success(api):
    """Test get_free_space with successful response."""
    mock_response = {
        "karotz": {"percent_used_space": "36"},
        "usb": {"percent_used_space": "-1"}
    }
    
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await api.get_free_space()
        
        assert result is not None
        assert result["karotz"]["percent_used_space"] == "36"


@pytest.mark.asyncio
async def test_get_free_space_failure(api):
    """Test get_free_space with failed response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 404
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await api.get_free_space()
        
        assert result is None


@pytest.mark.asyncio
async def test_set_led_color_success(api):
    """Test set_led_color with successful response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await api.set_led_color("FF0000")
        
        assert result is True


@pytest.mark.asyncio
async def test_set_led_color_failure(api):
    """Test set_led_color with failed response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await api.set_led_color("FF0000")
        
        assert result is False


@pytest.mark.asyncio
async def test_play_sound_success(api):
    """Test play_sound with successful response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await api.play_sound("bip1")
        
        assert result is True


@pytest.mark.asyncio
async def test_play_sound_url_success(api):
    """Test play_sound_url with successful response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await api.play_sound_url("http://example.com/sound.mp3")
        
        assert result is True


@pytest.mark.asyncio
async def test_play_tts_success(api):
    """Test play_tts with successful response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await api.play_tts("Hello World", "1")
        
        assert result is True


@pytest.mark.asyncio
async def test_get_rfid_list_success(api):
    """Test get_rfid_list with successful response."""
    mock_response = {"tags": [], "return": "0"}
    
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await api.get_rfid_list()
        
        assert result is not None
        assert result["return"] == "0"


@pytest.mark.asyncio
async def test_clear_cache_success(api):
    """Test clear_cache with successful response."""
    with patch('homeassistant.helpers.aiohttp_client.ClientSession') as mock_session:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_resp
        
        result = await api.clear_cache()
        
        assert result is True