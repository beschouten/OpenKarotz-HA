"""OpenKarotz configuration flow."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_HOST, CONF_PORT
from .api import OpenKarotzAPI

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=80): int,
    }
)


class OpenKarotzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenKarotz."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> data_entry_flow.FlowResultType:
        """Handle the user step of the config flow."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = int(user_input.get(CONF_PORT, 80))

            # Test connection
            try:
                api = OpenKarotzAPI(host, port)
                await api.async_connect()

                # Check if device is reachable
                info = await api.get_info()
                if not info:
                    errors["base"] = "connection_failed"
                else:
                    await api.async_disconnect()

                    # Check for duplicate entries
                    if self._check_duplicate(host, port):
                        errors["base"] = "already_configured"

                    if not errors:
                        return self.async_create_entry(title=f"OpenKarotz ({host})", data=user_input)
            except Exception as e:
                _LOGGER.error(f"Connection test failed: {e}")
                errors["base"] = "connection_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    def _check_duplicate(self, host: str, port: int) -> bool:
        """Check if device is already configured."""
        for entry in self._async_current_entries():
            if entry.data.get(CONF_HOST) == host and entry.data.get(CONF_PORT) == port:
                return True
        return False


class OpenKarotzOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for OpenKarotz."""

    async def async_step_init(self, user_input: dict[str, str] | None = None) -> data_entry_flow.FlowResultType:
        """Handle the options step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_HOST): str,
                    vol.Optional(CONF_PORT): int,
                }
            ),
        )