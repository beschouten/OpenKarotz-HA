# Release Notes - v1.3.9

## Overview
Release of the Open Karotz Home Assistant integration with TTS service fix.

## Fixes

### TTS Service Error
- Fixed `'NoneType' object has no attribute 'data'` error in TTS service action
- Root cause: `entry.runtime_data` was never set in `async_setup_entry()`
- Fix: Added `entry.runtime_data = api` to properly store the API instance in the config entry

## Changes

### Core Components
- **TTS Service**: Fixed service handler to properly retrieve API instance from `entry.runtime_data`

## Features

### Core Components
- **Storage Sensors**: Monitor Karotz and USB storage usage
- **LED Control**: RGB LED color control (Red, Green, Blue, Yellow, Cyan, Magenta, White, Black/off)
- **Ear Control**: Position control (0-100%), reset, and random positioning
- **Media Player**: Local sound playback (14 predefined sounds)
- **TTS Service**: Multi-language text-to-speech with 88 voices
- **Mood Control**: Select from 301 French mood sounds
- **Camera**: Snapshot capture
- **System Controls**: Sleep/wake switch, clear cache button
- **RFID**: RFID tag detection sensor

### Supported Languages
French, English, German, Spanish, Italian, Dutch, Portuguese, Russian, Turkish, and 70+ others.

## Installation

### Using HACS
1. Install [HACS](https://hacs.xyz/)
2. Go to HACS → Integrations
3. Click "+" and add repository: `https://github.com/openkarotz/OpenKarotz-HA`
4. Select "Integration" type
5. Search for "Open Karotz" and click "Download"

### Manual Installation
1. Copy `custom_components/open_karotz` to `config/custom_components`
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Open Karotz"

## Configuration
1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Open Karotz"
4. Enter your device IP address (default: 192.168.1.70)
5. Enter a device name
6. Click "Submit"

## API Endpoints Tested
- ✅ `/cgi-bin/get_free_space` - Storage information
- ✅ `/cgi-bin/leds?color=...` - LED control
- ✅ `/cgi-bin/ears?left=...&right=...` - Ear position
- ✅ `/cgi-bin/ears_reset` - Reset ears
- ✅ `/cgi-bin/ears_random` - Random ear position
- ✅ `/cgi-bin/sound?id=...` - Play sound
- ✅ `/cgi-bin/sound?url=...` - Play URL
- ✅ `/cgi-bin/tts?text=...&voice=...` - TTS playback
- ✅ `/cgi-bin/apps/moods?id=...` - Play mood
- ✅ `/cgi-bin/apps/moods` - Random mood
- ✅ `/cgi-bin/snapshot?silent=1` - Snapshot capture
- ✅ `/cgi-bin/sleep` - Sleep mode
- ✅ `/cgi-bin/wake_up` - Wake up
- ✅ `/cgi-bin/clear_cache` - Clear cache
- ✅ `/cgi-bin/rfid_list` - RFID tags

## Breaking Changes
None

## Dependencies
- Home Assistant 2024.1.0 or later
- Python 3.10+
- aiohttp

## Tested With
- Open Karotz firmware 2.0+
- Device: 192.168.1.70

## Known Issues
- `/cgi-bin/wake_up` returns 404 (device-specific)
- `/cgi-bin/radio_list` returns 404
- Some operations may timeout (increase timeout if needed)

## Future Improvements
- Add more audio file formats
- Support squeezebox integration
- Add FTP upload for snapshots
- Improve timeout handling

## Credits
- [Open Karotz](https://openkarotz.org/) for the firmware
- [Home Assistant](https://www.home-assistant.io/) for the platform