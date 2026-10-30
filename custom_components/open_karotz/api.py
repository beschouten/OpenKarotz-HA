"""API client for OpenKarotz devices.

Design constraints (live-verified on firmware web 210 / rootfs 12.07.19.00):
- The device runs busybox httpd which REFUSES concurrent requests: exactly one
  request may be in flight at a time (enforced with an asyncio lock).
- Playback endpoints (sound?id=, apps/moods) are synchronous and block the CGI
  until audio finishes -> long timeouts.
- Endpoints that call EarsReset (sleep, wakeup, ears_reset, ears_random,
  rfid_start_record) hang for 60s+ on affected units -> fire-and-forget mode:
  short timeout, timeout is NOT an error, truth comes from status polling.
- Response schemas are not uniform: status/get_free_space have no "return"
  field, tts returns a boolean, some scripts emit malformed JSON.
"""
from __future__ import annotations

import asyncio
import json
import logging
import socket
from typing import Any
from urllib.parse import quote

import aiohttp

_LOGGER = logging.getLogger(__name__)

TIMEOUT_STATUS = 10
TIMEOUT_ACTION = 15
TIMEOUT_PLAYBACK = 180
TIMEOUT_FAF = 2  # fire-and-forget


class OpenKarotzError(Exception):
    """Base error."""


class OpenKarotzConnectionError(OpenKarotzError):
    """Device unreachable (maps to ConfigEntryNotReady)."""


class OpenKarotzRefused(OpenKarotzError):
    """Device returned return != 0 (e.g. 'rabbit is sleeping')."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg = msg


class OpenKarotzAPI:
    """Serialized HTTP client for one OpenKarotz device."""

    def __init__(self, host: str, websession: aiohttp.ClientSession) -> None:
        self._host = host
        self._session = websession
        self._lock = asyncio.Lock()

    @property
    def host(self) -> str:
        return self._host

    @property
    def base(self) -> str:
        return f"http://{self._host}"

    # ------------------------------------------------------------------ core
    async def _raw_get(self, path: str, timeout: float) -> bytes:
        """Minimal HTTP/1.0 client for CGIs that emit non-compliant responses.

        The snapshot CGI leaks a D-Bus reply between the status line and the
        headers ("Invalid header token" for aiohttp); curl tolerates it, so
        we read until EOF and parse leniently. Runs on a thread: asyncio's
        StreamReader returns early on this server's status-line-then-pause
        write pattern, a blocking socket does not.
        """
        def _fetch() -> bytes:
            with socket.create_connection((self._host, 80), timeout=timeout) as sock:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.sendall(
                    f"GET {path} HTTP/1.0\r\nHost: {self._host}\r\n\r\n".encode()
                )
                buf = bytearray()
                while chunk := sock.recv(65536):
                    buf.extend(chunk)
                    if len(buf) > 2_000_000:
                        break
                return bytes(buf)

        try:
            data = await asyncio.to_thread(_fetch)
        except (OSError, ConnectionResetError) as exc:
            raise OpenKarotzConnectionError(f"{path}: {exc}") from exc
        # Header block uses mixed line endings (status line \r\n, CGI echo
        # headers bare \n). Body starts at the first blank line of either
        # flavour; binary bodies are safe because the real separator always
        # precedes any \n\n that may occur inside the payload.
        cut_crlf = data.find(b"\r\n\r\n")
        cut_lf = data.find(b"\n\n")
        candidates = [i for i in (cut_crlf, cut_lf) if i != -1]
        if not candidates:
            raise OpenKarotzRefused(f"{path}: malformed HTTP response")
        cut = min(candidates)
        head = data[:cut]
        body = data[cut + (4 if cut == cut_crlf else 2):]
        if not head.startswith(b"HTTP/"):
            raise OpenKarotzRefused(f"{path}: malformed HTTP response")
        return body

    async def _get(
        self,
        path: str,
        *,
        timeout: float = TIMEOUT_ACTION,
        raw: bool = False,
    ) -> Any:
        """One in-flight GET. Returns parsed JSON dict (or bytes if raw).

        Raises OpenKarotzConnectionError on connect/transport failure and
        OpenKarotzRefused when the payload carries return != 0.
        """
        url = f"{self.base}{path}"
        async with self._lock:
            try:
                async with self._session.get(
                    url, timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    if resp.status == 404:
                        raise OpenKarotzRefused(f"{path}: endpoint not found (404)")
                    body = await resp.read()
            except asyncio.TimeoutError as err:
                raise OpenKarotzConnectionError(f"{path}: timeout") from err
            except aiohttp.ClientError as err:
                raise OpenKarotzConnectionError(f"{path}: {err}") from err

        if raw:
            return body
        try:
            data = json.loads(body.decode("utf-8", "replace"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            _LOGGER.debug("Non-JSON response from %s: %.120s", path, body)
            raise OpenKarotzRefused(f"{path}: malformed response") from exc
        if isinstance(data, dict) and not self.ok(data):
            raise OpenKarotzRefused(str(data.get("msg") or data.get("return")))
        return data

    async def _faf(self, path: str) -> bool:
        """Fire-and-forget: dispatch, return False if it hangs (expected)."""
        try:
            await self._get(path, timeout=TIMEOUT_FAF)
            return True
        except OpenKarotzError:
            _LOGGER.debug("fire-and-forget %s dispatched (no prompt ack)", path)
            return False

    @staticmethod
    def ok(data: dict) -> bool:
        """Schema-tolerant success check: '0', 0, True or missing return."""
        ret = data.get("return", "0")
        return ret in ("0", 0, True, "true", "True")

    @staticmethod
    def _params(**kwargs: object) -> str:
        parts = []
        for key, val in kwargs.items():
            if val is None:
                continue
            parts.append(f"{key}={quote(str(val), safe='')}")
        return ("?" + "&".join(parts)) if parts else ""

    # ------------------------------------------------------------- telemetry
    async def get_status(self) -> dict:
        return await self._get("/cgi-bin/status", timeout=TIMEOUT_STATUS)

    async def get_version(self) -> dict:
        return await self._get("/cgi-bin/get_version", timeout=TIMEOUT_STATUS)

    async def get_free_space(self) -> dict:
        return await self._get("/cgi-bin/get_free_space", timeout=TIMEOUT_STATUS)

    async def voice_list(self) -> list[dict]:
        data = await self._get("/cgi-bin/voice_list", timeout=TIMEOUT_STATUS)
        return data.get("voices", [])

    async def sound_list(self) -> list[dict]:
        data = await self._get("/cgi-bin/sound_list", timeout=TIMEOUT_STATUS)
        return data.get("sounds", [])

    async def moods_list(self) -> list[dict]:
        data = await self._get("/cgi-bin/moods_list", timeout=TIMEOUT_STATUS)
        return data.get("moods", [])

    async def radios_list(self) -> list[dict]:
        data = await self._get("/cgi-bin/radios_list", timeout=TIMEOUT_STATUS)
        return data.get("streams", [])

    async def display_cache(self) -> dict:
        return await self._get("/cgi-bin/display_cache", timeout=TIMEOUT_STATUS)

    # ------------------------------------------------------------------ led
    async def set_led(
        self,
        color: str,
        *,
        color2: str | None = None,
        pulse: int | None = None,
        blink: int | None = None,
        speed: int | None = None,
        nomemory: int | None = None,
    ) -> dict:
        return await self._get(
            "/cgi-bin/leds"
            + self._params(
                color=color, color2=color2, pulse=pulse, blink=blink,
                speed=speed, nomemory=nomemory,
            )
        )

    # ----------------------------------------------------------------- ears
    async def ears_move(self, left: int, right: int) -> dict:
        """Move ears 0-16. Always noreset=1: the reset path hangs on this fw."""
        return await self._get(
            "/cgi-bin/ears" + self._params(left=left, right=right, noreset=1)
        )

    async def ears_mode(self, disable: bool) -> dict | bool:
        """Enable/disable ear motors. Enable path runs EarsReset -> FAF."""
        path = "/cgi-bin/ears_mode" + self._params(disable=1 if disable else 0)
        if disable:
            return await self._get(path)
        return await self._faf(path)

    # ---------------------------------------------------------------- audio
    async def play_sound(self, sound_id: str) -> dict:
        return await self._get(
            "/cgi-bin/sound" + self._params(id=sound_id), timeout=TIMEOUT_PLAYBACK
        )

    async def play_mood(self, mood_id: str | None = None) -> bool:
        """Play a mood. The moods CGI runs EarsReset after audio (hangs on
        this firmware), so this is fire-and-forget: audio plays, the CGI
        never returns. Returns False when (expectedly) unacked."""
        return await self._faf(
            "/cgi-bin/apps/moods" + self._params(id=mood_id)
        )

    async def tts(
        self,
        text: str,
        *,
        voice: str | None = None,
        engine: str | None = None,
        speed: str | None = None,
        nocache: bool = False,
        mute: bool = False,
    ) -> dict:
        return await self._get(
            "/cgi-bin/tts"
            + self._params(
                text=text, voice=voice, engine=engine, speed=speed,
                nocache=1 if nocache else None, mute=1 if mute else None,
            ),
            timeout=TIMEOUT_PLAYBACK,
        )

    # --------------------------------------------------------------- camera
    async def snapshot(self, silent: bool = True) -> dict:
        """Returns {'filename':..., 'thumb':...} — NOT image bytes.

        Uses the raw client: this CGI leaks D-Bus output into the HTTP
        header block, which aiohttp rejects outright.
        """
        path = "/cgi-bin/snapshot" + self._params(silent=1 if silent else None)
        async with self._lock:
            body = await self._raw_get(path, timeout=TIMEOUT_PLAYBACK)
        try:
            data = json.loads(body.decode("utf-8", "replace"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise OpenKarotzRefused(f"{path}: malformed snapshot response") from exc
        if isinstance(data, dict) and not self.ok(data):
            raise OpenKarotzRefused(str(data.get("msg") or data.get("return")))
        return data

    async def snapshot_get(self, filename: str) -> bytes:
        # raw client too: same CGI family, binary-safe (reads to EOF)
        async with self._lock:
            return await self._raw_get(
                "/cgi-bin/snapshot_get" + self._params(filename=filename),
                timeout=TIMEOUT_PLAYBACK,
            )

    async def snapshot_list(self) -> list[dict]:
        data = await self._get("/cgi-bin/snapshot_list", timeout=TIMEOUT_STATUS)
        return data.get("snapshots", [])

    async def clear_snapshots(self) -> dict:
        return await self._get("/cgi-bin/clear_snapshots")

    # --------------------------------------------------------------- system
    async def sleep(self) -> bool:
        return await self._faf("/cgi-bin/sleep")

    async def wakeup(self, silent: bool = False) -> bool:
        return await self._faf(
            "/cgi-bin/wakeup" + self._params(silent=1 if silent else None)
        )

    async def clear_cache(self) -> dict:
        return await self._get("/cgi-bin/clear_cache")

    async def setclock(self) -> dict:
        return await self._get("/cgi-bin/setclock", timeout=TIMEOUT_PLAYBACK)

    async def reboot(self) -> dict:
        return await self._get("/cgi-bin/reboot")

    async def squeezebox(self, cmd: str) -> dict:
        return await self._get(
            "/cgi-bin/squeezebox" + self._params(cmd=cmd), timeout=TIMEOUT_PLAYBACK
        )

    # ----------------------------------------------------------------- rfid
    async def rfid_list(self) -> list[dict]:
        data = await self._get("/cgi-bin/rfid_list", timeout=TIMEOUT_STATUS)
        return data.get("tags", [])

    async def rfid_info(self, tag: str) -> dict:
        return await self._get("/cgi-bin/rfid_info" + self._params(tag=tag))

    async def rfid_rename(
        self, tag: str, name: str | None = None, color: str | None = None
    ) -> dict:
        return await self._get(
            "/cgi-bin/rfid_rename" + self._params(tag=tag, name=name, color=color)
        )

    async def rfid_delete(self, tag: str) -> dict:
        return await self._get("/cgi-bin/rfid_delete" + self._params(tag=tag))

    async def rfid_start_record(self) -> bool:
        return await self._faf("/cgi-bin/rfid_start_record")

    async def rfid_stop_record(self) -> dict:
        return await self._get("/cgi-bin/rfid_stop_record", timeout=TIMEOUT_PLAYBACK)

    async def rfid_assign_url(
        self, tag: str, url: str, param: str | None = None, name: str | None = None
    ) -> dict:
        return await self._get(
            "/cgi-bin/rfid_assign_url"
            + self._params(tag=tag, url=url, param=param, name=name)
        )
