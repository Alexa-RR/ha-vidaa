"""Config flow for the VIDAA TV integration."""

from __future__ import annotations

import os
import uuid
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_NAME, CONF_PORT
from homeassistant.helpers import device_registry as dr

from .const import (
    CLIENT_CERT,
    CLIENT_KEY,
    CONF_CLIENT_ID,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)
from .vidaa import CannotConnect, InvalidAuth, VidaaTV

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Optional(CONF_MAC, default=""): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)

PIN_SCHEMA = vol.Schema({vol.Required("pin"): str})


class VidaaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VIDAA TV."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise the flow."""
        self._data: dict[str, Any] = {}
        self._tv: VidaaTV | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect connection details and start pairing."""
        errors: dict[str, str] = {}

        if user_input is not None:
            mac = user_input.get(CONF_MAC, "").strip()
            if mac:
                formatted = dr.format_mac(mac)
                await self.async_set_unique_id(formatted)
                self._abort_if_unique_id_configured()
                user_input[CONF_MAC] = formatted

            client_id = f"ha-{uuid.uuid4().hex[:12]}"
            self._data = {**user_input, CONF_CLIENT_ID: client_id}

            package_dir = os.path.dirname(__file__)
            tv = VidaaTV(
                self.hass,
                host=user_input[CONF_HOST],
                port=user_input.get(CONF_PORT, DEFAULT_PORT),
                client_id=client_id,
                certfile=os.path.join(package_dir, CLIENT_CERT),
                keyfile=os.path.join(package_dir, CLIENT_KEY),
            )
            try:
                await tv.async_connect()
                already_paired = await tv.async_authenticate()
            except CannotConnect:
                errors["base"] = "cannot_connect"
                await _safe_disconnect(tv)
            else:
                self._tv = tv
                if already_paired:
                    return await self._async_create()
                return await self.async_step_pair()

        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )

    async def async_step_pair(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the PIN displayed on the TV."""
        errors: dict[str, str] = {}
        assert self._tv is not None

        if user_input is not None:
            try:
                await self._tv.async_send_pin(user_input["pin"])
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            else:
                return await self._async_create()

        return self.async_show_form(
            step_id="pair", data_schema=PIN_SCHEMA, errors=errors
        )

    async def _async_create(self) -> ConfigFlowResult:
        """Finish the flow and create the entry."""
        if self._tv is not None:
            await _safe_disconnect(self._tv)
        return self.async_create_entry(
            title=self._data.get(CONF_NAME, DEFAULT_NAME), data=self._data
        )


async def _safe_disconnect(tv: VidaaTV) -> None:
    """Disconnect a transient client, ignoring errors."""
    try:
        await tv.async_disconnect()
    except Exception:  # noqa: BLE001 - best effort cleanup
        pass
