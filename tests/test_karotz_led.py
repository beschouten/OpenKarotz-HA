"""Test LED change on actual Karotz device."""

import asyncio
import sys
sys.path.insert(0, '.')

from custom_components.openkarotz.api import OpenKarotzAPI


async def test_led_green():
    """Test changing LED to green."""
    print("Testing LED change to green on Karotz device...")
    
    api = OpenKarotzAPI('192.168.1.70')
    
    try:
        connected = await api.async_connect()
        if not connected:
            print("Failed to connect to Karotz device")
            return
        
        print("Connected to Karotz device")
        
        # Set LED to green
        print("Setting LED to green (00FF00)...")
        result = await api.set_led(rgb_value='00FF00')
        print(f"LED set result: {result}")
        
        # Get LED state to verify
        print("Getting LED state...")
        leds = await api.get_leds()
        print(f"LED state: {leds}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await api.async_disconnect()
        print("Disconnected from Karotz device")


if __name__ == "__main__":
    asyncio.run(test_led_green())