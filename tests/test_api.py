"""Unit tests for the v4 OpenKarotz API client.

Fixtures mirror live device responses captured on firmware web 210 /
rootfs 12.07.19.00 / patch 222 (see plans/v4-implementation-plan.md).
"""
import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest

from .conftest import RespCtx, api_mod, make_session

OpenKarotzAPI = api_mod.OpenKarotzAPI
OpenKarotzConnectionError = api_mod.OpenKarotzConnectionError
OpenKarotzRefused = api_mod.OpenKarotzRefused

# --- live fixtures ---------------------------------------------------------
STATUS = {
    "version": "200", "ears_disabled": "0", "sleep": "0", "sleep_time": "0",
    "led_color": "00FF00", "led_pulse": "1", "tts_cache_size": "0",
    "usb_free_space": "-1", "karotz_free_space": "147.4M",
    "eth_mac": "00:00:00:00:00:00", "wlan_mac": "00:0E:8E:2D:29:07",
    "nb_tags": "0", "nb_moods": "305", "nb_sounds": "14", "nb_stories": "0",
    "karotz_percent_used_space": "37", "usb_percent_used_space": "",
    "data_dir": "/usr/openkarotz",
}


class TestStatus:
    async def test_status_parses_without_return_field(self, api):
        # status has NO "return" field — must still succeed (finding N5)
        api._session = make_session([RespCtx(json_data=STATUS)])
        data = await api.get_status()
        assert data["wlan_mac"] == "00:0E:8E:2D:29:07"
        assert api.ok(data) is True

    async def test_connection_error_maps(self):
        import aiohttp

        api = OpenKarotzAPI("10.0.0.1", make_session([aiohttp.ClientConnectorError(
            MagicMock(), MagicMock())]))
        with pytest.raises(OpenKarotzConnectionError):
            await api.get_status()

    async def test_refused_raises(self, api):
        api._session = make_session([RespCtx(json_data={"return": "1", "msg": "rabbit is sleeping"})])
        with pytest.raises(OpenKarotzRefused):
            await api.get_status()


class TestOkSemantics:
    def test_missing_return_is_ok(self, api):
        assert api.ok({"version": "200"}) is True

    def test_zero_string_is_ok(self, api):
        assert api.ok({"return": "0"}) is True

    def test_nonzero_is_not_ok(self, api):
        assert api.ok({"return": 1}) is False


class TestFireAndForget:
    async def test_timeout_is_not_an_error(self, api):
        # _get maps asyncio timeouts to OpenKarotzConnectionError; FAF swallows it
        async def slow(*a, **k):
            raise OpenKarotzConnectionError("timeout")

        api._get = slow
        assert await api._faf("/cgi-bin/sleep") is False

    async def test_fast_reply_returns_true(self, api):
        async def fast(*a, **k):
            return {"return": "0"}

        api._get = fast
        assert await api._faf("/cgi-bin/sleep") is True


class TestRawClient:
    """The snapshot CGI leaks D-Bus text into the header block (finding N3/N9)."""

    RAW_SNAPSHOT = (
        b"HTTP/1.0 200 OK\r\n"
        b"method return sender=:1.2 -> dest=:1.34 reply_serial=2\n"
        b"   boolean true\n"
        b"Server: OpenKarotz WebServer 1.0 - Massalia 2013\n"
        b"Connection: close\n"
        b"Content-type: application/json\n"
        b"\n"
        b'{"filename":"snapshot_x.jpg","thumb":"snapshot_x.thumb.gif","return":"0"}\n'
    )

    def _fake_socket(self, data):
        sock = MagicMock()
        sock.recv = MagicMock(side_effect=[data, b""])
        sock.sendall = MagicMock()
        sock.setsockopt = MagicMock()
        sock.__enter__ = MagicMock(return_value=sock)
        sock.__exit__ = MagicMock(return_value=False)
        return sock

    async def test_mixed_line_endings_and_dbus_garbage(self, api):
        sock = self._fake_socket(self.RAW_SNAPSHOT)
        with patch("socket.create_connection", return_value=sock):
            body = await api._raw_get("/cgi-bin/snapshot", timeout=5)
        assert json.loads(body)["filename"] == "snapshot_x.jpg"

    async def test_binary_body_preserved(self, api):
        raw = (
            b"HTTP/1.0 200 OK\r\nServer: x\nContent-type: image/jpeg\n\n"
            b"\xff\xd8\xff\xe0JPEGBODY\xff\x00\x0a\x0a"
        )
        sock = self._fake_socket(raw)
        with patch("socket.create_connection", return_value=sock):
            body = await api._raw_get("/cgi-bin/snapshot_get?filename=a.jpg", timeout=5)
        assert body.startswith(b"\xff\xd8\xff\xe0")
        assert body.endswith(b"\x0a\x0a")

    async def test_malformed_rejected(self, api):
        sock = self._fake_socket(b"garbage without status line")
        with patch("socket.create_connection", return_value=sock), pytest.raises(OpenKarotzRefused):
            await api._raw_get("/cgi-bin/snapshot", timeout=5)


class TestSnapshotFlow:
    async def test_snapshot_uses_raw_client_and_parses_json(self, api):
        async def fake_raw(path, timeout):
            assert path.startswith("/cgi-bin/snapshot?silent=1")
            return b'{"filename":"s.jpg","thumb":"s.thumb.gif","return":"0"}'

        api._raw_get = fake_raw
        meta = await api.snapshot()
        assert meta["filename"] == "s.jpg"

    async def test_snapshot_error_payload(self, api):
        async def fake_raw(path, timeout):
            return b'{"return":"1","msg":"Unable to take snapshot."}'

        api._raw_get = fake_raw
        with pytest.raises(OpenKarotzRefused):
            await api.snapshot()


class TestParamEncoding:
    async def test_ears_uses_noreset(self, api):
        seen = []

        async def fake_get(path, **kw):
            seen.append(path)
            return {"return": "0"}

        api._get = fake_get
        await api.ears_move(3, 12)
        assert "left=3" in seen[0] and "right=12" in seen[0] and "noreset=1" in seen[0]

    async def test_none_params_omitted(self, api):
        assert api._params(a=1, b=None, c=0) == "?a=1&c=0"

    async def test_tts_boolean_reply_accepted(self, api):
        # tts replies `true` (not JSON object) on this firmware (finding N5)
        api._session = make_session([RespCtx(json_data=True)])
        await api.tts("hello")

    async def test_tts_url_encodes_text(self, api):
        seen = []

        async def fake_get(path, **kw):
            seen.append(path)
            return {"return": "0"}

        api._get = fake_get
        await api.tts("héllo wörld")
        assert "%25" not in seen[0]  # no double-encoding
        assert "h%C3%A9llo" in seen[0]


class TestSerialization:
    async def test_concurrent_calls_are_queued(self):
        """busybox httpd refuses concurrent requests (finding N4)."""
        active = {"n": 0, "max": 0}

        api = OpenKarotzAPI("h", make_session([]))

        async def fake_get(path, **kw):
            active["n"] += 1
            active["max"] = max(active["max"], active["n"])
            await asyncio.sleep(0.01)
            active["n"] -= 1
            return {"return": "0"}

        api._get = fake_get

        async def call():
            async with api._lock:
                return await fake_get("x")

        await asyncio.gather(*[call() for _ in range(5)])
        assert active["max"] == 1
