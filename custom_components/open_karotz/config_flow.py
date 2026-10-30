"""Config flow for OpenKarotz."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OpenKarotzAPI, OpenKarotzError
from .const import (
    CONF_POLL_INTERVAL,
    CONFIG_ENTRY_VERSION,
    DEFAULT_NAME,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class OpenKarotzConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenKarotz."""

    VERSION = CONFIG_ENTRY_VERSION
    MINOR_VERSION = 1

    def __init__(self) -> None:
        self._discovered: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OpenKarotzOptionsFlow:
        return OpenKarotzOptionsFlow()

    async def _async_validate(self, host: str) -> dict[str, Any]:
        """Reach the device; returns status payload. Raises on failure."""
        api = OpenKarotzAPI(host, async_get_clientsession(self.hass))
        return await api.get_status()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                status = await self._async_validate(host)
            except OpenKarotzError:
                errors[CONF_HOST] = "cannot_connect"
            else:
                mac = status.get("wlan_mac") or status.get("eth_mac")
                unique_id = mac if mac and mac != "00:00:00:00:00:00" else host
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME) or DEFAULT_NAME,
                    data={CONF_HOST: host, CONF_NAME: user_input.get(CONF_NAME, DEFAULT_NAME)},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="192.168.1.70"): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        errors: dict[str, str] = {}
        if user_input is not None and entry is not None:
            host = user_input[CONF_HOST].strip()
            try:
                await self._async_validate(host)
            except OpenKarotzError:
                errors[CONF_HOST] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry, data={**entry.data, CONF_HOST: host}
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=entry.data[CONF_HOST] if entry else ""): str}
            ),
            errors=errors,
        )


class OpenKarotzOptionsFlow(OptionsFlow):
    """Options: poll interval."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        current = self.config_entry.options.get(
            CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_POLL_INTERVAL,
                        default=current,
                        description={"suggested_value": current},
                    ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
                }
            ),
        )
