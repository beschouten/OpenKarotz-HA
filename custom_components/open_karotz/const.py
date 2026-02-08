"""Constants for the Open Karotz integration."""

DOMAIN = "open_karotz"

# API Base URL
BASE_URL = "http://192.168.1.70"

# Storage
STORAGE_KAROTZ = "karotz_percent_used_space"
STORAGE_USB = "usb_percent_used_space"

# LED Colors
LED_COLORS = {
    "red": "FF0000",
    "green": "00FF00",
    "blue": "0000FF",
    "yellow": "FFFF00",
    "cyan": "00FFFF",
    "magenta": "FF00FF",
    "white": "FFFFFF",
    "black": "000000",
}

# Ear Positions
EAR_MIN = 0
EAR_MAX = 16
EAR_DOWN = 0
EAR_HORIZONTAL = 8
EAR_UP = 16

# Sound IDs
SOUND_LIST = [
    "bip1", "bling", "flush", "install_ok", "jet1", "laser_15", 
    "merde", "ready", "rfid_error", "rfid_ok", "saut1", "start", 
    "twang_01", "twang_04"
]

# TTS Voices
TTS_VOICES = {
    "1": "French Male", "2": "French Female", "3": "Canadian French Male", "4": "Canadian French Female",
    "5": "English (US) Male", "6": "English (US) Female", "7": "English (UK) Male", "8": "English (UK) Female",
    "9": "German Male", "10": "German Female", "11": "Italian Male", "12": "Italian Female",
    "13": "Spanish Male", "14": "Spanish Female", "15": "Dutch Male", "16": "Dutch Female",
    "17": "Afrikan Male", "18": "Afrikan Female", "19": "Armenian Male", "20": "Armenian Female",
    "21": "Arabic Male", "22": "Arabic Female", "23": "Bosnian Male", "24": "Bosnian Female",
    "25": "Brazilian Portuguese Male", "26": "Brazilian Portuguese Female", "27": "Croatian Male", "28": "Croatian Female",
    "29": "Czech Male", "30": "Czech Female", "31": "Danish Male", "32": "Danish Female",
    "33": "English (Australian) Male", "34": "English (Australian) Female", "35": "Esperanto Male", "36": "Esperanto Female",
    "37": "Finnish Male", "38": "Finnish Female", "39": "Greek Male", "40": "Greek Female",
    "41": "Hatian Creole Male", "42": "Hatian Creole Female", "43": "Hindi Male", "44": "Hindi Female",
    "45": "Hungarian Male", "46": "Hungarian Female", "47": "Icelandic Male", "48": "Icelandic Female",
    "49": "Indonesian Male", "50": "Indonesian Female", "51": "Japanese Male", "52": "Japanese Female",
    "53": "Korean Male", "54": "Korean Female", "55": "Latin Male", "56": "Latin Female",
    "57": "Norwegian Male", "58": "Norwegian Female", "59": "Polish Male", "60": "Polish Female",
    "61": "Portuguese Male", "62": "Portuguese Female", "63": "Romanian Male", "64": "Romanian Female",
    "65": "Russian Male", "66": "Russian Female", "67": "Serbian Male", "68": "Serbian Female",
    "69": "Serbo-Croatian Male", "70": "Serbo-Croatian Female", "71": "Slovak Male", "72": "Slovak Female",
    "73": "Swahili Male", "74": "Swahili Female", "75": "Swedish Male", "76": "Swedish Female",
    "77": "Tamil Male", "78": "Tamil Female", "79": "Thai Male", "80": "Thai Female",
    "81": "Turkish Male", "82": "Turkish Female", "83": "Vietnamese Male", "84": "Vietnamese Female",
    "85": "Welsh Male", "86": "Welsh Female"
}

# Moods
MOOD_IDS = [str(i) for i in range(1, 302)]

# RFID
RFID_TAG_LENGTH = 10

# Squeezebox Commands
SQUEEZEBOX_START = "start"
SQUEEZEBOX_STOP = "stop"

# FTP Upload
FTP_DEFAULT_PORT = 21

# Configuration
CONF_HOST = "host"
CONF_NAME = "name"

# Default Values
DEFAULT_NAME = "Open Karotz"