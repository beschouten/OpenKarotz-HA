# Open Karotz Home Assistant Integration

Custom Home Assistant integration for Open Karotz devices.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.12+-orange.svg)](https://www.home-assistant.io/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](https://github.com/openkarotz/OpenKarotz-HA/releases/tag/v3.0.0)

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Storage Sensors | ✅ | Monitor Karotz and USB storage |
| LED Control | ✅ | RGB LED (8 colors + off) |
| Ear Control | ✅ | Position, reset, random |
| Sound Player | ✅ | Local sounds (14 predefined) |
| TTS | ✅ | Service action + media_player |
| Mood Control | ✅ | 301 French moods |
| Camera | ✅ | Snapshot capture |
| System | ✅ | Sleep/wake, clear cache |
| RFID | ✅ | Tag detection |

## Installation

### HACS (Recommended)

1. Install [HACS](https://hacs.xyz/)
2. Go to **HACS** → **Integrations**
3. Click **"+"** in bottom right
4. Add repository: `https://github.com/openkarotz/OpenKarotz-HA`
5. Select **"Integration"** type
6. Search **"Open Karotz"** and click **"Download"**
7. Restart Home Assistant
8. Go to **Settings** → **Devices & Services** → **Add Integration**

### Manual Installation

1. Copy `custom_components/open_karotz` to `config/custom_components`
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**

## Configuration

### Configuration Flow (Recommended - EASIEST)

1. Go to **Settings** → **Devices & Services**
2. Click **"Add Integration"**
3. Search for **"Open Karotz"**
4. Enter your device information:
   - **Host (IP address)**: Your Open Karotz device IP (default: 192.168.1.70)
   - **Name**: Display name
5. Click **"Submit"**

**Finding Your Open Karotz IP Address:**
- Check your router's DHCP client list
- Open Karotz web interface shows IP on screen
- Use network scanning tools like `nmap` or [Advanced IP Scanner](https://advanced-ip-scanner.com/)

### Manual IP Configuration

To find your Open Karotz device IP:

```bash
# Using nmap (Linux/macOS/Windows with WSL)
nmap -sn 192.168.1.0/24 | grep -B2 -A2 "karotz"

# Or ping the default IP
ping 192.168.1.70
```

### YAML Configuration (Alternative)

```yaml
# configuration.yaml
open_karotz:
  host: "192.168.1.70"
  name: "Open Karotz"
```

## Entities

### Sensors

| Entity | Description |
|--------|-------------|
| `sensor.karotz_storage` | Karotz storage usage (0-100%) |
| `sensor.usb_storage` | USB storage usage (0-100%, -1 if disconnected) |

### Lights

| Entity | Description |
|--------|-------------|
| `light.open_karotz_led` | RGB LED control |

**Color Options**: Red, Green, Blue, Yellow, Cyan, Magenta, White, Black (off)

### Covers

| Entity | Description |
|--------|-------------|
| `cover.open_karotz_ears` | Ear position control (0-100%) |

**Actions**: Open, Close, Set Position, Reset, Random

### Media Players

| Entity | Description |
|--------|-------------|
| `media_player.open_karotz` | Sound playback + **TTS** |

**Features**:
- Local sound playback (14 predefined sounds)
- Network sound playback (URL)
- Volume control
- **Text-to-Speech via service action**

### Selects

| Entity | Description |
|--------|-------------|
| `select.open_karotz_mood` | Mood selection (301 moods) |

**Actions**: Select mood, Play random

### Cameras

| Entity | Description |
|--------|-------------|
| `camera.open_karotz_camera` | Snapshot capture |

**Features**: Manual capture, Stream support

### Switches

| Entity | Description |
|--------|-------------|
| `switch.open_karotz_sleep` | Sleep/wake control |

**Actions**: Turn on (wake), Turn off (sleep)

### Binary Sensors

| Entity | Description |
|--------|-------------|
| `binary_sensor.open_karotz_rfid` | RFID tag detection |

**Attributes**: `tag_id`

### Buttons

| Entity | Description |
|--------|-------------|
| `button.open_karotz_clear_cache` | Clear system cache |

## 📢 Text-to-Speech (TTS) - How to Use

Open Karotz TTS is accessible through **two methods**:

### Method 1: Service Action (Easiest)

This is the recommended way to use TTS:

```yaml
# In automations, scripts, or service calls
action:
  service: open_karotz.tts
  data:
    text: "Hello World"
    voice: "6"  # English Female
```

### Method 2: Media Player

TTS is also available through the media player entity:

1. Use `media_player.play_media` service
2. Set `media_content_type` to "music"
3. Set `media_content_id` to your text
4. The text will be spoken using the default voice

### Voice Selection

Choose from 88 voices across 30+ languages:

| Voice ID | Language | Gender |
|----------|----------|--------|
| 1 | French | Male |
| 6 | English (US) | Female |
| 7 | English (UK) | Male |
| 13 | Spanish | Male |
| 25 | Brazilian Portuguese | Male |

### Full TTS Examples

**Basic TTS**:
```yaml
action:
  service: open_karotz.tts
  data:
    text: "Welcome home!"
```

**With Voice Selection**:
```yaml
action:
  service: open_karotz.tts
  data:
    text: "Bonjour!"
    voice: "1"  # French Male
```

**In an Automation**:
```yaml
automation:
  - alias: "Doorbell TTS"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: 'on'
    action:
      - service: open_karotz.tts
        data:
          text: "Someone is at the door"
          voice: "6"
      - service: light.toggle
        target:
          entity_id: light.open_karotz_led
```

**Using Home Assistant GUI**:
1. Go to **Settings** → **Automations & Scenes**
2. Create a new automation
3. Add action: **"Call Service"**
4. Service: `open_karotz.tts`
5. Fill in `text` and optional `voice`

### TTS Voice IDs (Complete List)

| ID | Language | Gender |
|----|----------|--------|
| 1-86 | 30+ languages | Male/Female |

Commonly used:
- **6**: English (US) Female (default)
- **7**: English (UK) Male
- **1**: French Male
- **2**: French Female

### Troubleshooting TTS

If TTS doesn't work:

1. **Verify voice ID**: 1-88 (use `6` for English)
2. **Check network**: `ping 192.168.1.70`
3. **Test on device**: Try TTS via Open Karotz web interface
4. **Text length**: Keep under 200 characters
5. **URL encoding**: Special characters are automatically encoded

## Configuration Examples

### Automation: Welcome Notification

```yaml
automation:
  - alias: "Welcome Home"
    trigger:
      - platform: state
        entity_id: device_tracker.phone
        to: 'home'
    action:
      - service: open_karotz.tts
        data:
          text: "Welcome home!"
          voice: "6"
      - service: light.turn_on
        data:
          rgb_color: [0, 255, 0]  # Green
        target:
          entity_id: light.open_karotz_led
```

### Automation: Storage Alert

```yaml
automation:
  - alias: "Storage Full Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.karotz_storage
        above: 90
    action:
      - service: notify.persistent_notification
        data:
          message: "Karotz storage is 90% full!"
```

### Automation: Random Mood

```yaml
automation:
  - alias: "Random Morning Mood"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: select.select_option
        data:
          option: "random"
        target:
          entity_id: select.open_karotz_mood
```

## Troubleshooting

### Device Not Found

1. Verify Open Karotz is powered on
2. Check network connectivity: `ping 192.168.1.70`
3. Verify same network segment
4. Check firewall settings

### Sound Not Playing

1. Verify sound files exist on Open Karotz
2. Check sound ID (1-14 for predefined sounds)
3. Verify network connectivity

### LED Not Responding

1. Verify LED control supported in firmware
2. Check network connectivity
3. Try different color values

### TTS Not Working

See full **[TTS Troubleshooting](#troubleshooting-tts)** section above.

Common fixes:
1. Verify voice ID (1-88, default: 6)
2. Test with short text (200 chars max)
3. Check device is online: `ping 192.168.1.70`
4. Test via Open Karotz web interface

### RFID Not Detected

1. Verify tag is properly programmed
2. Ensure tag within reading distance (1-2 cm)
3. Check Open Karotz web interface for RFID

## API Documentation

For complete API documentation, see the [API Documentation](custom_components/open_karotz/api.py) or [API Plan](plans/open_karotz_api_documentation.md).

## Testing

### Unit Tests

```bash
pytest tests
```

### Integration Tests

Integration tests verify communication with a real Open Karotz device at `192.168.1.70`.

```bash
pytest tests/test_integration.py -v
```

## Project Structure

```
custom_components/open_karotz/
├── __init__.py          # Integration setup
├── const.py             # Constants
├── config_flow.py       # Configuration flow
├── manifest.json        # Integration metadata
├── api.py               # API helper
├── sensor.py            # Storage sensors
├── light.py             # LED control
├── cover.py             # Ear control
├── media_player.py      # Sound playback
| **TTS via service action**
├── select.py            # Mood control
├── camera.py            # Snapshot capture
├── switch.py            # Sleep/wake
├── binary_sensor.py     # RFID sensor
├── button.py            # Clear cache
└── translations/
    └── en.json
tests/
├── test_api.py
├── test_const.py
├── test_config_flow.py
├── test_sensor.py
├── test_light.py
├── test_cover.py
├── test_media_player.py
├── test_select.py
├── test_camera.py
├── test_switch.py
├── test_binary_sensor.py
├── test_button.py
└── test_integration.py
```

## Development

### Setting Up Development Environment

1. Clone the repository
2. Install dependencies: `pip install pytest pytest-asyncio`
3. Run tests: `pytest tests`

### Adding New Features

1. Update `api.py` with new API methods
2. Create appropriate Home Assistant component
3. Add tests in `tests/`
4. Update documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## 📢 TTS Troubleshooting

If TTS doesn't work:

1. **Verify voice ID**: 1-88 (default: 6 for English)
2. **Check network**: `ping 192.168.1.70`
3. **Test text length**: Keep under 200 characters
4. **Web interface test**: Try TTS via Open Karotz web interface
5. **Check logs**: Look for error messages in Home Assistant logs

## Acknowledgments

- [Open Karotz](https://openkarotz.org/) for the Open Karotz firmware
- [Home Assistant](https://www.home-assistant.io/) for the platform