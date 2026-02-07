"""OpenKarotz Home Assistant Integration Constants."""

import voluptuous as vol

# Integration name and domain
DOMAIN = "openkarotz"

# API endpoints
API_ENDPOINTS = {
      "GET_INFO": "/cgi-bin/status",
      "GET_STATE": "/cgi-bin/status",
      "GET_LEDS": "/cgi-bin/leds",
      "GET_TTS": "/cgi-bin/tts",

      "GET_APPS": "/cgi-bin/moods",
      "POST_LEDS": "/cgi-bin/leds",
      "POST_TTS": "/cgi-bin/tts",

      "GET_VERSION": "/cgi-bin/get_version",
      "WAKEUP": "/cgi-bin/wakeup",
      "SLEEP": "/cgi-bin/sleep",

      "CLEAR_CACHE": "/cgi-bin/clear_cache",
      "CLEAR_SNAPSHOTS": "/cgi-bin/clear_snapshots",
      "TAKE_SNAPSHOT": "/cgi-bin/take_snapshot",
      "PLAY_STREAM": "/cgi-bin/play_stream",
      "PAUSE": "/cgi-bin/pause",
      "SQUEEZEBOX_START": "/cgi-bin/squeezebox_start",
      "SQUEEZEBOX_STOP": "/cgi-bin/squeezebox_stop",
}

# Service names
SERVICE_NAMES = {
    "SET_LED": "set_led",
    "PLAY_TTS": "play_tts",
}

# Sensor types
SENSOR_TYPES = {
    "DEVICE_INFO": "device_info",
    "DEVICE_STATE": "device_state",
    "MEMORY_USAGE": "memory_usage",
    "UPTIME": "uptime",
}

# Light attributes
LIGHT_ATTRIBUTES = {
    "COLOR": "color",
    "BRIGHTNESS": "brightness",
    "COLOR_TEMPERATURE": "color_temperature",
    "PRESET": "preset",
    "RGB_VALUE": "rgb_value",
}

# TTS attributes
TTS_ATTRIBUTES = {
    "VOICE": "voice",
    "CATEGORY": "category",
    "STATUS": "status",
    "COMPLETED": "completed",
}

# Service data schemas
SERVICE_DATA_SCHEMAS = {
    "set_led": {
        vol.Required("config_entry_id"): str,
        vol.Optional("color"): str,
        vol.Optional("brightness"): int,
        vol.Optional("color_temperature"): int,
        vol.Optional("preset"): str,
        vol.Optional("rgb_value"): str,
    },
    "play_tts": {
        vol.Required("config_entry_id"): str,
        vol.Required("text"): str,
        vol.Optional("voice"): str,
        vol.Optional("category"): str,
    },
}

# Default values
DEFAULT_PORT = 80
DEFAULT_TIMEOUT = 10
DEFAULT_RECONNECT_ATTEMPTS = 3
DEFAULT_RECONNECT_DELAY = 5

# Entity attributes
ATTR_LAST_UPDATE = "last_update"
ATTR_CONNECTION_STATUS = "connection_status"
ATTR_ERROR_MESSAGE = "error_message"