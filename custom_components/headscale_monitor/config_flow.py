"""Config flow to configure the Tailscale integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api.exceptions import HeadscaleAuthenticationError, HeadscaleError
from .api.headscale import Headscale
from .const import DOMAIN


async def validate_input(hass: HomeAssistant, *, host: str, api_key: str) -> None:
    """Try using the give tailnet & api key against the Headscale API."""
    session = async_get_clientsession(hass)
    headscale = Headscale(
        session=session,
        api_key=api_key,
        host=host,
    )
    await headscale.nodes()


class TailscaleFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Tailscale."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            try:
                await validate_input(
                    self.hass,
                    host=user_input[CONF_HOST],
                    api_key=user_input[CONF_API_KEY],
                )
            except HeadscaleAuthenticationError:
                errors["base"] = "invalid_auth"
            except HeadscaleError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_API_KEY])
                self._abort_if_unique_id_configured(
                    updates={CONF_HOST: user_input[CONF_HOST]}
                )
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_API_KEY: user_input[CONF_API_KEY],
                    },
                )
        else:
            user_input = {}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "")): str,
                    vol.Required(
                        CONF_API_KEY, default=user_input.get(CONF_API_KEY, "")
                    ): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle initiation of re-authentication with Headscale."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle re-authentication with Headscale."""
        errors = {}

        if user_input is not None:
            reauth_entry = self._get_reauth_entry()
            try:
                await validate_input(
                    self.hass,
                    host=reauth_entry.data[CONF_HOST],
                    api_key=user_input[CONF_API_KEY],
                )
            except HeadscaleAuthenticationError:
                errors["base"] = "invalid_auth"
            except HeadscaleError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_API_KEY: user_input[CONF_API_KEY]},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )
