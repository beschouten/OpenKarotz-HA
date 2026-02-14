"""Integration tests for OpenKarotz light entity."""

import asyncio
import sys
sys.path.insert(0, '.')

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.openkarotz.light import OpenKarotzLight, PREDEFINED_COLORS
from custom_components.openkarotz.coordinator import OpenKarotzCoordinator
from custom_components.openkarotz.const import DOMAIN


@pytest.mark.asyncio
async def test_light_entity_turn_on():
    """Test light entity turn on functionality."""
    print("\n=== Testing Light Entity Turn On ===\n")

    # Create mock coordinator
    coordinator = MagicMock(spec=OpenKarotzCoordinator)
    coordinator.api = AsyncMock()
    coordinator.api.set_led = AsyncMock(return_value={"status": "ok"})

    # Mock LED state
    coordinator.leds_state = {"enabled": True, "brightness": 50, "rgb_value": "FF0000"}
    coordinator.data = {
        "info": {"id": "test_device_123"},
        "leds": {"enabled": True, "brightness": 50, "rgb_value": "FF0000"}
    }

    # Create light entity
    led_data = {"id": 1, "name": "Main LED"}
    light = OpenKarotzLight(coordinator, led_data)

    # Test turn on with brightness
    print("Test 1: Turn on with brightness=75")
    await light.async_turn_on(brightness=75)
    coordinator.api.set_led.assert_called_with(brightness=75)
    print("  SUCCESS: Brightness set to 75")

    # Reset mock
    coordinator.api.set_led.reset_mock()

    # Test turn on with color
    print("\nTest 2: Turn on with color (red)")
    await light.async_turn_on(color=(255, 0, 0))
    coordinator.api.set_led.assert_called_with(rgb_value="ff0000")
    print("  SUCCESS: Color set to red (FF0000)")

    # Reset mock
    coordinator.api.set_led.reset_mock()

    # Test turn on with color temperature
    print("\nTest 3: Turn on with color_temperature=3500")
    await light.async_turn_on(color_temperature=3500)
    coordinator.api.set_led.assert_called_with(color_temperature=3500, rgb_value=None)
    print("  SUCCESS: Color temperature set to 3500K with RGB cleared")

    # Reset mock
    coordinator.api.set_led.reset_mock()

    # Test turn on without parameters (should set brightness to 100)
    print("\nTest 4: Turn on without parameters")
    await light.async_turn_on()
    coordinator.api.set_led.assert_called_with(brightness=100)
    print("  SUCCESS: Brightness set to 100 (default)")


@pytest.mark.asyncio
async def test_light_entity_turn_off():
    """Test light entity turn off functionality."""
    print("\n=== Testing Light Entity Turn Off ===\n")

    # Create mock coordinator
    coordinator = MagicMock(spec=OpenKarotzCoordinator)
    coordinator.api = AsyncMock()
    coordinator.api.set_led = AsyncMock(return_value={"status": "ok"})

    # Mock LED state
    coordinator.leds_state = {"enabled": True, "brightness": 100, "rgb_value": "FFFFFF"}
    coordinator.data = {
        "info": {"id": "test_device_123"},
        "leds": {"enabled": True, "brightness": 100, "rgb_value": "FFFFFF"}
    }

    # Create light entity
    led_data = {"id": 1, "name": "Main LED"}
    light = OpenKarotzLight(coordinator, led_data)

    # Test turn off
    print("Test: Turn off light")
    await light.async_turn_off()
    coordinator.api.set_led.assert_called_with(brightness=0)
    print("  SUCCESS: Brightness set to 0 (off)")


@pytest.mark.asyncio
async def test_light_entity_color_change():
    """Test light entity color change functionality."""
    print("\n=== Testing Light Entity Color Change ===\n")

    # Create mock coordinator
    coordinator = MagicMock(spec=OpenKarotzCoordinator)
    coordinator.api = AsyncMock()
    coordinator.api.set_led = AsyncMock(return_value={"status": "ok"})

    # Mock LED state
    coordinator.leds_state = {"enabled": True, "brightness": 100, "rgb_value": "FFFFFF"}
    coordinator.data = {
        "info": {"id": "test_device_123"},
        "leds": {"enabled": True, "brightness": 100, "rgb_value": "FFFFFF"}
    }

    # Create light entity
    led_data = {"id": 1, "name": "Main LED"}
    light = OpenKarotzLight(coordinator, led_data)

    # Test color change using color_name
    print("Test: Change color to blue using color_name")
    await light.async_select_color("blue")
    coordinator.api.set_led.assert_called_with(rgb_value="0000ff")
    print("  SUCCESS: Color changed to blue")

    # Test color change using rgb tuple
    print("\nTest: Change color to green using rgb tuple")
    await light.async_turn_on(color=(0, 255, 0))
    coordinator.api.set_led.assert_called_with(rgb_value="00ff00")
    print("  SUCCESS: Color changed to green")


@pytest.mark.asyncio
async def test_light_entity_properties():
    """Test light entity properties."""
    print("\n=== Testing Light Entity Properties ===\n")

    # Create mock coordinator
    coordinator = MagicMock(spec=OpenKarotzCoordinator)
    coordinator.api = AsyncMock()
    coordinator.api.set_led = AsyncMock(return_value={"status": "ok"})

    # Mock LED state with RGB
    coordinator.leds_state = {"enabled": True, "brightness": 75, "rgb_value": "FF5500"}
    coordinator.data = {
        "info": {"id": "test_device_123"},
        "leds": {"enabled": True, "brightness": 75, "rgb_value": "FF5500"}
    }

    # Create light entity
    led_data = {"id": 1, "name": "Main LED"}
    light = OpenKarotzLight(coordinator, led_data)

    # Test color mode
    print("Test: Check color mode")
    assert light.color_mode == "rgb"
    print("  SUCCESS: Color mode is rgb")

    # Test color property
    print("\nTest: Check color property")
    color = light.color
    assert color == (255, 85, 0)
    print(f"  SUCCESS: Color is {color}")

    # Test brightness property
    print("\nTest: Check brightness property")
    assert light.brightness == 75
    print("  SUCCESS: Brightness is 75")


@pytest.mark.asyncio
async def test_light_entity_with_color_temperature():
    """Test light entity with color temperature."""
    print("\n=== Testing Light Entity With Color Temperature ===\n")

    # Create mock coordinator
    coordinator = MagicMock(spec=OpenKarotzCoordinator)
    coordinator.api = AsyncMock()
    coordinator.api.set_led = AsyncMock(return_value={"status": "ok"})

    # Mock LED state with color temperature
    coordinator.leds_state = {"enabled": True, "brightness": 50, "color_temperature": 3500}
    coordinator.data = {
        "info": {"id": "test_device_123"},
        "leds": {"enabled": True, "brightness": 50, "color_temperature": 3500}
    }

    # Create light entity
    led_data = {"id": 1, "name": "Main LED"}
    light = OpenKarotzLight(coordinator, led_data)

    # Test color mode
    print("Test: Check color mode with color temperature")
    assert light.color_mode == "color_temperature"
    print("  SUCCESS: Color mode is color_temperature")

    # Test color temperature property
    print("\nTest: Check color temperature property")
    assert light.color_temperature == 3500
    print("  SUCCESS: Color temperature is 3500K")

    # Test turn on with color temperature
    print("\nTest: Turn on with color_temperature=4000")
    await light.async_turn_on(color_temperature=4000)
    coordinator.api.set_led.assert_called_with(color_temperature=4000, rgb_value=None)
    print("  SUCCESS: Color temperature set to 4000K with RGB cleared")