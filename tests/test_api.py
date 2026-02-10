"""Tests for Open Karotz API."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.open_karotz.api import OpenKarotzAPI


class AsyncContextManagerMock(MagicMock):
    """MagicMock that can be used as async context manager."""
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        pass


@pytest.fixture
def api():
    """Create API instance with mocked session."""
    mock_session = MagicMock()
    mock_resp = AsyncContextManagerMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={})
    mock_resp.text = AsyncMock(return_value="")
    mock_resp.read = AsyncMock(return_value=b"")
    type(mock_resp).headers = {"Content-Type": "application/json"}
    mock_session.get.return_value = AsyncContextManagerMock()
    mock_session.get.return_value.__aenter__.return_value = mock_resp
    return OpenKarotzAPI("192.168.1.70", websession=mock_session)


@pytest.mark.asyncio
async def test_get_free_space_success(api):
    """Test get_free_space with successful response."""
    mock_response = {
        "karotz": {"percent_used_space": "36"},
        "usb": {"percent_used_space": "-1"}
    }
    
    mock_resp = AsyncContextManagerMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=mock_response)
    mock_resp.text = AsyncMock(return_value="")
    mock_resp.read = AsyncMock(return_value=b"")
    type(mock_resp).headers = {"Content-Type": "application/json"}
    api._websession.get.return_value = AsyncContextManagerMock()
    api._websession.get.return_value.__aenter__.return_value = mock_resp
    
    result = await api.get_free_space()
    
    assert result is not None
    assert result["karotz"]["percent_used_space"] == "36"


@pytest.mark.asyncio
async def test_get_free_space_failure(api):
    """Test get_free_space with failed response."""
    mock_resp = AsyncContextManagerMock()
    mock_resp.status = 404
    api._websession.get.return_value = AsyncContextManagerMock()
    api._websession.get.return_value.__aenter__.return_value = mock_resp
    
    result = await api.get_free_space()
    
    assert result is None


@pytest.mark.asyncio
async def test_set_led_color_success(api):
    """Test set_led_color with successful response."""
    mock_resp = AsyncContextManagerMock()
    mock_resp.status = 200
    api._websession.get.return_value = AsyncContextManagerMock()
    api._websession.get.return_value.__aenter__.return_value = mock_resp
    
    result = await api.set_led_color("FF0000")
    
    assert result is True


@pytest.mark.asyncio
async def test_set_led_color_failure(api):
    """Test set_led_color with failed response."""
    mock_resp = AsyncContextManagerMock()
    mock_resp.status = 500
    api._websession.get.return_value = AsyncContextManagerMock()
    api._websession.get.return_value.__aenter__.return_value = mock_resp
    
    result = await api.set_led_color("FF0000")
    
    assert result is False


@pytest.mark.asyncio
async def test_play_sound_success(api):
    """Test play_sound with successful response."""
    mock_resp = AsyncContextManagerMock()
    mock_resp.status = 200
    api._websession.get.return_value = AsyncContextManagerMock()
    api._websession.get.return_value.__aenter__.return_value = mock_resp
    
    result = await api.play_sound("bip1")
    
    assert result is True


@pytest.mark.asyncio
async def test_play_tts_success(api):
    """Test play_tts with successful response."""
    mock_resp = AsyncContextManagerMock()
    mock_resp.status = 200
    api._websession.get.return_value = AsyncContextManagerMock()
    api._websession.get.return_value.__aenter__.return_value = mock_resp
    
    result = await api.play_tts("Hello World", "1")
    
    assert result is True


@pytest.mark.asyncio
async def test_get_rfid_list_success(api):
    """Test get_rfid_list with successful response."""
    mock_response = {"tags": [], "return": "0"}
    
    mock_resp = AsyncContextManagerMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=mock_response)
    mock_resp.text = AsyncMock(return_value='{"tags": [], "return": "0"}')
    api._websession.get.return_value = AsyncContextManagerMock()
    api._websession.get.return_value.__aenter__.return_value = mock_resp
    
    result = await api.get_rfid_list()
    
    assert result is not None
    assert result["return"] == "0"


@pytest.mark.asyncio
async def test_clear_cache_success(api):
    """Test clear_cache with successful response."""
    mock_resp = AsyncContextManagerMock()
    mock_resp.status = 200
    api._websession.get.return_value = AsyncContextManagerMock()
    api._websession.get.return_value.__aenter__.return_value = mock_resp
    
    result = await api.clear_cache()
    
    assert result is True
