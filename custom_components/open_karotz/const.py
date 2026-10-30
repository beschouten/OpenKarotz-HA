"""Constants for the OpenKarotz integration."""
from __future__ import annotations

DOMAIN = "open_karotz"

# Config keys (CONF_HOST/CONF_NAME come from homeassistant.const)
CONF_POLL_INTERVAL = "poll_interval"
CONF_DEFAULT_VOICE = "default_voice"

DEFAULT_NAME = "OpenKarotz"
DEFAULT_POLL_INTERVAL = 60  # seconds; device is slow, keep >= 30

# Ear servo range (write-only, 0=down, 8=horizontal, 16=up)
EAR_MIN = 0
EAR_MAX = 16
EAR_HORIZONTAL = 8

# LED effects (status only reports led_pulse; blink tracked optimistically)
EFFECT_OFF = "off"
EFFECT_PULSE = "pulse"
EFFECT_BLINK = "blink"
EFFECT_PULSE_BLINK = "pulse_blink"
EFFECTS = [EFFECT_PULSE, EFFECT_BLINK, EFFECT_PULSE_BLINK]

# Config entry version history:
#   1: initial (v3 integration)
#   2: unique_id from device MAC (v4)
CONFIG_ENTRY_VERSION = 2
