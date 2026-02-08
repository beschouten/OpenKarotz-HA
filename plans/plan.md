# Open Karotz Home Assistant Integration Plan

## Overview
This document outlines the development plan for the Open Karotz Home Assistant integration, including testing strategy and milestones.

## API Validation Phase

### Step 1.1: Storage Endpoints Testing
- [ ] Test `/cgi-bin/get_free_space` endpoint
  - [ ] Verify JSON response format
  - [ ] Test with Karotz storage (0-100%)
  - [ ] Test with USB storage (-1 when not connected, 0-100% when connected)
  - [ ] Document actual response format

### Step 1.2: LED Controls Testing
- [ ] Test `/cgi-bin/leds?color=...` endpoint
  - [ ] Test with red color (FF0000)
  - [ ] Test with green color (00FF00)
  - [ ] Test with blue color (0000FF)
  - [ ] Test with white color (FFFFFF)
  - [ ] Test with black color (000000) - LED off
  - [ ] Document response format

### Step 1.3: Ear Controls Testing
- [ ] Test `/cgi-bin/ears?left=...&right=...` endpoint
  - [ ] Test with position 0 (down)
  - [ ] Test with position 8 (horizontal)
  - [ ] Test with position 16 (up)
  - [ ] Test with mixed positions
  - [ ] Document response format
- [ ] Test `/cgi-bin/ears_reset` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/ears_random` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/ears_mode?disable=...` endpoint
  - [ ] Test with disable=1 (disable ears)
  - [ ] Test with disable=0 (enable ears)
  - [ ] Document response format

### Step 1.4: Sound & TTS Testing
- [ ] Test `/cgi-bin/sound?id=...` endpoint
  - [ ] Test with available sound IDs
  - [ ] Document available sound IDs
  - [ ] Document response format
- [ ] Test `/cgi-bin/sound?url=...` endpoint
  - [ ] Test with valid MP3 URL
  - [ ] Document response format
- [ ] Test `/cgi-bin/tts?text=...&voice=...` endpoint
  - [ ] Test with English text
  - [ ] Test with French text
  - [ ] Document available voices
  - [ ] Document response format

### Step 1.5: Mood & Apps Testing
- [ ] Test `/cgi-bin/apps/moods` endpoint (random mood)
  - [ ] Document response format
- [ ] Test `/cgi-bin/apps/moods...` endpoint (specific mood)
  - [ ] Test with available mood IDs
  - [ ] Document available moods
  - [ ] Document response format
- [ ] Test `/cgi-bin/apps/clock` endpoint
  - [ ] Document response format

### Step 1.6: Snapshot Testing
- [ ] Test `/cgi-bin/snapshot?silent=1` endpoint
  - [ ] Document response format
  - [ ] Verify snapshot is saved
- [ ] Test `/cgi-bin/snapshot_list` endpoint
  - [ ] Document response format
  - [ ] Document snapshot naming convention
- [ ] Test `/cgi-bin/clear_snapshots` endpoint
  - [ ] Document response format

### Step 1.7: System Controls Testing
- [ ] Test `/cgi-bin/sleep` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/wake_up` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/display_cache` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/clear_cache` endpoint
  - [ ] Document response format

### Step 1.8: RFID Testing
- [ ] Test `/cgi-bin/rfid_start_record` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/rfid_stop_record` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/rfid_list` endpoint
  - [ ] Document response format
  - [ ] Document RFID tag format
- [ ] Test `/cgi-bin/rfid_list_ext` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/rfid_delete...` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/rfid_unassign...` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/rfid_rename...` endpoint
  - [ ] Document response format

### Step 1.9: Sound List Testing
- [ ] Test `/cgi-bin/sound_list` endpoint
  - [ ] Document all available sound IDs
  - [ ] Document response format
- [ ] Test `/cgi-bin/voice_list` endpoint
  - [ ] Document all available voices
  - [ ] Document response format
- [ ] Test `/cgi-bin/moods_list` endpoint
  - [ ] Document all available moods
  - [ ] Document response format
- [ ] Test `/cgi-bin/radio_list` endpoint
  - [ ] Document all available radio stations
  - [ ] Document response format

### Step 1.10: Squeezebox Testing
- [ ] Test `/cgi-bin/squeezebox?cmd=start` endpoint
  - [ ] Document response format
- [ ] Test `/cgi-bin/squeezebox?cmd=stop` endpoint
  - [ ] Document response format

### Step 1.11: FTP Upload Testing
- [ ] Test `/cgi-bin/snapshot_ftp?server=...&user=...&password=...&remote_dir=...` endpoint
  - [ ] Test with valid FTP server
  - [ ] Document response format

## Integration Development Phase

### Step 2.1: Create Integration Structure
- [ ] Create `custom_components/open_karotz/` directory
- [ ] Create `manifest.json` with integration metadata
- [ ] Create `__init__.py` for integration setup
- [ ] Create `const.py` for constants
- [ ] Create `config_flow.py` for UI configuration

### Step 2.2: Implement Storage Sensor
- [ ] Create `sensor.py` for storage sensors
- [ ] Implement `get_free_space` API call
- [ ] Create Karotz storage sensor
- [ ] Create USB storage sensor
- [ ] Add unit tests

### Step 2.3: Implement LED Control
- [ ] Create `light.py` for LED control
- [ ] Implement color selection
- [ ] Add unit tests

### Step 2.4: Implement Ear Control
- [ ] Create `cover.py` or `number.py` for ear position
- [ ] Implement ear position control
- [ ] Add reset and random buttons
- [ ] Add unit tests

### Step 2.5: Implement Sound Control
- [ ] Create `media_player.py` for sound playback
- [ ] Implement local sound playback
- [ ] Implement network sound playback
- [ ] Add unit tests

### Step 2.6: Implement TTS
- [ ] Create `tts` service
- [ ] Implement text-to-speech
- [ ] Add voice selection
- [ ] Add unit tests

### Step 2.7: Implement Mood Control
- [ ] Create `select.py` for mood selection
- [ ] Implement mood playback
- [ ] Add random mood button
- [ ] Add unit tests

### Step 2.8: Implement Snapshot
- [ ] Create `camera.py` for snapshot
- [ ] Implement snapshot capture
- [ ] Add unit tests

### Step 2.9: Implement System Controls
- [ ] Create `switch.py` for sleep/wake
- [ ] Implement clear cache button
- [ ] Add unit tests

### Step 2.10: Implement RFID
- [ ] Create `binary_sensor.py` for RFID detection
- [ ] Implement RFID tag management
- [ ] Add unit tests

### Step 2.11: Implement Squeezebox
- [ ] Create `media_player.py` for Squeezebox
- [ ] Implement play/stop controls
- [ ] Add unit tests

### Step 2.12: Implement FTP Upload
- [ ] Create `camera.py` with FTP upload option
- [ ] Implement FTP configuration
- [ ] Add unit tests

## Testing Phase

### Step 3.1: Unit Testing
- [ ] Test all API calls
- [ ] Test error handling
- [ ] Test timeout handling
- [ ] Test invalid parameter handling

### Step 3.2: Integration Testing
- [ ] Test with real Open Karotz device
- [ ] Test all sensors
- [ ] Test all controls
- [ ] Test configuration flow

### Step 3.3: Documentation Testing
- [ ] Test installation instructions
- [ ] Test configuration instructions
- [ ] Test usage examples

## Release Phase

### Step 4.1: Documentation
- [ ] Create README.md
- [ ] Create configuration examples
- [ ] Create troubleshooting guide

### Step 4.2: Release
- [ ] Create GitHub repository
- [ ] Create release notes
- [ ] Publish to HACS

## Maintenance

### Step 5.1: Bug Fixes
- [ ] Address issues from users
- [ ] Update documentation

### Step 5.2: Feature Updates
- [ ] Add new API endpoints
- [ ] Improve existing features