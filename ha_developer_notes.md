# Home Assistant Developer Notes for Open Karotz Integration

This document provides comprehensive notes on Home Assistant integration best practices, specifically tailored for the Open Karotz integration. It covers service registration, entity patterns, response handling, and internationalization.

## Table of Contents

1. [Service Action Registration Best Practices](#service-action-registration-best-practices)
2. [Service Action Description Format (services.yaml)](#service-action-description-format-servicesyaml)
3. [Entity Service Actions Pattern](#entity-service-actions-pattern)
4. [Response Data Handling](#response-data-handling)
5. [Icons Configuration](#icons-configuration)
6. [Field Grouping and Filtering](#field-grouping-and-filtering)
7. [Translation Requirements](#translation-requirements)
8. [Sample Code Patterns for Open Karotz](#sample-code-patterns-for-open-karotz)

---

## Service Action Registration Best Practices

### Register Services in `async_setup`, Not `async_setup_entry`

Services should be registered in the [`async_setup()`](custom_components/open_karotz/__init__.py:48) function, not in [`async_setup_entry()`](custom_components/open_karotz/__init__.py:33). This ensures services are available even before any config entries are loaded.

**Why `async_setup`?**
- Services are global to the integration, not tied to a specific device
- Services should be available immediately when the integration loads
- `async_setup_entry` is called for each device/config entry, which would duplicate service registration

**Example from Open Karotz:**
```python
async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Open Karotz integration."""
    # Load services.yaml using async executor to avoid blocking
    services_path = hass.config.path("custom_components/open_karotz/services.yaml")
    services_config = await hass.async_add_executor_job(
        lambda: yaml.safe_load(open(services_path, "r", encoding="utf-8"))
    )
    
    # Register service handlers
    async def async_open_karotz_tts_service(service_call: ServiceCall) -> None:
        """Handle TTS service call."""
        # ... service logic ...
    
    # Register services with schemas from services.yaml
    if services_config:
        for service_name, service_config in services_config.items():
            # Build voluptuous schema from fields
            fields = service_config.get("fields", {})
            schema = {}
            for field_name, field_config in fields.items():
                required = field_config.get("required", False)
                if required:
                    schema[vol.Required(field_name)] = str
                else:
                    schema[vol.Optional(field_name)] = str
            
            service_schema = vol.Schema(schema)
            
            # Register each service
            if service_name == "tts":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_tts_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
```

### Use `async_register_admin_service` for Admin Services

For services that control devices (like TTS, LED, ear position), use [`async_register_admin_service()`](custom_components/open_karotz/__init__.py:277). This registers services in the admin panel and makes them available to automations.

**Key Points:**
- Admin services require authentication
- Services appear in Developer Tools > Services
- Services can be called from automations and scripts

### Service Registration Pattern

```python
from homeassistant.helpers.service import async_register_admin_service
import voluptuous as vol

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    # ... load services.yaml ...
    
    async def service_handler(service_call: ServiceCall) -> None:
        """Handle service call."""
        # Access service data
        text = service_call.data.get("text", "")
        voice = service_call.data.get("voice", "6")
        
        # Get API instance
        entries = hass.config_entries.async_entries(DOMAIN)
        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)
        
        # Execute service logic
        await api.play_tts(text, voice)
    
    # Register service
    async_register_admin_service(
        hass,
        DOMAIN,
        "tts",
        service_handler,
        schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
    )
```

---

## Service Action Description Format (services.yaml)

The [`services.yaml`](custom_components/open_karotz/services.yaml) file defines service metadata including names, descriptions, and field specifications.

### Basic Structure

```yaml
service_name:
  name: Service Name
  description: Service description
  fields:
    field_name:
      name: Field Name
      description: Field description
      required: true/false
      example: Example value
      selector:
        selector_type:
          # selector-specific options
```

### Open Karotz Service Examples

#### TTS Service with Optional Voice Parameter

```yaml
tts:
  name: Text-to-Speech
  description: Speak text using the Karotz TTS engine.
  fields:
    text:
      name: Text
      description: The text to speak.
      required: true
      example: "Hello, this is Karotz speaking."
      selector:
        text:
    voice:
      name: Voice
      description: The voice ID to use (1-86). See TTS_VOICES in const.py for available voices.
      required: false
      example: "5"
      selector:
        number:
          min: 1
          max: 86
          mode: box
```

#### Play Sound Service with Select Selector

```yaml
play_sound:
  name: Play Sound
  description: Play a sound from the Karotz sound library.
  fields:
    sound_id:
      name: Sound ID
      description: The sound ID to play. See SOUND_LIST in const.py for available sounds.
      required: true
      example: "bip1"
      selector:
        select:
          options:
            - "bip1"
            - "bling"
            - "flush"
            - "install_ok"
            - "jet1"
            - "laser_15"
            - "merde"
            - "ready"
            - "rfid_error"
            - "rfid_ok"
            - "saut1"
            - "start"
            - "twang_01"
            - "twang_04"
```

#### Set Volume Service with Number Slider

```yaml
set_volume:
  name: Set Volume
  description: Set the Karotz volume level.
  fields:
    volume:
      name: Volume
      description: Volume level from 0.0 (mute) to 1.0 (maximum).
      required: true
      example: "0.5"
      selector:
        number:
          min: 0.0
          max: 1.0
          step: 0.01
          mode: slider
```

#### Set LED Color Service with RGB Input

```yaml
set_led_color:
  name: Set LED Color
  description: Set the Karotz LED color using RGB values.
  fields:
    rgb_color:
      name: RGB Color
      description: The RGB color value as a list [red, green, blue] with values 0-255.
      required: true
      example: "[255, 0, 0]"
      selector:
        text:
```

#### Set Ear Position Service with Number Input

```yaml
set_ear_position:
  name: Set Ear Position
  description: Set the Karotz ear position.
  fields:
    position:
      name: Position
      description: "Ear position from 0 to 100. Standard values: 0 down, 8 horizontal, 16 up."
      required: true
      example: "8"
      selector:
        number:
          min: 0
          max: 100
          mode: box
```

#### Set Mood Service with Number Input

```yaml
set_mood:
  name: Set Mood
  description: Set the Karotz mood.
  fields:
    mood_id:
      name: Mood ID
      description: The mood ID to set (1-301). See MOOD_IDS in const.py for available moods.
      required: true
      example: "1"
      selector:
        number:
          min: 1
          max: 301
          mode: box
```

### Simple Services (No Parameters)

```yaml
wake_up:
  name: Wake Up
  description: Wake up the Karotz from sleep mode.

sleep:
  name: Sleep
  description: Put the Karotz to sleep mode.

clear_cache:
  name: Clear Cache
  description: Clear the Karotz cache.
```

---

## Entity Service Actions Pattern

Entity services allow entities to expose platform-specific actions that can be called from automations.

### Registering Entity Services

Entity services are registered in the entity's `async_added_to_hass()` method using `self._register_entity_service()`.

**Example: Adding entity services to Open Karotz entities**

```python
from homeassistant.core import ServiceCall
from homeassistant.helpers.service import async_register_entity_service

class OpenKarotzMediaPlayer(MediaPlayerEntity):
    """Representation of the Open Karotz media player."""
    
    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "play_local_sound",
            {
                "required": [vol.Required("sound_id")],
                "optional": [],
            },
            "async_play_local_sound",
        )
        
        self._register_entity_service(
            "play_tts",
            {
                "required": [vol.Required("text")],
                "optional": [vol.Optional("voice", default="6")],
            },
            "async_play_tts",
        )
    
    async def async_play_local_sound(self, sound_id: str) -> None:
        """Play a local sound from the library."""
        await self._async_play_local(sound_id)
    
    async def async_play_tts(self, text: str, voice: str = "6") -> None:
        """Play text-to-speech."""
        await self._async_tts(text, voice)
```

### Entity Service Decorator Pattern

For simpler entity services, use the `@entity_service` decorator:

```python
from homeassistant.helpers.entity import entity_service

class OpenKarotzMediaPlayer(MediaPlayerEntity):
    """Representation of the Open Karotz media player."""
    
    @entity_service(
        vol.Schema({
            vol.Required("sound_id"): str,
        })
    )
    async def async_play_local_sound(self, sound_id: str) -> None:
        """Play a local sound from the library."""
        await self._async_play_local(sound_id)
```

### Entity Service Schema Options

```python
# Required field only
vol.Schema({vol.Required("sound_id"): str})

# Required and optional fields
vol.Schema({
    vol.Required("text"): str,
    vol.Optional("voice", default="6"): str,
})

# Multiple optional fields with defaults
vol.Schema({
    vol.Required("text"): str,
    vol.Optional("voice", default="6"): str,
    vol.Optional("volume", default=0.5): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
})
```

---

## Response Data Handling

Service responses can be used to return data to automations.

### Returning Data from Services

To return data from a service, raise a `ServiceResponse` exception with the response data:

```python
from homeassistant.exceptions import ServiceResponse

async def async_open_karotz_get_status_service(service_call: ServiceCall) -> None:
    """Handle get_status service call."""
    entries = hass.config_entries.async_entries(DOMAIN)
    api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
    if api is None:
        api = hass.data[DOMAIN].get(entries[0].entry_id)
    
    # Get status data
    status = await api.get_status()
    
    # Return data to automation
    raise ServiceResponse({
        "status": status,
        "timestamp": datetime.now().isoformat(),
    })
```

### Service Response in services.yaml

```yaml
get_status:
  name: Get Status
  description: Get the current status of Open Karotz.
  fields: {}
```

### Using Service Response in Automations

```yaml
automation:
  - alias: Check Karotz Status
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: open_karotz.get_status
        target:
          entity_id: all
        response_variable: status_response
      - service: notify.mobile_app
        data:
          message: "Karotz status: {{ status_response.status }}"
```

---

## Icons Configuration

Icons are defined in [`icons.json`](custom_components/open_karotz/icons.json) to provide consistent iconography across the integration.

### Basic Icons Structure

```json
{
  "entity": {
    "platform_name": {
      "entity_id": {
        "default": "mdi:icon-name"
      }
    }
  }
}
```

### Open Karotz Icons Configuration

```json
{
  "entity": {
    "sensor": {
      "karotz_storage": {
        "default": "mdi:memory"
      },
      "usb_storage": {
        "default": "mdi:usb"
      }
    },
    "light": {
      "led": {
        "default": "mdi:lightbulb"
      }
    },
    "cover": {
      "ears": {
        "default": "mdi:arrow-up-down-bold"
      }
    },
    "media_player": {
      "media_player": {
        "default": "mdi:speaker"
      }
    },
    "select": {
      "mood": {
        "default": "mdi:emoticon"
      }
    },
    "camera": {
      "camera": {
        "default": "mdi:camera"
      }
    },
    "switch": {
      "sleep": {
        "default": "mdi:power-sleep"
      }
    },
    "binary_sensor": {
      "rfid": {
        "default": "mdi:nfc"
      }
    },
    "button": {
      "clear_cache": {
        "default": "mdi:trash-can"
      }
    }
  }
}
```

### Icon Naming Conventions

| Entity Type | Icon Suggestion | Example |
|-------------|-----------------|---------|
| Sensor | `mdi:memory`, `mdi:usb`, `mdi:water` | Storage sensors |
| Light | `mdi:lightbulb`, `mdi:led` | LED control |
| Cover | `mdi:arrow-up-down-bold`, `mdi:window-open` | Ear position |
| Media Player | `mdi:speaker`, `mdi:play` | Audio playback |
| Select | `mdi:emoticon`, `mdi:palette` | Mood selection |
| Camera | `mdi:camera`, `mdi:video` | Snapshot capture |
| Switch | `mdi:power`, `mdi:toggle-switch` | System controls |
| Binary Sensor | `mdi:nfc`, `mdi:door` | RFID detection |
| Button | `mdi:trash-can`, `mdi:refresh` | Action buttons |

### Dynamic Icons Based on State

Icons can be dynamically changed based on entity state using the `icon` property:

```python
class OpenKarotzLed(LightEntity):
    """Representation of the Open Karotz LED."""
    
    @property
    def icon(self) -> str:
        """Return the icon based on state."""
        if self.is_on:
            return "mdi:lightbulb-on"
        return "mdi:lightbulb-off"
```

---

## Field Grouping and Filtering

### Field Grouping in services.yaml

Fields can be grouped using the `group` property for better organization:

```yaml
set_led_color:
  name: Set LED Color
  description: Set the Karotz LED color using RGB values.
  fields:
    color_group:
      name: Color Settings
      fields:
        rgb_color:
          name: RGB Color
          description: The RGB color value as a list [red, green, blue] with values 0-255.
          required: true
          example: "[255, 0, 0]"
          selector:
            text:
        fade_time:
          name: Fade Time
          description: Time in milliseconds to fade to the new color.
          required: false
          example: "500"
          selector:
            number:
              min: 0
              max: 5000
              mode: box
```

### Field Filtering

Use `filter` to restrict field values based on other fields:

```yaml
play_tts:
  name: Play TTS
  description: Play text-to-speech with voice selection.
  fields:
    text:
      name: Text
      description: The text to speak.
      required: true
      selector:
        text:
    language:
      name: Language
      description: The language to use.
      required: true
      selector:
        select:
          options:
            - "en"
            - "fr"
            - "de"
            - "es"
    voice:
      name: Voice
      description: The voice ID to use.
      required: true
      selector:
        select:
          options: []
      filter:
        field: language
        mapping:
          "en":
            - "5"  # English (US) Male
            - "6"  # English (US) Female
            - "7"  # English (UK) Male
            - "8"  # English (UK) Female
          "fr":
            - "1"  # French Male
            - "2"  # French Female
            - "3"  # Canadian French Male
            - "4"  # Canadian French Female
```

### Conditional Fields

Use `enable_if` to show fields conditionally:

```yaml
play_media:
  name: Play Media
  description: Play media from URL or local library.
  fields:
    media_type:
      name: Media Type
      description: Type of media to play.
      required: true
      selector:
        select:
          options:
            - "local"
            - "url"
    sound_id:
      name: Sound ID
      description: Local sound to play.
      required: true
      enable_if:
        field: media_type
        value: "local"
      selector:
        select:
          options:
            - "bip1"
            - "bling"
            - "flush"
    url:
      name: URL
      description: URL of media to play.
      required: true
      enable_if:
        field: media_type
        value: "url"
      selector:
        text:
```

---

## Translation Requirements

### Translation File Structure

Translations are defined in [`translations/en.json`](custom_components/open_karotz/translations/en.json) with the following structure:

```json
{
  "config": {
    "step": {
      "user": {
        "data": {
          "host": "Host (IP address)",
          "name": "Name"
        }
      }
    }
  },
  "error": {
    "invalid_host": "Invalid host",
    "unknown": "Unknown error"
  },
  "entities": {
    "platform_name": {
      "entity_id": {
        "name": "Entity Name"
      }
    }
  },
  "services": {
    "service_name": {
      "name": "Service Name",
      "description": "Service description",
      "fields": {
        "field_name": {
          "name": "Field Name",
          "description": "Field description"
        }
      }
    }
  }
}
```

### Open Karotz Translation Examples

#### Service Translations

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
      "description": "Play a local sound from the library",
      "fields": {
        "sound_id": {
          "name": "Sound ID",
          "description": "Sound to play from the library"
        }
      }
    },
    "set_volume": {
      "name": "Set Volume",
      "description": "Set the volume level for media playback",
      "fields": {
        "volume": {
          "name": "Volume",
          "description": "Volume level (0.0 to 1.0)"
        }
      }
    },
    "set_led_color": {
      "name": "Set LED Color",
      "description": "Set the LED color",
      "fields": {
        "rgb_color": {
          "name": "RGB Color",
          "description": "RGB color values (0-255 for each channel)"
        }
      }
    },
    "set_ear_position": {
      "name": "Set Ear Position",
      "description": "Set the ear position",
      "fields": {
        "position": {
          "name": "Position",
          "description": "Position percentage (0-100)"
        }
      }
    },
    "set_mood": {
      "name": "Set Mood",
      "description": "Set the mood",
      "fields": {
        "mood_id": {
          "name": "Mood ID",
          "description": "Mood ID (1-301)"
        }
      }
    },
    "wake_up": {
      "name": "Wake Up",
      "description": "Wake up Open Karotz from sleep mode"
    },
    "sleep": {
      "name": "Sleep",
      "description": "Put Open Karotz to sleep mode"
    },
    "clear_cache": {
      "name": "Clear Cache",
      "description": "Clear the Open Karotz cache"
    }
  }
}
```

#### Entity Translations

```json
{
  "entities": {
    "sensor": {
      "karotz_storage": {"name": "Karotz Storage"},
      "usb_storage": {"name": "USB Storage"}
    },
    "light": {
      "led": {"name": "Open Karotz LED"}
    },
    "cover": {
      "ears": {"name": "Open Karotz Ears"}
    },
    "media_player": {
      "media_player": {"name": "Open Karotz"}
    },
    "select": {
      "mood": {"name": "Open Karotz Mood"}
    },
    "camera": {
      "camera": {"name": "Open Karotz Camera"}
    },
    "switch": {
      "sleep": {"name": "Open Karotz Sleep"}
    },
    "binary_sensor": {
      "rfid": {"name": "Open Karotz RFID"}
    },
    "button": {
      "clear_cache": {"name": "Clear Cache"}
    }
  }
}
```

### Translation Best Practices

1. **Use Translation Keys**: Always use translation keys in entities instead of hardcoded names:
   ```python
   class OpenKarotzLed(LightEntity):
       _attr_translation_key = "led"
   ```

2. **Service Names**: Service names in `services.yaml` should match translation keys:
   ```yaml
   tts:
     name: Text-to-Speech
   ```

3. **Consistent Naming**: Use consistent naming conventions:
   - Entity names: "Open Karotz [Feature]"
   - Service names: "[Action] [Feature]"
   - Field names: Descriptive, lowercase with underscores

4. **Description Clarity**: Service descriptions should clearly explain what the service does:
   - Start with a verb: "Play", "Set", "Get", "Wake up"
   - Include context: "on Open Karotz", "from the library"
   - Specify ranges: "(0.0 to 1.0)", "(1-86)"

5. **Field Descriptions**: Field descriptions should explain:
   - What the field accepts
   - Valid ranges or options
   - Examples of valid values

---

## Sample Code Patterns for Open Karotz

### Complete Service Registration Pattern

```python
"""Open Karotz Home Assistant Integration."""
from __future__ import annotations

import asyncio
import logging
import yaml

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.service import async_register_admin_service
import voluptuous as vol

from .const import DOMAIN
from .api import OpenKarotzAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.LIGHT,
    Platform.COVER,
    Platform.MEDIA_PLAYER,
    Platform.SELECT,
    Platform.CAMERA,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Open Karotz integration."""
    # Load services.yaml using async executor to avoid blocking
    services_path = hass.config.path("custom_components/open_karotz/services.yaml")
    try:
        services_config = await hass.async_add_executor_job(
            lambda: yaml.safe_load(open(services_path, "r", encoding="utf-8"))
        )
    except FileNotFoundError:
        _LOGGER.error("services.yaml not found at %s", services_path)
        return False
    except yaml.YAMLError as err:
        _LOGGER.error("Error parsing services.yaml: %s", err)
        return False

    # Service handlers
    async def async_open_karotz_tts_service(service_call: ServiceCall) -> None:
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

    async def async_open_karotz_play_sound_service(service_call: ServiceCall) -> None:
        """Handle play_sound service call."""
        sound_id = service_call.data.get("sound_id")

        if not sound_id:
            raise HomeAssistantError("sound_id is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.play_sound(sound_id)
        except Exception as err:
            raise HomeAssistantError(f"Failed to play sound: {err}")

    async def async_open_karotz_set_volume_service(service_call: ServiceCall) -> None:
        """Handle set_volume service call."""
        volume = service_call.data.get("volume")

        if volume is None:
            raise HomeAssistantError("volume is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.set_volume(volume)
        except Exception as err:
            raise HomeAssistantError(f"Failed to set volume: {err}")

    async def async_open_karotz_set_led_color_service(service_call: ServiceCall) -> None:
        """Handle set_led_color service call."""
        rgb_color = service_call.data.get("rgb_color")

        if rgb_color is None:
            raise HomeAssistantError("rgb_color is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.set_led_color(rgb_color)
        except Exception as err:
            raise HomeAssistantError(f"Failed to set LED color: {err}")

    async def async_open_karotz_set_ear_position_service(service_call: ServiceCall) -> None:
        """Handle set_ear_position service call."""
        position = service_call.data.get("position")

        if position is None:
            raise HomeAssistantError("position is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.set_ear_position_single(position)
        except Exception as err:
            raise HomeAssistantError(f"Failed to set ear position: {err}")

    async def async_open_karotz_set_mood_service(service_call: ServiceCall) -> None:
        """Handle set_mood service call."""
        mood_id = service_call.data.get("mood_id")

        if mood_id is None:
            raise HomeAssistantError("mood_id is required")

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.set_mood(mood_id)
        except Exception as err:
            raise HomeAssistantError(f"Failed to set mood: {err}")

    async def async_open_karotz_wake_up_service(service_call: ServiceCall) -> None:
        """Handle wake_up service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.wake_up()
        except Exception as err:
            raise HomeAssistantError(f"Failed to wake up: {err}")

    async def async_open_karotz_sleep_service(service_call: ServiceCall) -> None:
        """Handle sleep service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.sleep()
        except Exception as err:
            raise HomeAssistantError(f"Failed to put to sleep: {err}")

    async def async_open_karotz_clear_cache_service(service_call: ServiceCall) -> None:
        """Handle clear_cache service call."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Open Karotz devices configured")

        api = entries[0].runtime_data if hasattr(entries[0], "runtime_data") else None
        if api is None:
            api = hass.data[DOMAIN].get(entries[0].entry_id)

        if not api:
            raise HomeAssistantError("Open Karotz not initialized")

        try:
            await api.clear_cache()
        except Exception as err:
            raise HomeAssistantError(f"Failed to clear cache: {err}")

    # Register all services with schemas from services.yaml
    if services_config:
        for service_name, service_config in services_config.items():
            # Build voluptuous schema from fields
            fields = service_config.get("fields", {})
            schema = {}
            for field_name, field_config in fields.items():
                required = field_config.get("required", False)
                if required:
                    schema[vol.Required(field_name)] = str
                else:
                    schema[vol.Optional(field_name)] = str
            
            # Create voluptuous schema
            service_schema = vol.Schema(schema)
            
            if service_name == "tts":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_tts_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "play_sound":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_play_sound_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "set_volume":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_set_volume_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "set_led_color":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_set_led_color_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "set_ear_position":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_set_ear_position_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "set_mood":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_set_mood_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "wake_up":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_wake_up_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "sleep":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_sleep_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )
            elif service_name == "clear_cache":
                async_register_admin_service(
                    hass,
                    DOMAIN,
                    service_name,
                    async_open_karotz_clear_cache_service,
                    schema=vol.Schema({}, extra=vol.ALLOW_EXTRA),
                )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Open Karotz from a config entry."""
    host = entry.data["host"]

    api = OpenKarotzAPI(host)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
```

### Entity Service Pattern

```python
"""Light platform for Open Karotz LED control."""
from __future__ import annotations

import logging

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.service import async_register_entity_service
import voluptuous as vol

from .const import BASE_URL, DOMAIN, LED_COLORS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz light entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzLed(host, entry.entry_id)])


class OpenKarotzLed(LightEntity):
    """Representation of the Open Karotz LED."""

    _attr_name = "Open Karotz LED"
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_translation_key = "led"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the LED."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_led"
        self._attr_is_on = False
        self._rgb_color = (0, 0, 0)

    async def _async_send_command(self, color: str) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/leds?color={color}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to set LED color: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    async def async_update(self) -> None:
        """Update the entity status."""
        if self._rgb_color != (0, 0, 0):
            self._attr_is_on = True
        else:
            self._attr_is_on = False

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the color variable."""
        return self._rgb_color

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the LED."""
        rgb = kwargs.get("rgb_color", self._rgb_color)
        self._rgb_color = rgb
        self._attr_is_on = True

        hex_color = f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
        await self._async_send_command(hex_color)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the LED."""
        self._rgb_color = (0, 0, 0)
        self._attr_is_on = False
        await self._async_send_command("000000")

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "set_color_with_fade",
            {
                "required": [vol.Required("rgb_color")],
                "optional": [vol.Optional("fade_time", default=500)],
            },
            "async_set_color_with_fade",
        )
        
        self._register_entity_service(
            "blink",
            {
                "required": [vol.Required("rgb_color")],
                "optional": [
                    vol.Optional("count", default=3),
                    vol.Optional("delay", default=0.5),
                ],
            },
            "async_blink",
        )
    
    async def async_set_color_with_fade(self, rgb_color: tuple[int, int, int], fade_time: int = 500) -> None:
        """Set LED color with fade effect."""
        # Implementation would add fade logic here
        self._rgb_color = rgb_color
        hex_color = f"{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}"
        await self._async_send_command(hex_color)
    
    async def async_blink(self, rgb_color: tuple[int, int, int], count: int = 3, delay: float = 0.5) -> None:
        """Blink the LED with specified color."""
        import asyncio
        
        original_color = self._rgb_color
        
        for _ in range(count):
            self._rgb_color = rgb_color
            hex_color = f"{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}"
            await self._async_send_command(hex_color)
            await asyncio.sleep(delay)
            await self.async_turn_off()
            await asyncio.sleep(delay)
        
        # Restore original color
        self._rgb_color = original_color
        if original_color != (0, 0, 0):
            hex_color = f"{original_color[0]:02X}{original_color[1]:02X}{original_color[2]:02X}"
            await self._async_send_command(hex_color)
```

### Media Player Entity Service Pattern

```python
"""Media player platform for Open Karotz."""
from __future__ import annotations

import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.service import async_register_entity_service
import voluptuous as vol

from .const import BASE_URL, DOMAIN, SOUND_LIST

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz media player entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzMediaPlayer(host, entry.entry_id)])


class OpenKarotzMediaPlayer(MediaPlayerEntity):
    """Representation of the Open Karotz media player."""

    _attr_name = "Open Karotz"
    _attr_media_content_type = MediaType.MUSIC
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY_MEDIA
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.VOLUME_SET
    )
    _attr_translation_key = "media_player"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the media player."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_media_player"
        self._state = MediaPlayerState.IDLE
        self._volume = 0.5
        self._title = None
        self._source = None

    async def _async_send_command(self, endpoint: str) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}{endpoint}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to send command: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    async def _async_play_local(self, sound_id: str) -> bool:
        """Play local sound."""
        return await self._async_send_command(f"/cgi-bin/sound?id={sound_id}")

    async def _async_play_url(self, url: str) -> bool:
        """Play sound from URL."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/sound?url={url}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to play URL: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error playing URL: %s", err)
            return False

    async def _async_tts(self, text: str, voice: str = "1") -> bool:
        """Play text-to-speech."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/tts?text={text}&voice={voice}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to play TTS: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error playing TTS: %s", err)
            return False

    async def _async_stop(self) -> bool:
        """Stop playback."""
        return await self._async_send_command("/cgi-bin/stop")

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the media player."""
        return self._state

    @property
    def volume_level(self) -> float | None:
        """Return the volume level."""
        return self._volume

    @property
    def media_title(self) -> str | None:
        """Return the media title."""
        return self._title

    async def async_update(self) -> None:
        """Update the entity status."""
        pass

    async def async_media_play(self) -> None:
        """Play media."""
        self._state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

    async def async_media_stop(self) -> None:
        """Stop media."""
        await self._async_stop()
        self._state = MediaPlayerState.IDLE
        self.async_write_ha_state()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level."""
        self._volume = volume

    async def async_play_media(
        self, media_type: str | None, media_id: str | None, **kwargs
    ) -> None:
        """Play media."""
        if media_type == MediaType.MUSIC and media_id:
            if media_id in SOUND_LIST:
                await self._async_play_local(media_id)
                self._title = f"Sound {media_id}"
                self._state = MediaPlayerState.PLAYING
                self.async_write_ha_state()
            else:
                _LOGGER.warning("Invalid sound ID: %s", media_id)

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        self._source = source

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "play_local_sound",
            {
                "required": [vol.Required("sound_id")],
            },
            "async_play_local_sound",
        )
        
        self._register_entity_service(
            "play_tts",
            {
                "required": [vol.Required("text")],
                "optional": [vol.Optional("voice", default="6")],
            },
            "async_play_tts",
        )
        
        self._register_entity_service(
            "play_url",
            {
                "required": [vol.Required("url")],
            },
            "async_play_url",
        )
    
    async def async_play_local_sound(self, sound_id: str) -> None:
        """Play a local sound from the library."""
        if sound_id in SOUND_LIST:
            await self._async_play_local(sound_id)
            self._title = f"Sound {sound_id}"
            self._state = MediaPlayerState.PLAYING
            self.async_write_ha_state()
        else:
            _LOGGER.warning("Invalid sound ID: %s", sound_id)
    
    async def async_play_tts(self, text: str, voice: str = "6") -> None:
        """Play text-to-speech."""
        from urllib.parse import quote
        encoded_text = quote(text)
        await self._async_tts(encoded_text, voice)
        self._title = f"TTS: {text}"
        self._state = MediaPlayerState.PLAYING
        self.async_write_ha_state()
    
    async def async_play_url(self, url: str) -> None:
        """Play sound from URL."""
        await self._async_play_url(url)
        self._title = f"URL: {url}"
        self._state = MediaPlayerState.PLAYING
        self.async_write_ha_state()
```

### Cover Entity Service Pattern

```python
"""Cover platform for Open Karotz ear control."""
from __future__ import annotations

import logging

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.service import async_register_entity_service
import voluptuous as vol

from .const import BASE_URL, DOMAIN, EAR_DOWN, EAR_HORIZONTAL, EAR_MAX, EAR_MIN, EAR_UP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz cover entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzEars(host, entry.entry_id)])


class OpenKarotzEars(CoverEntity):
    """Representation of the Open Karotz ears."""

    _attr_name = "Open Karotz Ears"
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
    )
    _attr_translation_key = "ears"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the ears."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_ears"
        self._left_position = EAR_HORIZONTAL
        self._right_position = EAR_HORIZONTAL

    async def _async_send_command(self, left: int, right: int) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/ears?left={left}&right={right}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to set ear position: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    async def _async_send_reset(self) -> bool:
        """Send reset command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/ears_reset") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to reset ears: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    async def _async_send_random(self) -> bool:
        """Send random command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/ears_random") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to set random ear position: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        return False

    @property
    def current_cover_position(self) -> int | None:
        """Return the current position of the cover."""
        return int((self._left_position + self._right_position) / 2)

    async def async_open_cover(self, **kwargs) -> None:
        """Open the ears (up)."""
        self._left_position = EAR_UP
        self._right_position = EAR_UP
        await self._async_send_command(EAR_UP, EAR_UP)

    async def async_close_cover(self, **kwargs) -> None:
        """Close the ears (down)."""
        self._left_position = EAR_DOWN
        self._right_position = EAR_DOWN
        await self._async_send_command(EAR_DOWN, EAR_DOWN)

    async def async_set_cover_position(self, **kwargs) -> None:
        """Set the cover position."""
        position = kwargs.get("position", 50)
        left = int(position * EAR_MAX / 100)
        right = int(position * EAR_MAX / 100)
        self._left_position = left
        self._right_position = right
        await self._async_send_command(left, right)

    async def async_stop_cover(self, **kwargs) -> None:
        """Stop the cover."""
        pass

    async def async_open_cover_tilt(self, **kwargs) -> None:
        """Open the tilt."""
        self._left_position = EAR_UP
        self._right_position = EAR_DOWN
        await self._async_send_command(EAR_UP, EAR_DOWN)

    async def async_close_cover_tilt(self, **kwargs) -> None:
        """Close the tilt."""
        self._left_position = EAR_DOWN
        self._right_position = EAR_UP
        await self._async_send_command(EAR_DOWN, EAR_UP)

    async def async_stop_cover_tilt(self, **kwargs) -> None:
        """Stop the tilt."""
        pass

    async def async_reset_ears(self, **kwargs) -> None:
        """Reset the ears to default position."""
        self._left_position = EAR_HORIZONTAL
        self._right_position = EAR_HORIZONTAL
        await self._async_send_reset()

    async def async_random_ears(self, **kwargs) -> None:
        """Set ears to random position."""
        await self._async_send_random()

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "set_ear_positions",
            {
                "required": [vol.Required("left"), vol.Required("right")],
            },
            "async_set_ear_positions",
        )
        
        self._register_entity_service(
            "set_ear_position",
            {
                "required": [vol.Required("position")],
            },
            "async_set_ear_position",
        )
    
    async def async_set_ear_positions(self, left: int, right: int) -> None:
        """Set left and right ear positions separately."""
        self._left_position = left
        self._right_position = right
        await self._async_send_command(left, right)
    
    async def async_set_ear_position(self, position: int) -> None:
        """Set both ears to the same position."""
        self._left_position = position
        self._right_position = position
        await self._async_send_command(position, position)
```

### Select Entity Service Pattern

```python
"""Select platform for Open Karotz mood control."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.service import async_register_entity_service
import voluptuous as vol

from .const import BASE_URL, DOMAIN, MOOD_IDS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz select entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzMood(host, entry.entry_id)])


class OpenKarotzMood(SelectEntity):
    """Representation of the Open Karotz mood select."""

    _attr_name = "Open Karotz Mood"
    _attr_options = MOOD_IDS
    _attr_translation_key = "mood"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the mood select."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_mood"
        self._current_mood = MOOD_IDS[0]

    async def _async_play_mood(self, mood_id: str) -> bool:
        """Play mood on Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/apps/moods?id={mood_id}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to play mood: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error playing mood: %s", err)
            return False

    async def _async_play_random_mood(self) -> bool:
        """Play random mood on Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/apps/moods") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to play random mood: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error playing random mood: %s", err)
            return False

    @property
    def current_option(self) -> str | None:
        """Return the current mood."""
        return self._current_mood

    async def async_select_option(self, option: str) -> None:
        """Select a mood."""
        if option in MOOD_IDS:
            self._current_mood = option
            await self._async_play_mood(option)

    async def async_play_random(self) -> None:
        """Play random mood."""
        await self._async_play_random_mood()

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "set_mood_with_duration",
            {
                "required": [vol.Required("mood_id")],
                "optional": [vol.Optional("duration", default=30)],
            },
            "async_set_mood_with_duration",
        )
        
        self._register_entity_service(
            "play_mood_sequence",
            {
                "required": [vol.Required("mood_ids")],
                "optional": [
                    vol.Optional("delay", default=1.0),
                    vol.Optional("repeat", default=1),
                ],
            },
            "async_play_mood_sequence",
        )
    
    async def async_set_mood_with_duration(self, mood_id: str, duration: int = 30) -> None:
        """Set mood with a specific duration."""
        if mood_id in MOOD_IDS:
            self._current_mood = mood_id
            await self._async_play_mood(mood_id)
            # Implementation would add duration logic here
    
    async def async_play_mood_sequence(self, mood_ids: list[str], delay: float = 1.0, repeat: int = 1) -> None:
        """Play a sequence of moods."""
        import asyncio
        
        for _ in range(repeat):
            for mood_id in mood_ids:
                if mood_id in MOOD_IDS:
                    self._current_mood = mood_id
                    await self._async_play_mood(mood_id)
                    await asyncio.sleep(delay)
```

### Button Entity Service Pattern

```python
"""Button platform for Open Karotz actions."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.service import async_register_entity_service
import voluptuous as vol

from .const import BASE_URL, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz button entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([
        OpenKarotzClearCacheButton(host, entry.entry_id),
    ])


class OpenKarotzClearCacheButton(ButtonEntity):
    """Representation of the Open Karotz clear cache button."""

    _attr_name = "Open Karotz Clear Cache"
    _attr_translation_key = "clear_cache"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the clear cache button."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_clear_cache"

    async def _async_send_command(self, endpoint: str) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}{endpoint}") as resp:
                if resp.status == 200:
                    return True
                return False
        except Exception:
            return False

    async def async_press(self) -> None:
        """Press the button."""
        await self._async_send_command("/cgi-bin/clear_cache")

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "clear_cache_with_restart",
            {
                "required": [],
                "optional": [vol.Optional("restart", default=True)],
            },
            "async_clear_cache_with_restart",
        )
    
    async def async_clear_cache_with_restart(self, restart: bool = True) -> None:
        """Clear cache with optional restart."""
        await self._async_send_command("/cgi-bin/clear_cache")
        if restart:
            await self._async_send_command("/cgi-bin/restart")
```

### Switch Entity Service Pattern

```python
"""Switch platform for Open Karotz system controls."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.service import async_register_entity_service
import voluptuous as vol

from .const import BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz switch entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzSleepSwitch(host, entry.entry_id)])


class OpenKarotzSleepSwitch(SwitchEntity):
    """Representation of the Open Karotz sleep switch."""

    _attr_name = "Open Karotz Sleep"
    _attr_translation_key = "sleep"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the sleep switch."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_sleep"
        self._is_on = False

    async def _async_send_command(self, endpoint: str) -> bool:
        """Send command to Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}{endpoint}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to send command: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch (wake up)."""
        self._is_on = True
        await self._async_send_command("/cgi-bin/wake_up")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch (sleep)."""
        self._is_on = False
        await self._async_send_command("/cgi-bin/sleep")
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "sleep_with_timeout",
            {
                "required": [],
                "optional": [vol.Optional("timeout", default=3600)],
            },
            "async_sleep_with_timeout",
        )
        
        self._register_entity_service(
            "wake_up_after",
            {
                "required": [],
                "optional": [vol.Optional("delay", default=0)],
            },
            "async_wake_up_after",
        )
    
    async def async_sleep_with_timeout(self, timeout: int = 3600) -> None:
        """Sleep with automatic wake-up after timeout."""
        self._is_on = False
        await self._async_send_command("/cgi-bin/sleep")
        self.async_write_ha_state()
        # Implementation would add timeout scheduling here
    
    async def async_wake_up_after(self, delay: float = 0) -> None:
        """Wake up after a delay."""
        import asyncio
        
        if delay > 0:
            await asyncio.sleep(delay)
        self._is_on = True
        await self._async_send_command("/cgi-bin/wake_up")
        self.async_write_ha_state()
```

### Binary Sensor Entity Service Pattern

```python
"""Binary sensor platform for Open Karotz RFID."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.service import async_register_entity_service
import voluptuous as vol

from .const import BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz binary sensor entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzRfidSensor(host, entry.entry_id)])


class OpenKarotzRfidSensor(BinarySensorEntity):
    """Representation of the Open Karotz RFID sensor."""

    _attr_name = "Open Karotz RFID"
    _attr_device_class = BinarySensorDeviceClass.PRESENCE
    _attr_translation_key = "rfid"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the RFID sensor."""
        self._host = host
        self._attr_unique_id = f"{entry_id}_rfid"
        self._is_on = False
        self._tag_id = None

    async def _async_get_rfid_list(self) -> dict | None:
        """Get RFID list from Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        import json

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/rfid_list") as resp:
                if resp.status == 200:
                    text = await resp.text()
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        _LOGGER.error("Failed to parse JSON from rfid_list: %s", text)
                        return {"rfids": []}
                _LOGGER.error("Failed to get RFID list: %s", resp.status)
                return None
        except Exception as err:
            _LOGGER.error("Error getting RFID list: %s", err)
            return None

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self._is_on

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return the state attributes."""
        return {"tag_id": self._tag_id}

    async def async_update(self) -> None:
        """Update the entity status."""
        data = await self._async_get_rfid_list()
        if data and "rfids" in data and len(data["rfids"]) > 0:
            self._is_on = True
            self._tag_id = data["rfids"][0].get("tag")
        else:
            self._is_on = False
            self._tag_id = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "get_rfid_tags",
            {
                "required": [],
            },
            "async_get_rfid_tags",
        )
    
    async def async_get_rfid_tags(self) -> list[str]:
        """Get all registered RFID tags."""
        data = await self._async_get_rfid_list()
        if data and "rfids" in data:
            return [tag.get("tag") for tag in data["rfids"]]
        return []
```

### Sensor Entity Service Pattern

```python
"""Sensor platform for Open Karotz."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, PERCENTAGE
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.service import async_register_entity_service
import voluptuous as vol
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, STORAGE_KAROTZ, STORAGE_USB

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz sensor entities."""
    host = entry.data[CONF_HOST]
    coordinator = OpenKarotzCoordinator(hass, host)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            KarotzStorageSensor(coordinator, entry),
            UsbStorageSensor(coordinator, entry),
        ]
    )


class OpenKarotzCoordinator(DataUpdateCoordinator):
    """Class to manage data updates for Open Karotz."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Open Karotz",
            update_method=self._async_update_data,
            update_interval=None,
        )
        self.host = host

    async def _async_update_data(self):
        """Fetch data from Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        import json

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self.host}/cgi-bin/get_free_space") as resp:
                if resp.status == 200:
                    text = await resp.text()
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        _LOGGER.error("Failed to parse JSON from get_free_space: %s", text)
                        return None
                _LOGGER.error("Failed to fetch free space: %s", resp.status)
                return None
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            return None


class KarotzStorageSensor(CoordinatorEntity, SensorEntity):
    """Representation of the Karotz storage sensor."""

    _attr_translation_key = "karotz_storage"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: OpenKarotzCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Karotz Storage"
        self._attr_unique_id = f"{entry.entry_id}_{STORAGE_KAROTZ}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("karotz", {}).get("percent_used_space")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:memory"

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "get_storage_details",
            {
                "required": [],
            },
            "async_get_storage_details",
        )
    
    async def async_get_storage_details(self) -> dict:
        """Get detailed storage information."""
        if self.coordinator.data is None:
            return {}
        return self.coordinator.data.get("karotz", {})


class UsbStorageSensor(CoordinatorEntity, SensorEntity):
    """Representation of the USB storage sensor."""

    _attr_translation_key = "usb_storage"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: OpenKarotzCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "USB Storage"
        self._attr_unique_id = f"{entry.entry_id}_{STORAGE_USB}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("usb", {}).get("percent_used_space")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:usb"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self.coordinator.data is None:
            return False
        return self.coordinator.data.get("usb", {}).get("percent_used_space", -1) >= 0

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "get_storage_details",
            {
                "required": [],
            },
            "async_get_storage_details",
        )
    
    async def async_get_storage_details(self) -> dict:
        """Get detailed storage information."""
        if self.coordinator.data is None:
            return {}
        return self.coordinator.data.get("usb", {})
```

### Camera Entity Service Pattern

```python
"""Camera platform for Open Karotz snapshot."""
from __future__ import annotations

import logging

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.service import async_register_entity_service
import voluptuous as vol

from .const import BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Open Karotz camera entities."""
    host = entry.data[CONF_HOST]
    async_add_entities([OpenKarotzCamera(host, entry.entry_id)])


class OpenKarotzCamera(Camera):
    """Representation of the Open Karotz camera."""

    _attr_name = "Open Karotz Camera"
    _attr_translation_key = "camera"

    def __init__(self, host: str, entry_id: str) -> None:
        """Initialize the camera."""
        super().__init__()
        self._host = host
        self._attr_unique_id = f"{entry_id}_camera"
        self._last_image = None

    async def _async_capture_snapshot(self) -> bytes | None:
        """Capture a snapshot from Open Karotz."""
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        import json

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(f"http://{self._host}/cgi-bin/snapshot?silent=1") as resp:
                if resp.status == 200:
                    content_type = resp.headers.get("content-type", "")
                    if "image" in content_type:
                        return await resp.read()
                    text = await resp.text()
                    try:
                        json_data = json.loads(text)
                        _LOGGER.error("Snapshot API returned JSON instead of image: %s", json_data)
                        return None
                    except json.JSONDecodeError:
                        _LOGGER.error("Snapshot API returned non-image content: %s", text[:100])
                        return None
                _LOGGER.error("Failed to capture snapshot: %s", resp.status)
                return None
        except Exception as err:
            _LOGGER.error("Error capturing snapshot: %s", err)
            return None

    def camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return the current image."""
        return self._last_image

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return the current image."""
        self._last_image = await self._async_capture_snapshot()
        return self._last_image

    async def async_enable_motion_detection(self) -> None:
        """Enable motion detection."""
        pass

    async def async_disable_motion_detection(self) -> None:
        """Disable motion detection."""
        pass

    @property
    def motion_detection_enabled(self) -> bool:
        """Return the motion detection status."""
        return False

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Register entity services
        self._register_entity_service(
            "capture_snapshot_with_filename",
            {
                "required": [vol.Required("filename")],
                "optional": [
                    vol.Optional("width"),
                    vol.Optional("height"),
                ],
            },
            "async_capture_snapshot_with_filename",
        )
        
        self._register_entity_service(
            "capture_snapshot_with_timestamp",
            {
                "required": [],
                "optional": [
                    vol.Optional("width"),
                    vol.Optional("height"),
                ],
            },
            "async_capture_snapshot_with_timestamp",
        )
    
    async def async_capture_snapshot_with_filename(self, filename: str, width: int | None = None, height: int | None = None) -> bool:
        """Capture a snapshot and save to specified filename."""
        image = await self._async_capture_snapshot()
        if image:
            import os
            from homeassistant.core import HomeAssistant
            from homeassistant.helpers import config_validation as cv
            
            # Save image to specified path
            # Implementation would add file saving logic here
            return True
        return False
    
    async def async_capture_snapshot_with_timestamp(self, width: int | None = None, height: int | None = None) -> str:
        """Capture a snapshot and return the filename with timestamp."""
        import datetime
        from homeassistant.core import HomeAssistant
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"karotz_snapshot_{timestamp}.jpg"
        
        image = await self._async_capture_snapshot()
        if image:
            # Save image with timestamp filename
            # Implementation would add file saving logic here
            return filename
        return ""
```

### API Integration Pattern

```python
"""API module for Open Karotz integration."""
from __future__ import annotations

import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


class OpenKarotzAPI:
    """API class for Open Karotz."""

    def __init__(self, host: str) -> None:
        """Initialize the API."""
        self.host = host
        self._session = None

    async def _async_send_command(self, endpoint: str) -> bool:
        """Send command to Open Karotz."""
        if self._session is None:
            self._session = async_get_clientsession(self._hass)
        
        try:
            async with self._session.get(f"http://{self.host}{endpoint}") as resp:
                if resp.status == 200:
                    return True
                _LOGGER.error("Failed to send command: %s", resp.status)
                return False
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    async def play_tts(self, text: str, voice: str = "6") -> bool:
        """Play text-to-speech."""
        return await self._async_send_command(f"/cgi-bin/tts?text={text}&voice={voice}")

    async def play_sound(self, sound_id: str) -> bool:
        """Play a sound from the library."""
        return await self._async_send_command(f"/cgi-bin/sound?id={sound_id}")

    async def set_volume(self, volume: float) -> bool:
        """Set the volume level."""
        return await self._async_send_command(f"/cgi-bin/volume?level={volume}")

    async def set_led_color(self, rgb_color: tuple[int, int, int]) -> bool:
        """Set the LED color."""
        hex_color = f"{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}"
        return await self._async_send_command(f"/cgi-bin/leds?color={hex_color}")

    async def set_ear_position_single(self, position: int) -> bool:
        """Set both ears to the same position."""
        return await self._async_send_command(f"/cgi-bin/ears?left={position}&right={position}")

    async def set_ear_position(self, left: int, right: int) -> bool:
        """Set left and right ear positions separately."""
        return await self._async_send_command(f"/cgi-bin/ears?left={left}&right={right}")

    async def set_mood(self, mood_id: str) -> bool:
        """Set the mood."""
        return await self._async_send_command(f"/cgi-bin/apps/moods?id={mood_id}")

    async def wake_up(self) -> bool:
        """Wake up the Karotz."""
        return await self._async_send_command("/cgi-bin/wake_up")

    async def sleep(self) -> bool:
        """Put the Karotz to sleep."""
        return await self._async_send_command("/cgi-bin/sleep")

    async def clear_cache(self) -> bool:
        """Clear the cache."""
        return await self._async_send_command("/cgi-bin/clear_cache")

    async def get_status(self) -> dict:
        """Get the current status."""
        if self._session is None:
            self._session = async_get_clientsession(self._hass)
        
        try:
            async with self._session.get(f"http://{self.host}/cgi-bin/status") as resp:
                if resp.status == 200:
                    return await resp.json()
                _LOGGER.error("Failed to get status: %s", resp.status)
                return {}
        except Exception as err:
            _LOGGER.error("Error getting status: %s", err)
            return {}
```

### Constants Configuration

```python
"""Constants for the Open Karotz integration."""

DOMAIN = "open_karotz"

# API Base URL
BASE_URL = "http://192.168.1.70"

# Storage
STORAGE_KAROTZ = "karotz_percent_used_space"
STORAGE_USB = "usb_percent_used_space"

# LED Colors
LED_COLORS = {
    "red": "FF0000",
    "green": "00FF00",
    "blue": "0000FF",
    "yellow": "FFFF00",
    "cyan": "00FFFF",
    "magenta": "FF00FF",
    "white": "FFFFFF",
    "black": "000000",
}

# Ear Positions
EAR_MIN = 0
EAR_MAX = 16
EAR_DOWN = 0
EAR_HORIZONTAL = 8
EAR_UP = 16

# Sound IDs
SOUND_LIST = [
    "bip1", "bling", "flush", "install_ok", "jet1", "laser_15", 
    "merde", "ready", "rfid_error", "rfid_ok", "saut1", "start", 
    "twang_01", "twang_04"
]

# TTS Voices
TTS_VOICES = {
    "1": "French Male", "2": "French Female", "3": "Canadian French Male", "4": "Canadian French Female",
    "5": "English (US) Male", "6": "English (US) Female", "7": "English (UK) Male", "8": "English (UK) Female",
    "9": "German Male", "10": "German Female", "11": "Italian Male", "12": "Italian Female",
    "13": "Spanish Male", "14": "Spanish Female", "15": "Dutch Male", "16": "Dutch Female",
    "17": "Afrikan Male", "18": "Afrikan Female", "19": "Armenian Male", "20": "Armenian Female",
    "21": "Arabic Male", "22": "Arabic Female", "23": "Bosnian Male", "24": "Bosnian Female",
    "25": "Brazilian Portuguese Male", "26": "Brazilian Portuguese Female", "27": "Croatian Male", "28": "Croatian Female",
    "29": "Czech Male", "30": "Czech Female", "31": "Danish Male", "32": "Danish Female",
    "33": "English (Australian) Male", "34": "English (Australian) Female", "35": "Esperanto Male", "36": "Esperanto Female",
    "37": "Finnish Male", "38": "Finnish Female", "39": "Greek Male", "40": "Greek Female",
    "41": "Hatian Creole Male", "42": "Hatian Creole Female", "43": "Hindi Male", "44": "Hindi Female",
    "45": "Hungarian Male", "46": "Hungarian Female", "47": "Icelandic Male", "48": "Icelandic Female",
    "49": "Indonesian Male", "50": "Indonesian Female", "51": "Japanese Male", "52": "Japanese Female",
    "53": "Korean Male", "54": "Korean Female", "55": "Latin Male", "56": "Latin Female",
    "57": "Norwegian Male", "58": "Norwegian Female", "59": "Polish Male", "60": "Polish Female",
    "61": "Portuguese Male", "62": "Portuguese Female", "63": "Romanian Male", "64": "Romanian Female",
    "65": "Russian Male", "66": "Russian Female", "67": "Serbian Male", "68": "Serbian Female",
    "69": "Serbo-Croatian Male", "70": "Serbo-Croatian Female", "71": "Slovak Male", "72": "Slovak Female",
    "73": "Swahili Male", "74": "Swahili Female", "75": "Swedish Male", "76": "Swedish Female",
    "77": "Tamil Male", "78": "Tamil Female", "79": "Thai Male", "80": "Thai Female",
    "81": "Turkish Male", "82": "Turkish Female", "83": "Vietnamese Male", "84": "Vietnamese Female",
    "85": "Welsh Male", "86": "Welsh Female"
}

# Moods
MOOD_IDS = [str(i) for i in range(1, 302)]

# RFID
RFID_TAG_LENGTH = 10

# Squeezebox Commands
SQUEEZEBOX_START = "start"
SQUEEZEBOX_STOP = "stop"

# FTP Upload
FTP_DEFAULT_PORT = 21

# Configuration
CONF_HOST = "host"
CONF_NAME = "name"

# Default Values
DEFAULT_NAME = "Open Karotz"
```

---

## Summary

This document provides comprehensive notes on Home Assistant integration best practices for the Open Karotz integration. Key takeaways:

1. **Service Registration**: Always register services in `async_setup()`, not `async_setup_entry()`
2. **services.yaml**: Define service metadata including names, descriptions, and field specifications
3. **Entity Services**: Use `async_register_entity_service()` for platform-specific actions
4. **Response Data**: Raise `ServiceResponse` to return data to automations
5. **Icons**: Define icons in `icons.json` for consistent iconography
6. **Field Grouping**: Use `group` and `filter` for better field organization
7. **Translations**: Use translation keys in entities and define translations in `translations/en.json`

For more information, refer to the [Home Assistant Developer Documentation](https://developers.home-assistant.io/docs/dev_101_services/).