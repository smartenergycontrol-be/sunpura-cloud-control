"""Config flow for Hello World integration."""
from __future__ import annotations

import json
import hashlib
import logging
import voluptuous as vol
from homeassistant import config_entries, exceptions

from .const import DOMAIN, BASE_URL  # pylint:disable=unused-import
from homeassistant.helpers.aiohttp_client import async_get_clientsession
_LOGGER = logging.getLogger(__name__)

# This is the schema that used to display the UI to the user. This simple
# schema has a single required host field, but it could include a number of fields
# such as username, password etc. See other components in the HA core code for
# further examples.
# Note the input displayed to the user will be translated. See the
# translations/<lang>.json file and strings.json. See here for further information:
# https://developers.home-assistant.io/docs/config_entries_config_flow_handler/#translations
# At the time of writing I found the translations created by the scaffold didn't
# quite work as documented and always gave me the "Lokalise key references" string
# (in square brackets), rather than the actual translated value. I did not attempt to
# figure this out or look further into it.
DATA_SCHEMA = vol.Schema({"username": str, "password": str})
# session_manager = coordinator.hass.data[DOMAIN]['session_manager']




class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self.data = {}
        self.family = {}

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                hash_pwd = self.md5_hash(user_input['password'])
                await self._login(user_input['username'], hash_pwd)
                self.data.update(user_input)
                return await self.async_step_select_device()
            except Exception as err:
                _LOGGER.error(f"Login error: {err}")
                errors["base"] = "login_error"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("username"): str,
                vol.Required("password"): str,
            }),
            errors=errors,
        )

    async def async_step_select_device(self, user_input=None):
        if user_input is not None:
            # _LOGGER.info(f"选择的设备: {user_input['devices']}")
            selected_device_id = user_input["family"]
            selected_device_name = self.family[selected_device_id]
            self.data.update({
                "selected_device_id": selected_device_id,
                "selected_device_name": selected_device_name
            })
            return self.async_create_entry(title=f"Integration - {selected_device_name}", data=self.data)

        try:
            self.family = await self._fetch_devices()
        except Exception as err:
            _LOGGER.error(f"Device fetch error: {err}")
            return self.async_abort(reason="device_fetch_error")

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({
                vol.Required("family"): vol.In(self.family),
            }),
        )

    def md5_hash(self, password: str) -> str:
        """Return an MD5 hash for the given password."""
        hasher = hashlib.md5()
        hasher.update(password.encode('utf-8'))
        return hasher.hexdigest()

    async def _login(self, username: str, password: str) -> bool:
        url = f"{BASE_URL}/user/login"
        session = async_get_clientsession(self.hass)
        headers = {'Content-Type': 'application/json'}
        req = {"email": username, "password": password, "phoneOs": 1, "phoneModel": "1.1", "appVersion": "V1.1"}
        json_data = json.dumps(req)

        async with session.post(url, headers=headers, data=json_data) as resp:
            if resp.status == 200:
                _LOGGER.debug(await resp.text())
                session.cookie_jar.update_cookies(resp.cookies)
                return True
            else:
                raise Exception("Failed to login")

    async def _fetch_devices(self) -> dict:
        url = f"{BASE_URL}/plant/getPlantVos"
        session = async_get_clientsession(self.hass)

        async with session.get(url) as resp:
            if resp.status == 200:
                session.cookie_jar.update_cookies(resp.cookies)
                devices = await resp.json()
                return {str(item["id"]): item["plantName"] for item in devices['obj']}
            else:
                raise Exception("Failed to fetch devices")


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
