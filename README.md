"""OpenKarotz README and documentation."""

# OpenKarotz Home Assistant Integration v2.2.2

A Home Assistant integration for OpenKarotz devices, enabling control and monitoring of working features through the Home Assistant Community Store (HACS).

## Changelog v2.2.2

- Fixed config_flow version mismatch (v1 to v2)
- Fixed services data structure access
- Added config_entry_id to service schemas
- Updated coordinator async API calls
- Removed unused API_BASE_URL constant
- Improved migration logic

## Features

- **Device Information**: Monitor device status, memory usage, and uptime
- **LED Control**: Full RGB color control, brightness adjustment, and color temperature
- **Text-to-Speech**: Voice synthesis with customizable categories
- **Basic Device Control**: Wake up, sleep, and cache management

## Installation

### Via HACS (Recommended)

1. Install Home Assistant Community Store (HACS)
2. Go to HACS → Integrations
3. Search for "OpenKarotz"
4. Click "Install"
5. Follow the setup wizard

### Manual Installation

1. Download this repository
2. Place the `custom_components/openkarotz` directory in your Home Assistant `custom_components` folder
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration → OpenKarotz

## Configuration

### Basic Setup

Enter your OpenKarotz device IP address and port:

- **Host**: The IP address of your OpenKarotz device (default: 192.168.1.201)
- **Port**: The device port number (default: 80)

### Configuration Example

```yaml
openkarotz:
  host: 192.168.1.201
  port: 80
```

## Entities

### Sensors

- **Device Name**: Name of the OpenKarotz device
- **Device State**: Current state of the device
- **Memory Usage**: Memory usage percentage
- **Device Uptime**: Device uptime in seconds

### Lights

- **LED Light**: Full RGB color control with brightness and color temperature

### Switches

- **Enable Device**: Enable or disable the OpenKarotz device

## Services

### set_led
Set LED color, brightness, or preset.

**Service Data Attributes:**
- `color`: Color name (e.g., "red", "blue")
- `brightness`: Brightness level (0-100)
- `color_temperature`: Color temperature in Kelvin
- `preset`: Preset color scheme name
- `rgb_value`: RGB color value (e.g., "FF0000")

### play_tts
Play text-to-speech.

**Service Data Attributes:**
- `text`: Text to speak
- `voice`: Voice identifier
- `category`: TTS category (e.g., "notification")

### wakeup
Wake up the device.

**Service Data Attributes:**
- No attributes required

### sleep
Put the device to sleep.

**Service Data Attributes:**
- No attributes required

### clear_cache
Clear device cache.

**Service Data Attributes:**
- No attributes required

## Configuration Examples

### Automation Examples

#### Turn on LED when device starts
```yaml
automation:
  - alias: "Turn on LED on startup"
    trigger:
      - platform: state
        entity_id: sensor.device_state
        to: "running"
    action:
      - service: openkarotz.set_led
        data:
          color: "blue"
          brightness: 100
```

#### Play TTS on device startup
```yaml
automation:
  - alias: "Play TTS on startup"
    trigger:
      - platform: state
        entity_id: sensor.device_state
        to: "running"
    action:
      - service: openkarotz.play_tts
        data:
          text: "Device started"
          category: "notification"
```

## Troubleshooting

### Connection Issues

- Ensure OpenKarotz device is accessible from Home Assistant
- Check IP address and port configuration
- Verify network connectivity
- Check device logs for errors

### Entity Not Appearing

- Wait for data synchronization (default: 30 seconds)
- Check connection status in device info
- Restart Home Assistant
- Verify device is responding to API requests

### API Errors

- Check device API documentation
- Verify API endpoints are accessible
- Review integration logs for detailed error messages
- Ensure proper authentication if required

## Development

### Project Structure

```
openkarotz-ha/
├── custom_components/
│   └── openkarotz/
│       ├── __init__.py
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── api.py
│       │   └── Includes: get_device_info(), set_led(), play_tts(), wakeup(), sleep(), clear_cache()
│       ├── sensors.py
│       ├── lights.py
│       ├── switch.py
│       ├── services.py
│       ├── const.py
│       ├── manifest.json
│       └── translations/
│           └── en.json
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── README.md
└── requirements.txt
```

### Requirements

- Home Assistant >= 2026.1.0
- Python 3.9+

### Testing

Run automated tests:
```bash
pytest tests/
```

## Changelog

### Version 1.2.0
- Removed non-working features (ears, RFID, pictures, sounds)
- Updated to only include working features: device info, LED control, TTS, basic device control
- Updated services to only show working services
- Updated entities to only include working entities
- Updated API documentation to only show working endpoints
- Updated project structure to reflect actual implementation

### Version 1.1.0
- Added ear movement control (move_ears, ears_mode, ears_reset)
- Added play_sound and display_picture services
- Added get_pictures, get_sounds, get_apps API methods
- Added comprehensive tests for ear movement API
- Fixed HACS installation issues
- All code validated with pytest

### Version 1.0.0
- Initial release with basic device control
- LED control functionality
- TTS functionality
- Device monitoring sensors

## Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests.

## License

This project is provided as-is for educational and personal use.

## Support

For issues, questions, or contributions, please visit the GitHub repository or contact the maintainers.

## Credits

- Home Assistant: https://www.home-assistant.io
- OpenKarotz: https://github.com/beschouten/OpenKarotz

## API Documentation

The OpenKarotz API is based on the OpenKarotz Websources Installer project by rofra:
- **Repository**: https://github.com/rofra/karotz-openkarotz-websources-installer
- **API Pattern**: All endpoints follow the `/cgi-bin/` pattern

### Working API Endpoints

| Endpoint | Function | Parameters |
|----------|----------|------------|
| `/cgi-bin/status` | Device status | - |
| `/cgi-bin/leds` | LED control | RGB, brightness |
| `/cgi-bin/tts` | Text-to-speech | text, voice, category |
| `/cgi-bin/wakeup` | Wake up device | - |
| `/cgi-bin/sleep` | Put device to sleep | - |
| `/cgi-bin/cache` | Clear cache | - |

For detailed API documentation, visit the [OpenKarotz API Documentation](https://github.com/rofra/karotz-openkarotz-websources-installer).