"""Mock HomeAssistant fixtures for testing."""
import sys
from unittest.mock import MagicMock, AsyncMock

# Mock HomeAssistant modules
sys.modules['homeassistant'] = MagicMock()
sys.modules['homeassistant.config_entries'] = MagicMock()
sys.modules['homeassistant.const'] = MagicMock()
sys.modules['homeassistant.core'] = MagicMock()
sys.modules['homeassistant.helpers'] = MagicMock()
sys.modules['homeassistant.helpers.aiohttp_client'] = MagicMock()
sys.modules['homeassistant.helpers.entity_platform'] = MagicMock()
sys.modules['homeassistant.helpers.update_coordinator'] = MagicMock()
sys.modules['homeassistant.components'] = MagicMock()
sys.modules['homeassistant.components.sensor'] = MagicMock()
sys.modules['homeassistant.components.light'] = MagicMock()
sys.modules['homeassistant.components.cover'] = MagicMock()
sys.modules['homeassistant.components.media_player'] = MagicMock()
sys.modules['homeassistant.components.select'] = MagicMock()
sys.modules['homeassistant.components.camera'] = MagicMock()
sys.modules['homeassistant.components.switch'] = MagicMock()
sys.modules['homeassistant.components.binary_sensor'] = MagicMock()
sys.modules['homeassistant.components.button'] = MagicMock()
sys.modules['homeassistant.data_entry_flow'] = MagicMock()
sys.modules['homeassistant.exceptions'] = MagicMock()

# Mock voluptuous
sys.modules['voluptuous'] = MagicMock()

print("Mock setup complete")