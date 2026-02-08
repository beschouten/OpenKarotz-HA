"""Test fixtures for Open Karotz."""
import pytest


@pytest.fixture(autouse=True)
def auto_enable_bypass():
    """Enable bypass for all tests."""
    pass