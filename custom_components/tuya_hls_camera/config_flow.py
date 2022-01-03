"""Adds config flow for Tuya HLS Camera."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.components.tuya import config_flow

from .const import CONF_PASSWORD
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import PLATFORMS


class TuyaHlsCameraFlowHandler(config_flow.TuyaConfigFlow, domain=DOMAIN):
    """Config flow for tuya_hls_camera."""
