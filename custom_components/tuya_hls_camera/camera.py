from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.tuya.camera import TuyaCameraEntity
from homeassistant.components.tuya.camera import async_setup_entry as tuya_camera_setup_entry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.components.tuya import (HomeAssistantTuyaData, DeviceListener)
from homeassistant.components.tuya.camera import CAMERAS

from .const import DOMAIN, TUYA_DISCOVERY_NEW

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya cameras dynamically through Tuya discovery."""
    hass_data: HomeAssistantTuyaData = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_discover_device(device_ids: list[str]) -> None:
        """Discover and add a discovered Tuya camera."""
        entities: list[TuyaHlsCameraEntity] = []
        for device_id in device_ids:
            device = hass_data.device_manager.device_map[device_id]
            if device.category in CAMERAS:
                entities.append(TuyaHlsCameraEntity(device, hass_data.device_manager))

        async_add_entities(entities)

    async_discover_device([*hass_data.device_manager.device_map])

    entry.async_on_unload(
        async_dispatcher_connect(hass, TUYA_DISCOVERY_NEW, async_discover_device)
    )


class TuyaHlsCameraEntity(TuyaCameraEntity):
    """Tuya HLS Camera Entity."""

    async def stream_source(self) -> str:
        """Return the source of the stream."""
        return await self.hass.async_add_executor_job(
            self.device_manager.get_device_stream_allocate,
            self.device.id,
            "hls",
        )