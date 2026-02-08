# Open Karotz API Documentation

This document outlines all available Open Karotz API endpoints, their input formats, test data, and expected results.

## Base URL
```
http://192.168.1.70
```

---

## Storage Endpoints

### `/cgi-bin/get_free_space`

**Description**: Returns storage usage information for internal and USB storage.

**Method**: GET

**Parameters**: None

**Response Format**: JSON

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/get_free_space
```

**Test Response**:
```json
{
  "karotz_percent_used_space": "36",
  "usb_percent_used_space": "-1"
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `karotz_percent_used_space` | String | Percentage of internal storage used (0-100) |
| `usb_percent_used_space` | String | Percentage of USB storage used (-1 if no USB device) |

**Expected Results**:
- Karotz storage: 0-100 (percentage)
- USB storage: -1 (no USB), 0-100 (percentage when USB is connected)

---

## LED Controls

### `/cgi-bin/leds?color=...`

**Description**: Sets LED color. Can be used for fixed or pulse effects.

**Method**: GET

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `color` | Yes | 6-digit hex color code (e.g., `FF0000` for red) |

**Test Requests**:
```
GET http://192.168.1.70/cgi-bin/leds?color=FF0000
```

**Expected Response**: Success message (text)

**Color Examples**:
| Color | Hex Code |
|-------|----------|
| Red | `FF0000` |
| Green | `00FF00` |
| Blue | `0000FF` |
| Yellow | `FFFF00` |
| Cyan | `00FFFF` |
| Magenta | `FF00FF` |
| White | `FFFFFF` |
| Black (Off) | `000000` |

---

## Ear Controls

### `/cgi-bin/ears?left=...&right=...`

**Description**: Moves ears to specified positions.

**Method**: GET

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `left` | Yes | Left ear position (0-16) |
| `right` | Yes | Right ear position (0-16) |

**Ear Position Reference**:
```
Position 0:  Down
Position 8:  Horizontal
Position 16: Up
```

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/ears?left=8&right=8
```

**Expected Response**: Success message (text)

### `/cgi-bin/ears_reset`

**Description**: Resets ears to default position.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/ears_reset
```

**Expected Response**: Success message (text)

### `/cgi-bin/ears_random`

**Description**: Moves ears to random positions.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/ears_random
```

**Expected Response**: Success message (text)

### `/cgi-bin/ears_mode?disable=...`

**Description**: Enables or disables ear motion (for broken ears).

**Method**: GET

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `disable` | Yes | `1` to disable, `0` to enable |

**Test Requests**:
```
GET http://192.168.1.70/cgi-bin/ears_mode?disable=1
GET http://192.168.1.70/cgi-bin/ears_mode?disable=0
```

**Expected Response**: Success message (text)

---

## Sound & TTS

### `/cgi-bin/sound?id=...`

**Description**: Plays a local sound file.

**Method**: GET

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Sound ID (filename without extension) |

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/sound?id=mood_happy
```

**Expected Response**: Success message (text)

### `/cgi-bin/sound?url=...`

**Description**: Plays a network sound (radio stream).

**Method**: GET

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `url` | Yes | URL to audio stream |

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/sound?url=http://example.com/stream.mp3
```

**Expected Response**: Success message (text)

### `/cgi-bin/tts?text=...&voice=...`

**Description**: Text-to-speech functionality.

**Method**: GET

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `text` | Yes | Text to speak |
| `voice` | Yes | Voice ID (e.g., `en-US`, `fr-FR`) |

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/tts?text=Hello%20World&voice=en-US
```

**Expected Response**: Success message (text)

---

## Mood & Apps

### `/cgi-bin/apps/moods`

**Description**: Plays a random mood.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/apps/moods
```

**Expected Response**: Success message (text)

### `/cgi-bin/apps/moods...`

**Description**: Plays a specific mood.

**Method**: GET

**Parameters**: Mood ID (appended to URL)

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/apps/moods_happy
```

**Expected Response**: Success message (text)

### `/cgi-bin/apps/clock`

**Description**: Plays the funny clock.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/apps/clock
```

**Expected Response**: Success message (text)

---

## Snapshot

### `/cgi-bin/snapshot?silent=1`

**Description**: Takes a snapshot photo.

**Method**: GET

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `silent` | No | `1` for silent mode |

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/snapshot?silent=1
```

**Expected Response**: Success message (text)

### `/cgi-bin/snapshot_list`

**Description**: Lists all snapshots.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/snapshot_list
```

**Expected Response**: List of snapshot filenames (text)

### `/cgi-bin/clear_snapshots`

**Description**: Deletes all snapshots.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/clear_snapshots
```

**Expected Response**: Success message (text)

---

## System Controls

### `/cgi-bin/sleep`

**Description**: Puts Karotz to sleep.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/sleep
```

**Expected Response**: Success message (text)

### `/cgi-bin/wake_up`

**Description**: Wakes up Karotz.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/wake_up
```

**Expected Response**: Success message (text)

### `/cgi-bin/display_cache`

**Description**: Displays cache information.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/display_cache
```

**Expected Response**: Cache info (text)

### `/cgi-bin/clear_cache`

**Description**: Clears the TTS cache.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/clear_cache
```

**Expected Response**: Success message (text)

---

## RFID

### `/cgi-bin/rfid_start_record`

**Description**: Starts RFID tag recording.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/rfid_start_record
```

**Expected Response**: Success message (text)

### `/cgi-bin/rfid_stop_record`

**Description**: Stops RFID tag recording.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/rfid_stop_record
```

**Expected Response**: Success message (text)

### `/cgi-bin/rfid_list`

**Description**: Lists RFID tags.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/rfid_list
```

**Expected Response**: List of RFID tags (text)

### `/cgi-bin/rfid_list_ext`

**Description**: Lists RFID tags with details.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/rfid_list_ext
```

**Expected Response**: List of RFID tags with details (text)

### `/cgi-bin/rfid_delete...`

**Description**: Deletes an RFID tag.

**Method**: GET

**Parameters**: Tag ID (appended to URL)

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/rfid_delete_tag123
```

**Expected Response**: Success message (text)

### `/cgi-bin/rfid_unassign...`

**Description**: Unassigns an RFID tag from actions.

**Method**: GET

**Parameters**: Tag ID (appended to URL)

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/rfid_unassign_tag123
```

**Expected Response**: Success message (text)

### `/cgi-bin/rfid_rename...`

**Description**: Renames an RFID tag.

**Method**: GET

**Parameters**: Tag ID and new name (appended to URL)

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/rfid_rename_tag123_newname
```

**Expected Response**: Success message (text)

---

## Sound List Endpoints

### `/cgi-bin/sound_list`

**Description**: Lists available local sounds.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/sound_list
```

**Expected Response**: List of sound IDs (text)

### `/cgi-bin/voice_list`

**Description**: Lists available TTS voices.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/voice_list
```

**Expected Response**: List of voice IDs (text)

### `/cgi-bin/moods_list`

**Description**: Lists available moods.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/moods_list
```

**Expected Response**: List of mood IDs (text)

### `/cgi-bin/radio_list`

**Description**: Lists available radio stations.

**Method**: GET

**Parameters**: None

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/radio_list
```

**Expected Response**: List of radio station URLs (text)

---

## Squeezebox

### `/cgi-bin/squeezebox?cmd=...`

**Description**: Controls Squeezebox player.

**Method**: GET

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `cmd` | Yes | Command: `start` or `stop` |

**Test Requests**:
```
GET http://192.168.1.70/cgi-bin/squeezebox?cmd=start
GET http://192.168.1.70/cgi-bin/squeezebox?cmd=stop
```

**Expected Response**: Success message (text)

---

## FTP Upload

### `/cgi-bin/snapshot_ftp?server=...&user=...&password=...&remote_dir=...`

**Description**: Takes snapshot and uploads via FTP.

**Method**: GET

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `server` | Yes | FTP server IP |
| `user` | Yes | FTP username |
| `password` | Yes | FTP password |
| `remote_dir` | Yes | Remote directory |

**Test Request**:
```
GET http://192.168.1.70/cgi-bin/snapshot_ftp?server=192.168.1.100&user=ftpuser&password=ftppass&remote_dir=/pictures
```

**Expected Response**: Success message (text)

---

## Notes

1. All endpoints use HTTP GET method unless otherwise specified
2. Parameters should be URL-encoded when containing special characters
3. Response format is typically plain text success message
4. Storage endpoints return JSON format
5. List endpoints return text lists (one item per line or comma-separated)
6. The API is designed for local network use only
7. No authentication is required for any endpoints