# v4.0.0

A ground-up rewrite of the API client and entity model, built from a full
live-device audit of the OpenKarotz firmware CGIs (web 210 / rootfs
12.07.19.00 / patch 222). Every exposed feature was verified against a real
device; features that do not work on current firmware were removed.

## Breaking changes

- **Ears**: `cover` entities replaced by two `number` entities (0–16, instant
  `noreset` moves). Update automations.
- **RFID**: `binary_sensor` replaced by the `open_karotz_tag_scanned` event +
  `rfid_*` services (see README).
- **Media player is play-only**: firmware `sound_control` (stop/volume) is dead;
  the entity no longer exposes volume/stop.
- **Services trimmed to what works**: only `tts` (compat) plus the new `rfid_*`
  services remain.
- Config entry migrates to v2 automatically (unique_id from device MAC).

## Added

- **LED effects**: pulse and blink (inactive CGI params are omitted — the CGI
  treats present-but-zero as active).
- **Sleep switch** with state tracking via status polling (hanging CGIs handled
  fire-and-forget).
- **Camera** using the correct two-step flow (`snapshot` → `snapshot_get`) with
  a tolerant raw HTTP client for the CGI's D-Bus leakage.
- **Buttons**: sync clock (NTP), clear TTS cache, reboot.
- **TTS entity** (`tts` platform) alongside the legacy service.
- **RFID**: enroll/rename/delete services and per-tag webhook assignment so a
  physical tag scan fires `open_karotz_tag_scanned` (device_id + tag_id).
- **Diagnostics** download (status payload, versions, poll counters).
- 13 sensors: storage %, free space, TTS cache, mood/sound/story/tag counts,
  sleep timestamp, web/rootfs/patch versions.

## Fixed (from the live audit, B1–B14 / N1–N9)

- All API calls serialized (device refuses concurrent requests).
- Correct timeouts per endpoint class; hanging CGIs (ears-reset family) are
  fire-and-forget with state read back from `status`.
- `snapshot` no longer treated as image bytes (it returns JSON).
- Schema-tolerant parsing (missing `return` fields, boolean `tts` reply,
  malformed JSON).
- Config flow validates reachability and derives unique_id from the MAC;
  duplicate entries are rejected.
- Real device state for light/ears/sleep instead of optimistic guesses.

## Removed

- Squeezebox support (CGI no-ops on current firmware).
- Dead v3 services and the v3 YAML import path.

# Release Notes - v3.0.0

Historical (v3) release notes preserved below.

## Overview
Major release v3.0.0 with significant architectural improvements and new features.

## Highlights (v3)
- Independent ear rotation control, TTS encoding fixes, service registration
  rework, storage sensors, LED control, media player, mood control, camera,
  sleep switch, RFID sensor.
- Tested endpoints list and known issues of the v3 era (superseded by the v4
  live audit — see `plans/v4-implementation-plan.md`).
