"""Test fixtures for OpenKarotz v4.

The integration package imports Home Assistant at package level, so the API
client (which has no HA imports) is loaded standalone from its file.
"""
import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).parent.parent
API_PATH = ROOT / "custom_components" / "open_karotz" / "api.py"


def _load_api_module():
    spec = importlib.util.spec_from_file_location("karotz_api", API_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["karotz_api"] = mod
    spec.loader.exec_module(mod)
    return mod


api_mod = _load_api_module()


class RespCtx:
    """Async context manager mimicking aiohttp ClientResponse."""

    def __init__(self, *, status=200, payload=None, json_data=None, headers=None):
        self.status = status
        self._payload = payload
        self._json = json_data
        self.headers = headers or {"Content-Type": "application/json"}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def json(self, content_type=None):
        if self._json is None:
            raise ValueError("no json")
        return self._json

    async def read(self):
        if self._payload is not None:
            return self._payload
        if self._json is not None:
            return json.dumps(self._json).encode()
        return b""


def make_session(responses):
    """Session mock serving `responses` (list of RespCtx or exceptions) in order."""
    session = MagicMock()
    seq = list(responses)

    def _get(*args, **kwargs):
        item = seq.pop(0) if seq else RespCtx(json_data={})
        if isinstance(item, Exception):
            raise item
        return item

    session.get = MagicMock(side_effect=_get)
    return session


@pytest.fixture
def api():
    return api_mod.OpenKarotzAPI("192.168.1.70", make_session([]))
