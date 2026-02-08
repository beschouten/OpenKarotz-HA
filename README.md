# Open Karotz Home Assistant Integration

Custom Home Assistant integration for Open Karotz devices.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1.0+-orange.svg)](https://www.home-assistant.io/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Storage Sensors | ✅ | Monitor Karotz and USB storage |
| LED Control | ✅ | RGB LED (8 colors + off) |
| Ear Control | ✅ | Position, reset, random |
| Sound Player | ✅ | Local sounds (14 predefined) |
| TTS | ✅ | 88 voices, 30+ languages |
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

### Configuration Flow (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **"Add Integration"**
3. Search for **"Open Karotz"**
4. Enter your device information:
   - **Host**: IP address (default: 192.168.1.70)
   - **Name**: Display name
5. Click **"Submit"**

### YAML Configuration

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
| `media_player.open_karotz` | Sound playback |

**Features**:
- Local sound playback (14 predefined sounds)
- Network sound playback (URL)
- Volume control

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

## Services

### TTS Service

Play text-to-speech on your Open Karotz device.

**Service**: `open_karotz.tts`

**Data**:
| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `text` | Yes | string | Text to speak |
| `voice` | No | string | Voice ID (1-88) |

**Example**:
```yaml
action:
  service: open_karotz.tts
  data:
    text: "Hello World"
    voice: "6"  # English Female
```

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

1. Verify voice ID (1-88)
2. Test with different text lengths
3. Check Open Karotz web interface for TTS

### RFID Not Detected

1. Verify tag is properly programmed
2. Ensure tag within reading distance (1-2 cm)
3. Check Open Karotz web interface for RFID

## API Documentation

For complete API documentation, see the [API Documentation](plans/open_karotz_api_documentation.md).

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
├── tts.py               # TTS service
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

## Acknowledgments

- [Open Karotz](https://openkarotz.org/) for the Open Karotz firmware
- [Home Assistant](https://www.home-assistant.io/) for the platform