"""Integration tests for Open Karotz device at 192.168.1.70."""
import pytest
import aiohttp

BASE_URL = "http://192.168.1.70"

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_integration_storage_sensor():
    """Test storage sensor endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/cgi-bin/get_free_space") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "karotz" in text
            assert "usb" in text


@pytest.mark.asyncio
async def test_integration_led_control():
    """Test LED control endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/cgi-bin/leds?color=FF0000") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "color" in text


@pytest.mark.asyncio
async def test_integration_tts_service():
    """Test TTS service endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/cgi-bin/tts?text=Hello%20World&voice=6") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "return" in text
            assert "played" in text


@pytest.mark.asyncio
async def test_integration_sound_list():
    """Test sound list endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/cgi-bin/sound_list") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "sounds" in text


@pytest.mark.asyncio
async def test_integration_mood_list():
    """Test mood list endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/cgi-bin/moods_list") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "moods" in text


@pytest.mark.asyncio
async def test_integration_voice_list():
    """Test voice list endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/cgi-bin/voice_list") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "voices" in text


@pytest.mark.asyncio
async def test_integration_rfid_list():
    """Test RFID list endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/cgi-bin/rfid_list") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "tags" in text


@pytest.mark.asyncio
async def test_integration_clear_cache():
    """Test clear cache endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/cgi-bin/clear_cache") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "return" in text


@pytest.mark.asyncio
async def test_integration_display_cache():
    """Test display cache endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/cgi-bin/display_cache") as resp:
            assert resp.status == 200
            text = await resp.text()
            assert "count" in text