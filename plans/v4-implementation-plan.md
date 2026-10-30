# OpenKarotz-HA v4 — Implementation Plan

**Status:** DRAFT FOR REVIEW · 2026-10-30
**Branch:** `v4-dev` (from master @ v3.0.0 / 36603cb) · **Target:** v4.0.0 release
**Inputs:** `/opt/data/karotz-refactor-plan.md` (bug list B1–B14), live probe fixtures `karotz-live/results.json` (findings N1–N9, ~80 verified endpoint calls on firmware web 210 / rootfs 12.07.19.00 / patch 222)

---

## 1. Scope

**In scope (all live-verified working):**
- Fix every bug B1–B14 + new findings N1–N9
- Core rewrite: serialized API client, `status`-based coordinator, validated config flow, DeviceInfo, config-entry migration
- Full LED (color/pulse/blink/speed + real state), ears (noreset moves + mode switch), sounds, moods (305 named), TTS (voices/engines/cache), camera (correct snapshot flow), sleep state, storage/version sensors, RFID registry + webhook scan events, system buttons (snapshot, setclock, clear cache/snapshots, reboot)

**Out of scope (verified broken or risky on this firmware):**
- Media stop/pause/volume (`sound_control` dead — N1), URL/stream playback (N5)
- `webcam` MJPEG stream (no data in 8 s — unreliable)
- Stories (app not installed; feature-gate if dir appears), `update`/`flash_update` (firmware flash risk), `check_health` (reboots on ping fail), `cmd` (shell eval), `sendmail`
- Squeezebox: include as opt-in switch ONLY if `squeezebox?cmd=start` verifies working (was untested — device asleep during probe); otherwise drop

## 2. Architecture

### 2.1 `api.py` — rewritten client
- Single shared `aiohttp` session; **global `asyncio.Lock` — exactly one in-flight request** (N3: httpd refuses concurrency).
- Per-call timeouts: status/list 10 s; actions 15 s; playback (`sound?id=`, `apps/moods`) 90 s (N4: synchronous playback); **fire-and-forget mode** (2 s timeout, swallow timeout) for `sleep`, `wakeup`, `ears_reset`, `ears_random`, `rfid_start_record` (N2: hang on EarsReset).
- Schema-tolerant JSON parse: no `return` field (`status`, `get_free_space`), boolean `return` (`tts`), malformed JSON tolerated (N7). Helper `ok(data)` handles `"0"`/`0`/`True`.
- Raise `ConfigEntryNotReady` on connect errors, `ApiError(msg)` on `return != 0` refusals (e.g. "rabbit is sleeping").
- All query params URL-encoded centrally (fixes B9).

### 2.2 `__init__.py` — coordinator + services
- `DataUpdateCoordinator` polls `/cgi-bin/status` every **60 s** (single request; gentle on device) + one-time `get_version`, `voice_list`, `sound_list`, `moods_list`, `radios_list` discovery at setup (runtime discovery — no hardcoded lists).
- `entry.runtime_data` = dataclass `{api, coordinator, capabilities}`; all platforms use `CoordinatorEntity`.
- Config entry **version 2** migration: backfill `unique_id` = wlan_mac (verified `00:0E:8E:2D:29:07`).
- Services: proper voluptuous schemas, `entity` selectors, target by entity → entry resolution, normal registration (drop admin-only), loop-safe for multi-device (fixes B11).

### 2.3 `config_flow.py`
- Validate by GET `status` (fixes B10); abort if already configured (unique_id); reconfigure step (host change); options: poll interval, default TTS voice/engine, snapshot sound.

## 3. Entity catalog (final)

| Platform | Entities | Notes |
|---|---|---|
| sensor | storage %, usb % (fix B4, normalize `""`/`-1`), firmware/rootfs/patch version, sleep time, TTS cache size, tags/moods/sounds counts | from `status`+`get_version` |
| light | LED RGB + **effects: pulse (color2+speed), blink** | real state from `status.led_color/led_pulse` (fixes optimistic-only) |
| number | ear left, ear right (0–16, `noreset=1`) | replaces cover (see D1) |
| switch | sleep (state = `status.sleep`; on=awake), ears mode, squeezebox (if verified) | sleep/wake fire-and-forget (N2/N8) |
| select | mood (305 **named**, HTML-unescaped), sound, radio stream | `apps/moods` fire-and-forget-ish (90 s timeout) |
| media_player | **play-only**: `play_media` (sound id / tts text), playing/idle tracked from call lifecycle | no volume/stop (N1) — see D2 |
| tts | HA `tts` entity (engine/voice/speed/nocache options) | keeps `open_karotz.tts` service for back-compat |
| camera | snapshot via `snapshot` → `snapshot_get` (fixes N6); motion stubs removed | optional `send_snapshot` service |
| event | RFID scan events (webhook via `rfid_assign_url`), per-tag + catch-all | zero tags today — dormant until tags enrolled |
| button | snapshot now, sync clock, clear TTS cache, clear snapshots, reboot | reboot = self-heal after hung ear calls (N9) |
| binary_sensor | — (bogus RFID presence sensor removed, B6) | entity-registry cleanup |

**Removed:** cover (or deprecated — D1), `update.open_karotz_update` stale entity cleanup.

## 4. Bug → fix map

B1 wake_up→wakeup (fire-forget) · B2/B3 stop/volume → **feature removed** (N1) · B4 flat keys + real interval · B5 coordinator interval · B6 → event platform + webhook · B7 ear read removed (write-only, documented) · B8 runtime `voice_list` · B9 central encoding · B10 flow validates + unique_id · B11 entity-targeted services · B12 correct snapshot flow, no motion stubs · B13 BASE_URL deleted · B14 single client via runtime_data · N1–N9 per §2.

## 5. Phases & acceptance criteria

| # | Deliverable | Acceptance (verified on live device) |
|---|---|---|
| P1 | api.py + coordinator + config flow + migration + DeviceInfo | entry loads with unique_id; status polled; wrong-IP flow errors; migration keeps existing entry |
| P2 | sensors + light (effects) + ears numbers + ears_mode | LED pulse/blink visible on device; `status` reflects color; ear moves ≤5 s; no hung CGIs after 10 min |
| P3 | sounds/moods selects + media_player + tts entity/platform | named mood plays; TTS speaks via entity + legacy service; automations using `open_karotz.tts` still fire |
| P4 | camera + buttons + sleep switch | snapshot image renders in HA; reboot button returns device in ~20 s; sleep switch state follows `status.sleep` |
| P5 | RFID registry + webhook events + services (record/rename/delete/assign) | simulated `rfid_assign_url` webhook call fires `open_karotz.rfid_scan` event (no physical tag needed to verify plumbing) |
| P6 | services cleanup + stale-entity cleanup + README/docs rewrite + CONFIGURATION_EXAMPLES (RFID + TTS automations) | docs match verified behavior incl. limitations section |
| P7 | tests + CI + release | pytest suite green (mocked firmware from fixtures); manifest 4.0.0; PR v4-dev→master; `gh release create v4.0.0`; HACS update; HA entry re-enabled and all entities verified in UI |

**Definition of done per phase:** deployed to `/logs/homeassistant/custom_components/open_karotz`, HA restarted, entry enabled, entities observed with real states (no `unknown` where device data exists), `home-assistant.log` clean of open_karotz errors, device `ps` free of stuck CGIs.

## 6. Quality bar
- Tests: unit (api parsing incl. schema quirks N7, fire-and-forget timeout paths, coordinator), platform tests with mocked coordinator, integration tests gated on `--device` flag using live device. Fixtures from the live probe committed under `tests/fixtures/live/`.
- Lint: ruff + `hassfest`-style manifest check; `pylint`-clean per HA core conventions.
- Every endpoint call in code must exist in the verified-working list (§1) — no speculative endpoints.
- README "Known limitations" section: no volume/stop, write-only ears, ear-reset hang workaround, single-request constraint.

## 7. Risks
- Ear-reset hang is likely mechanical (hangs cold-booted) — integration works around it, but flag to Steve for physical inspection.
- Fire-and-forget calls can still queue-block the device for ~60 s; mitigated by client-side "quiet period" after a timeout (no new requests until `status` responds twice).
- RFID webhook requires HA reachable from device (LAN — fine).
- Squeezebox unverified — P4 gate decides include/drop.

## 8. Decisions (RESOLVED 2026-10-30 with Steve)
- **D1** Ears: two `number` entities (0–16, `noreset=1`), **cover dropped** (entity-registry cleanup on migration).
- **D2** media_player: **play-only** (sound id + TTS text); no volume/stop — documented as firmware limitation.
- **D3** RFID webhook plumbing: **build in v4.0** (dormant until tags enrolled).
- **D4** Squeezebox: include switch **only if live-verified** in P4 (`squeezebox?cmd=start/stop` while awake); else drop.
- **D5** Release: **PR `v4-dev` → `master`**, then `gh release create v4.0.0`.
