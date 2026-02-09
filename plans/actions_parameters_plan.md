# Open Karotz Actions Parameters Plan

## Overview
This document outlines the plan to add proper parameter definitions for all Open Karotz actions so they are published at installation time in Home Assistant.

## Current State Analysis

### Actions Found
| Action | Platform | Parameters | Status |
|--------|----------|------------|--------|
| `tts` | `__init__.py` | `text` (required), `voice` (optional) | ❌ No schema |
| `play_media` | `media_player.py` | `media_type`, `media_id` | ❌ No service |
| `set_volume_level` | `media_player.py` | `volume` | ❌ No service |
| `turn_on` (LED) | `light.py` | `rgb_color` | ❌ No service |
| `turn_off` (LED) | `light.py` | None | ❌ No service |
| `set_cover_position` | `cover.py` | `position` | ❌ No service |
| `open_cover_tilt` | `cover.py` | None | ❌ No service |
| `close_cover_tilt` | `cover.py` | None | ❌ No service |
| `select_option` (Mood) | `select.py` | `option` | ❌ No service |
| `turn_on` (Sleep) | `switch.py` | None | ❌ No service |
| `turn_off` (Sleep) | `switch.py` | None | ❌ No service |
| `clear_cache` | `button.py` | None | ❌ No service |

## Plan

### Step 1: Define Service Schemas
Create a new `services.yaml` file to define all service schemas:

```yaml
tts:
  description: Play text-to-speech on Open Karotz
  fields:
    text:
      required: true
      description: Text to speak
      example: "Hello, this is a test"
      selector:
        text:
    voice:
      required: false
      description: Voice ID (1-86)
      example: "6"
      selector:
        number:
          min: 1
          max: 86
          mode: box

play_sound:
  description: Play a local sound
  fields:
    sound_id:
      required: true
      description: Sound ID from sound list
      example: "ready"
      selector:
        select:
          options:
            - "bip1"
            - "bling"
            - "flush"
            # ... all sound options

set_volume:
  description: Set media player volume
  fields:
    volume:
      required: true
      description: Volume level (0.0 - 1.0)
      example: "0.5"
      selector:
        number:
          min: 0
          max: 1
          step: 0.01
          mode: slider

set_led_color:
  description: Set LED color
  fields:
    rgb_color:
      required: true
      description: RGB color tuple
      example: "[255, 0, 0]"
      selector:
        color_rgb:

set_ear_position:
  description: Set ear position
  fields:
    position:
      required: true
      description: Position (0-100)
      example: "50"
      selector:
        number:
          min: 0
          max: 100
          mode: slider

set_mood:
  description: Set mood
  fields:
    mood_id:
      required: true
      description: Mood ID (1-301)
      example: "1"
      selector:
        number:
          min: 1
          max: 301
          mode: box

wake_up:
  description: Wake up Open Karotz
  fields: {}

sleep:
  description: Put Open Karotz to sleep
  fields: {}

clear_cache:
  description: Clear Open Karotz cache
  fields: {}
```

### Step 2: Update `__init__.py`
Modify the service registration to include proper schemas:

```python
async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Open Karotz integration."""
    from homeassistant.helpers.service import async_register_admin_service
    import yaml
    import os
    
    # Load service definitions
    services_file = os.path.join(os.path.dirname(__file__), "services.yaml")
    with open(services_file) as f:
        services = yaml.safe_load(f)
    
    # Register TTS service
    async def async_open_karotz_tts_service(service_call):
        """Handle TTS service call."""
        text = service_call.data.get("text", "")
        voice = service_call.data.get("voice", "6")
        
        if not text:
            raise HomeAssistantError("Text is required")
        
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")
        
        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)
        
        if not api:
            raise HomeAssistantError("Open Karotz not initialized")
        
        try:
            import urllib.parse
            encoded_text = urllib.parse.quote(text)
            await api.play_tts(encoded_text, voice)
        except Exception as err:
            raise HomeAssistantError(f"Failed to play TTS: {err}")
    
    async_register_admin_service(
        hass, DOMAIN, "tts", async_open_karotz_tts_service,
        schema=services["tts"]
    )
    
    return True
```

### Step 3: Create Platform-Specific Services
For each platform, create service definitions that can be called directly:

```python
# In media_player.py
async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Open Karotz media player entities."""
    host = entry.data[CONF_HOST]
    entity = OpenKarotzMediaPlayer(host, entry.entry_id)
    async_add_entities([entity])
    
    # Register platform services
    platform = entity.platform
    platform.async_register_entity_service(
        "play_sound",
        {
            vol.Required("sound_id"): vol.In(SOUND_LIST),
        },
        "async_play_local_sound",
    )
```

### Step 4: Update Translations
Add service descriptions to `translations/en.json`:

```json
{
  "services": {
    "tts": {
      "name": "Text-to-Speech",
      "description": "Play text-to-speech on Open Karotz",
      "fields": {
        "text": {
          "name": "Text",
          "description": "Text to speak"
        },
        "voice": {
          "name": "Voice",
          "description": "Voice ID (1-86)"
        }
      }
    },
    "play_sound": {
      "name": "Play Sound",
      "description": "Play a local sound",
      "fields": {
        "sound_id": {
          "name": "Sound ID",
          "description": "Sound to play"
        }
      }
    }
  }
}
```

## Implementation Order

1. **Create `services.yaml`** with all service definitions
2. **Update `__init__.py`** to load and register services with schemas
3. **Update platform files** to register entity services where applicable
4. **Update translations** with service descriptions
5. **Test** all services in Home Assistant
6. **Update documentation** with new service parameters

## Expected Outcome

After implementation:
- All actions will have proper parameter definitions
- Parameters will be visible in Home Assistant UI at installation time
- Service calls will validate parameters before execution
- Users will see helpful descriptions and examples for each parameter
- The integration will follow Home Assistant best practices for service definitions