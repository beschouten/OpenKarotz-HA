"""OpenKarotz Home Assistant Integration Constants."""

# Integration name and domain
DOMAIN = "openkarotz"

# API endpoints
API_BASE_URL = "http://192.168.1.201"
API_ENDPOINTS = {
    "GET_INFO": "/api",
    "GET_STATE": "/state",
    "GET_LEDS": "/leds",
    "GET_EARS": "/ears",
    "GET_RFID": "/rfid",
    "GET_TTS": "/tts",
    "GET_PICTURES": "/pictures",
    "GET_SOUNDS": "/sounds",
    "GET_APPS": "/apps",
    "POST_LEDS": "/leds",
    "POST_EARS": "/ears",
    "POST_TTS": "/tts",
    "POST_PICTURES": "/pictures",
    "POST_SOUNDS": "/sounds",
}

# Service names
SERVICE_NAMES = {
    "PLAY_AUDIO": "play_audio",
    "STOP_AUDIO": "stop_audio",
    "SET_VOLUME": "set_volume",
    "SET_LED": "set_led",
    "PLAY_TTS": "play_tts",
    "PLAY_SOUND": "play_sound",
    "DISPLAY_PICTURE": "display_picture",
    "TRIGGER_RFID": "trigger_rfid",
    "MOVE_EARS": "move_ears",
    "EAR_MODE": "ear_mode",
    "EAR_RESET": "ear_reset",
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

# Media player attributes
MEDIA_PLAYER_ATTRIBUTES = {
    "VOLUME": "volume",
    "PLAYBACK_STATE": "playback_state",
    "CURRENT_SOURCE": "current_source",
    "CATEGORY": "category",
    "SCHEDULE": "schedule",
}

# RFID attributes
RFID_ATTRIBUTES = {
    "DETECTED_ID": "detected_id",
    "DETECTED_TIME": "detected_time",
    "EVENT_TYPE": "event_type",
    "PREVIOUS_ID": "previous_id",
}

# TTS attributes
TTS_ATTRIBUTES = {
    "VOICE": "voice",
    "CATEGORY": "category",
    "STATUS": "status",
    "COMPLETED": "completed",
}

# Switch attributes
SWITCH_ATTRIBUTES = {
    "ENABLED": "enabled",
    "STATE": "state",
    "LAST_ACTION": "last_action",
}

# Service data schemas
SERVICE_DATA_SCHEMAS = {
    "play_audio": {
        "source": "string",
        "category": "string",
        "volume": "integer",
    },
    "stop_audio": {
        "source": "string",
    },
    "set_volume": {
        "volume": "integer",
    },
    "set_led": {
        "color": "string",
        "brightness": "integer",
        "color_temperature": "integer",
        "preset": "string",
    },
    "play_tts": {
        "text": "string",
        "voice": "string",
        "category": "string",
    },
    "play_sound": {
        "sound": "string",
        "volume": "integer",
    },
    "display_picture": {
        "picture": "string",
        "duration": "integer",
    },
    "trigger_rfid": {
        "rfid_id": "string",
        "action": "string",
    },
    "move_ears": {
        "left": "integer",
        "right": "integer",
    },
    "ear_mode": {
        "mode": "string",
    },
    "ear_reset": {},
}

# Default values
DEFAULT_PORT = 80
DEFAULT_TIMEOUT = 10
DEFAULT_RECONNECT_ATTEMPTS = 3
DEFAULT_RECONNECT_DELAY = 5

# Entity attributes
ATTR_DEVICE_ID = "device_id"
ATTR_LAST_UPDATE = "last_update"
ATTR_API_VERSION = "api_version"
ATTR_CONNECTION_STATUS = "connection_status"
ATTR_ERROR_MESSAGE = "error_message"
