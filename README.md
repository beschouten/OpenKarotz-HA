# Open Karotz — Home Assistant Integration

Full-featured Home Assistant integration for the **Parrot Karotz** robot with the
[OpenKarotz](https://www.openkarotz.org/) open firmware.

Built and live-verified against firmware **web 210 / rootfs 12.07.19.00 / patch 222**.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-4.0.0-green.svg)](https://github.com/beschouten/OpenKarotz-HA/releases)

## Features

| Feature | Entity | Notes |
|---|---|---|
| Nose LED | `light` | RGB + pulse/blink effects, real state from device |
| Ear positions | 2× `number` (0–16) | Left/right, instant (`noreset`) |
| Ear motors | `switch` | Enable/disable motor mode |
| Sleep mode | `switch` | Sleep / wake (state follows device) |
| Moods | `media_player` sources | All 305 device moods in the source list |
| Sounds | `media_player` sources + `select` | 14 built-in sounds |
| Text-to-speech | `tts` entity + legacy `open_karotz.tts` | Device-side TTS, numeric voice ids |
| Camera | `camera` | Fresh snapshot on every image request |
| Sensors | 13× `sensor` | Storage, versions, mood/sound/tag counts, TTS cache |
| Maintenance | 3× `button` | Sync clock (NTP), clear TTS cache, reboot |
| RFID tags | services + `open_karotz_tag_scanned` event | See [RFID tags](#rfid-tags) |

## Installation (HACS)

1. Install [HACS](https://hacs.xyz/)
2. **HACS → Integrations → ⋮ (top right) → Custom repositories → +**, repository
   `https://github.com/beschouten/OpenKarotz-HA`, type **Integration**
3. Search **Open Karotz** → **Download**
4. Restart Home Assistant
5. **Settings → Devices & Services → Add Integration → Open Karotz**, enter the
   device IP (e.g. `192.168.1.70`)

Manual install: copy `custom_components/open_karotz/` into your
`config/custom_components/` and restart.

**Finding the device IP**: router DHCP list, the Karotz display, or
`nmap -sn 192.168.1.0/24 | grep -i karotz`.

## Text-to-speech

Either the `tts` entity (`tts.open_karotz_text_to_speech`) or the legacy service:

```yaml
action: open_karotz.tts
data:
  text: "Welcome home!"
  voice: "6"   # optional, see below
```

Voices are the device's numeric ids (1–88, 30+ languages). Common ones:
**6** English (US) Female (default), **7** English (UK) Male, **1** French Male,
**2** French Female, **13** Spanish Male, **25** Brazilian Portuguese Male.
Keep text under ~200 characters.

## RFID tags

The Karotz executes a URL when an RFID tag is presented to its nose. This
integration uses that as a scan trigger:

1. **Enroll a tag**: call `open_karotz.rfid_start_record`, present the tag to
   the nose, then `open_karotz.rfid_stop_record`.
2. **Point it at Home Assistant**: call `open_karotz.rfid_assign_webhook` with
   the tag id (visible in the device web UI or via `rfid_list`).
3. **Automate**: each scan fires an `open_karotz_tag_scanned` event:

```yaml
automation:
  - trigger:
      - platform: event
        event_type: open_karotz_tag_scanned
        event_data:
          tag_id: "YOUR_TAG_ID"
    action:
      - action: light.turn_on
        target:
          entity_id: light.living_room
```

Other tag services: `rfid_rename`, `rfid_delete`.

## Device behaviour notes (live-verified)

Firmware characteristics the integration handles internally — useful when
writing automations:

- **Serialized API**: the device's web server refuses concurrent requests. The
  integration queues all calls; avoid hitting the CGI endpoints directly in
  parallel with automations.
- **Fire-and-forget endpoints**: `sleep`, `wakeup`, `rfid_start_record` and mood
  playback trigger an ears-reset routine that can hang the CGI for 10–60 s. The
  integration dispatches them with a short timeout and reads the truth from
  status polling — a service call returning quickly does **not** mean the action
  finished. State (e.g. the sleep switch) converges within ~15–30 s.
- **No audio control**: `sound_control` (stop/volume) is dead on current
  firmware. The media player is play-only: no volume, no stop.
- **Snapshot CGI** occasionally returns malformed HTTP (D-Bus leakage); the
  integration uses a tolerant raw client and retries once.

## Limitations

- **Play-only media player** — firmware offers no stop/pause/volume.
- **Recorder attribute size**: the mood source list (305 entries) exceeds the
  recorder's 16 KB attribute limit, so `media_player` state history is not
  stored (functionality is unaffected). Add it to `recorder: exclude:` to
  silence the log note.
- **Entity ids** are auto-generated (`sensor.open_karotz_3` style) because
  entity names are translated; rename entities freely in the UI.
- **Squeezebox** CGI exists on the device but does not start a player on current
  firmware — not exposed.
- **Ears are `number` entities now**: v4 replaced the v3 `cover` entities;
  update automations referencing `cover.open_karotz_*`.

## Upgrading from v3

- Config entry migrates automatically (unique_id backfilled from the device MAC).
- Removed platforms: `cover` (ears → numbers), `binary_sensor` (RFID → event).
- Removed services: everything except `tts` (kept for compatibility) plus the
  new `rfid_*` services.

## Troubleshooting

- **Integration fails to load** — check Settings → Devices & Services; a bad IP
  shows a clear config error. The device must be reachable (it sleeps at night
  by default).
- **Actions seem to do nothing** — remember the fire-and-forget behaviour above;
  wait ~30 s and check the device state.
- **TTS silent** — verify voice id (1–88), keep text short, confirm the device
  is awake.
- **Diagnostics**: Settings → Devices & Services → Open Karotz → ⋯ → Download
  diagnostics includes the last status payload and poll counters.

## Development

```bash
python -m pytest tests/ -q          # unit tests (live-fixture based)
ruff check custom_components/open_karotz
```

See `plans/v4-implementation-plan.md` for the architecture and the full list of
firmware findings (B1–B14, N1–N9) that shaped the API client.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

- [OpenKarotz](https://openkarotz.org/) for the open firmware
- [rofra's websources installer](https://github.com/rofra/karotz-openkarotz-websources-installer) for the CGI sources
- [Home Assistant](https://www.home-assistant.io/) for the platform
