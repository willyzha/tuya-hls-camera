from homeassistant.const import (
    Platform,
)

"""Constants for Tuya HLS Camera."""
# Base component constants
NAME = "Tuya HLS Camera"
DOMAIN = "tuya_hls_camera"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.0"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/willyzha/tuya-hls-camera/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
PLATFORMS = [
    Platform.CAMERA,
]

TUYA_DISCOVERY_NEW = "tuya_discovery_new"
TUYA_HA_SIGNAL_UPDATE_ENTITY = "tuya_entry_update"

# Configuration and options
CONF_AUTH_TYPE = "auth_type"
CONF_PROJECT_TYPE = "tuya_project_type"
CONF_ENDPOINT = "endpoint"
CONF_ACCESS_ID = "access_id"
CONF_ACCESS_SECRET = "access_secret"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_COUNTRY_CODE = "country_code"
CONF_APP_TYPE = "tuya_app_type"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
