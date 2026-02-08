# Troubleshooting Guide

## Common Issues

### Device Not Found

**Problem**: Open Karotz device not detected during setup

**Solutions**:
1. Verify Open Karotz is powered on
2. Check network connectivity:
   - Ping the device: `ping 192.168.1.70`
   - Ensure device is on same network as Home Assistant
3. Verify Open Karotz firmware is updated
4. Check firewall settings - ensure HTTP port (80) is accessible
5. Try rebooting both devices

### Storage Sensors Show -1

**Problem**: USB storage sensor shows -1

**Solution**: This indicates no USB drive is connected. This is normal behavior. The sensor will show 0-100% when a USB drive is connected.

### Sound Not Playing

**Problem**: Media player not playing sounds

**Solutions**:
1. Verify sound files exist on Open Karotz device (path: `/var/www/sounds/`)
2. Check sound ID is valid (1-50)
3. Test with different sound IDs
4. Verify network connectivity
5. Check Open Karotz web interface for playback

### LED Not Responding

**Problem**: LED color doesn't change

**Solutions**:
1. Verify Open Karotz firmware supports LED control
2. Check network connectivity
3. Try different color values
4. Check Open Karotz web interface for LED control

### Ear Control Issues

**Problem**: Ears not moving or moving incorrectly

**Solutions**:
1. Listen for mechanical sounds when controlling
2. Check if ears are physically obstructed
3. Try reset function to return to default position
4. Update Open Karotz firmware if issue persists

### TTS Not Working

**Problem**: Text-to-speech not playing

**Solutions**:
1. Verify voice ID is valid (1-30)
2. Test with different text lengths
3. Check Open Karotz web interface for TTS
4. Verify Open Karotz has sufficient storage for TTS cache

### RFID Tag Not Detected

**Problem**: RFID sensor not detecting tags

**Solutions**:
1. Verify RFID tag is properly programmed
2. Ensure tag is within reading distance (1-2 cm)
3. Check Open Karotz web interface for RFID listing
4. Verify RFID file format is correct

### Snapshot Not Capturing

**Problem**: Camera not capturing snapshots

**Solutions**:
1. Verify camera module is connected
2. Check Open Karotz web interface for camera
3. Test snapshot via web interface
4. Check storage space

## Logs

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.open_karotz: debug
```

### View Logs

1. Go to Settings → System → Logs
2. Search for "Open Karotz" or "open_karotz"

### Common Log Messages

**Connection Error**:
```
ERROR (MainThread) [custom_components.open_karotz.api] Error fetching data: Connection refused
```
→ Check network connectivity and device status

**API Error**:
```
ERROR (MainThread) [custom_components.open_karotz.api] Failed to fetch /cgi-bin/leds?color=FF0000: 500
```
→ Check Open Karotz firmware and API availability

**Timeout**:
```
ERROR (MainThread) [custom_components.open_karotz.api] Error fetching data: Timeout
```
→ Check network latency and device responsiveness

## Device Requirements

### Minimum Requirements

- Open Karotz firmware 2.0+
- HTTP API enabled
- Network connectivity (Ethernet or WiFi)
- Power supply stable

### Supported Features

| Feature | Minimum Firmware |
|---------|------------------|
| LED Control | 1.5+ |
| Ear Control | 1.5+ |
| Sound Playback | 1.0+ |
| TTS | 2.0+ |
| Moods | 2.0+ |
| Snapshot | 1.0+ |
| RFID | 2.0+ |
| Squeezebox | 2.0+ |

## API Endpoints

Test API directly via browser:

| Endpoint | Description |
|----------|-------------|
| `http://192.168.1.70/cgi-bin/get_free_space` | Storage info |
| `http://192.168.1.70/cgi-bin/leds?color=FF0000` | Red LED |
| `http://192.168.1.70/cgi-bin/ears?left=8&right=8` | Horizontal ears |
| `http://192.168.1.70/cgi-bin/sound?id=1` | Sound ID 1 |
| `http://192.168.1.70/cgi-bin/snapshot?silent=1` | Capture snapshot |

## Firmware Updates

1. Download latest firmware from [Open Karotz](https://openkarotz.org/)
2. Upload via Open Karotz web interface
3. Wait for restart (approx. 2 minutes)
4. Verify update success
5. Test integration

## Network Configuration

### Static IP (Recommended)

Configure Open Karotz with static IP to avoid address changes:

1. Log into Open Karotz web interface
2. Network settings
3. Set static IP address
4. Save configuration

### Firewall Rules

Allow these ports:
- TCP 80 (HTTP - required)
- TCP 21 (FTP - optional for file transfer)

## Reset to Factory Defaults

If integration issues persist:

1. Go to Open Karotz web interface
2. System settings
3. "Restore default settings"
4. Confirm reset
5. Reconfigure integration

## Getting Help

### Before Asking

1. Check troubleshooting section above
2. Enable debug logging
3. Check Open Karotz web interface
4. Verify network connectivity

### Support Channels

- [Open Karotz Forum](https://openkarotz.org/forum/)
- [Home Assistant Community](https://community.home-assistant.io/)
- GitHub Issues

### Information to Provide

When requesting help, include:

1. Open Karotz firmware version
2. Integration version
3. Home Assistant version
4. Network setup (Ethernet/WiFi)
5. Debug logs
6. Steps to reproduce the issue