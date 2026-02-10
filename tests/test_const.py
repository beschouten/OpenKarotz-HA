"""Tests for Open Karotz constants."""
from custom_components.open_karotz.const import (
    BASE_URL,
    DOMAIN,
    LED_COLORS,
    SOUND_LIST,
    TTS_VOICES,
    MOOD_IDS,
    EAR_MIN,
    EAR_MAX,
    EAR_DOWN,
    EAR_HORIZONTAL,
    EAR_UP,
    STORAGE_KAROTZ,
    STORAGE_USB,
    SQUEEZEBOX_START,
    SQUEEZEBOX_STOP,
    CONF_HOST,
    CONF_NAME,
)


def test_domain():
    """Test DOMAIN constant."""
    assert DOMAIN == "open_karotz"


def test_base_url():
    """Test BASE_URL constant."""
    assert "192.168.1.70" in BASE_URL


def test_led_colors():
    """Test LED_COLORS constant."""
    assert "red" in LED_COLORS
    assert LED_COLORS["red"] == "FF0000"
    assert "blue" in LED_COLORS
    assert LED_COLORS["blue"] == "0000FF"
    assert "white" in LED_COLORS
    assert LED_COLORS["white"] == "FFFFFF"
    assert "black" in LED_COLORS
    assert LED_COLORS["black"] == "000000"


def test_sound_list():
    """Test SOUND_LIST constant."""
    assert "bip1" in SOUND_LIST
    assert len(SOUND_LIST) == 14


def test_tts_voices():
    """Test TTS_VOICES constant."""
    assert "1" in TTS_VOICES
    assert "30" in TTS_VOICES
    assert len(TTS_VOICES) == 86


def test_mood_ids():
    """Test MOOD_IDS constant."""
    assert "1" in MOOD_IDS
    assert "50" in MOOD_IDS
    assert len(MOOD_IDS) == 301


def test_ear_positions():
    """Test ear position constants."""
    assert EAR_MIN == 0
    assert EAR_MAX == 16
    assert EAR_DOWN == 0
    assert EAR_HORIZONTAL == 8
    assert EAR_UP == 16


def test_storage_sensors():
    """Test storage sensor constants."""
    assert STORAGE_KAROTZ == "karotz_percent_used_space"
    assert STORAGE_USB == "usb_percent_used_space"


def test_squeezebox_commands():
    """Test squeezebox command constants."""
    assert SQUEEZEBOX_START == "start"
    assert SQUEEZEBOX_STOP == "stop"


def test_configuration_keys():
    """Test configuration keys."""
    assert CONF_HOST == "host"
    assert CONF_NAME == "name"