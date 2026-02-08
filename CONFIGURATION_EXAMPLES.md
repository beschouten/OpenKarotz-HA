# Configuration Examples

## Basic Configuration

### Configuration Flow (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **"Add Integration"**
3. Search for **"Open Karotz"**
4. Enter device information:
   - **Host**: `192.168.1.70` (your Open Karotz IP)
   - **Name**: `Open Karotz` (your choice)
5. Click **Submit**

## Advanced Configuration

### Example 1: Multiple Open Karotz Devices

Configure multiple devices with different names:

**Device 1**:
- Host: `192.168.1.70`
- Name: `Living Room`

**Device 2**:
- Host: `192.168.1.71`
- Name: `Bedroom`

### Example 2: Using with MQTT

Control Open Karotz via MQTT:

```yaml
# configuration.yaml
mqtt:
  sensor:
    - name: "Karotz Storage"
      state_topic: "homeassistant/sensor/karotz/storage/state"
```

### Example 3: Automation with LEDs

**Turn on LED when someone arrives**:

```yaml
# automations.yaml
- alias: "Turn on LED when home"
  trigger:
    - platform: state
      entity_id: device_tracker.phone
      to: 'home'
  action:
    - service: light.turn_on
      target:
        entity_id: light.open_karotz_led
      data:
        rgb_color: [0, 255, 0]  # Green
```

**Turn off LED when leaving**:

```yaml
- alias: "Turn off LED when away"
  trigger:
    - platform: state
      entity_id: device_tracker.phone
      to: 'not_home'
  action:
    - service: light.turn_off
      target:
        entity_id: light.open_karotz_led
```

### Example 4: TTS Notifications

**Welcome notification**:

```yaml
# automations.yaml
- alias: "Welcome Home"
  trigger:
    - platform: state
      entity_id: device_tracker.phone
      to: 'home'
  action:
    - service: open_karotz.tts
      data:
        text: "Welcome home!"
        voice: "2"  # French Female
```

**Doorbell notification**:

```yaml
- alias: "Doorbell TTS"
  trigger:
    - platform: state
      entity_id: binary_sensor.doorbell
      to: 'on'
  action:
    - service: open_karotz.tts
      data:
        text: "There is someone at the door"
        voice: "3"  # English Male
```

### Example 5: Mood Control

**Random mood on schedule**:

```yaml
# automations.yaml
- alias: "Morning Mood"
  trigger:
    - platform: time
      at: "08:00:00"
  action:
    - service: select.select_option
      target:
        entity_id: select.open_karotz_mood
      data:
        option: "1"
```

**Evening mood**:

```yaml
- alias: "Evening Mood"
  trigger:
    - platform: time
      at: "18:00:00"
  action:
    - service: select.select_option
      target:
        entity_id: select.open_karotz_mood
      data:
        option: "5"
```

### Example 6: Storage Monitoring

**Alert when storage is full**:

```yaml
# automations.yaml
- alias: "Storage Alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.karotz_storage
      above: 90
  action:
    - service: notify.persistent_notification
      data:
        message: "Karotz storage is 90% full!"
```

### Example 7: Ear Position Control

**Set ears on schedule**:

```yaml
- alias: "Morning Ear Position"
  trigger:
    - platform: time
      at: "08:00:00"
  action:
    - service: cover.open_cover
      target:
        entity_id: cover.open_karotz_ears
```

### Example 8: Camera Snapshot

**Take snapshot when motion detected**:

```yaml
# automations.yaml
- alias: "Motion Snapshot"
  trigger:
    - platform: state
      entity_id: binary_sensor.motion_sensor
      to: 'on'
  action:
    - service: camera.snapshot
      target:
        entity_id: camera.open_karotz_camera
      data:
        filename: "/tmp/karotz_snapshot_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
```

### Example 9: System Control

**Automatic sleep at night**:

```yaml
- alias: "Night Sleep"
  trigger:
    - platform: time
      at: "23:00:00"
  action:
    - service: switch.turn_off
      target:
        entity_id: switch.open_karotz_sleep
```

**Wake up in morning**:

```yaml
- alias: "Morning Wake"
  trigger:
    - platform: time
      at: "07:00:00"
  action:
    - service: switch.turn_on
      target:
        entity_id: switch.open_karotz_sleep
```

### Example 10: RFID Trigger

**Play sound on RFID scan**:

```yaml
# automations.yaml
- alias: "RFID Sound"
  trigger:
    - platform: state
      entity_id: binary_sensor.open_karotz_rfid
      to: 'on'
  action:
    - service: media_player.play_media
      target:
        entity_id: media_player.open_karotz
      data:
        media_content_type: music
        media_content_id: "1"
```

## YAML Configuration (Alternative)

If you prefer YAML configuration:

```yaml
# configuration.yaml
open_karotz:
  - host: "192.168.1.70"
    name: "Open Karotz"
```

**Note**: Configuration flow is recommended. YAML is only for specific use cases.

## Testing Configuration

### Verify Configuration

1. Go to **Settings** → **Devices & Services**
2. Find **Open Karotz** in integrations
3. Click on your device
4. Check entity status

### Test Entities

Use Developer Tools → Services:

**Test LED**:
```yaml
service: light.turn_on
data:
  rgb_color: [255, 0, 0]
target:
  entity_id: light.open_karotz_led
```

**Test TTS**:
```yaml
service: open_karotz.tts
data:
  text: "Test successful"
  voice: "1"
```

**Test Ear Position**:
```yaml
service: cover.set_cover_position
data:
  position: 50
target:
  entity_id: cover.open_karotz_ears
```

## Troubleshooting Configuration

### Check Device Status

1. Go to **Developer Tools** → **States**
2. Find `open_karotz` entities
3. Check state and attributes

### Validate IP Address

```bash
# Test connectivity
ping 192.168.1.70
curl http://192.168.1.70/cgi-bin/get_free_space
```

### Verify API Response

The API should return:

```json
{
  "karotz": {"percent_used_space": 45},
  "usb": {"percent_used_space": 30}
}
```

If not, check Open Karotz firmware version.

## Tips

1. **Use Configuration Flow**: Easier and less error-prone
2. **Test After Changes**: Verify entities in Developer Tools
3. **Check Logs**: Use debug logging for issues
4. **Network Stability**: Use Ethernet for best performance
5. **Firmware Updates**: Keep Open Karotz firmware updated
6. **Backup Config**: Save configuration before major changes