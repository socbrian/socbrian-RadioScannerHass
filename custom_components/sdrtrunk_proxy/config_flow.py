"""Config flow for SDRTrunk Proxy."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_METADATA_URL, CONF_NAME, CONF_STREAM_URL, DEFAULT_NAME, DOMAIN


class SDRTrunkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_STREAM_URL])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_STREAM_URL): str,
                vol.Required(CONF_METADATA_URL): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
