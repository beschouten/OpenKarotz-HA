"""Test script to change Karotz LED colors."""

import asyncio
import sys
sys.path.insert(0, '.')

from custom_components.openkarotz.api import OpenKarotzAPI


async def main():
    """Test changing Karotz LED colors."""
    karotz_host = "192.168.1.70"
    
    print(f"Connecting to Karotz at {karotz_host}...")
    
    api = OpenKarotzAPI(host=karotz_host)
    
    try:
        connected = await api.async_connect()
        if not connected:
            print("Failed to connect to Karotz device")
            return
        
        print("Connected successfully!")
        
        # Get device info
        print("\nGetting device info...")
        info = await api.get_info()
        print(f"Device Info: {info}")
        
        # Get current LED state
        print("\nCurrent LED state:")
        leds = await api.get_leds()
        print(f"  LED State: {leds}")
        
        # Change LED to red
        print("\n=== Changing LED to RED ===")
        try:
            result = await api.set_led(rgb_value="FF0000", brightness=100)
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Verify red
        print("\nVerifying RED LED:")
        leds = await api.get_leds()
        print(f"  LED State: {leds}")
        
        # Wait 10 seconds
        print("\nWaiting 10 seconds...")
        await asyncio.sleep(10)
        
        # Change LED to green
        print("\n=== Changing LED to GREEN ===")
        try:
            result = await api.set_led(rgb_value="00FF00", brightness=100)
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Verify green
        print("\nVerifying GREEN LED:")
        leds = await api.get_leds()
        print(f"  LED State: {leds}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await api.async_disconnect()
        print("\nDisconnected from Karotz")


if __name__ == "__main__":
    asyncio.run(main())