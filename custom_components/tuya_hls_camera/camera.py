from __future__ import annotations

import datetime
from pathlib import Path

from homeassistant.components import ffmpeg
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.tuya.camera import TuyaCameraEntity
from homeassistant.components.tuya.camera import async_setup_entry as tuya_camera_setup_entry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.components.tuya import (HomeAssistantTuyaData, DeviceListener)
from homeassistant.components.tuya.camera import CAMERAS
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util.dt import utcnow
from homeassistant.components.camera import SUPPORT_STREAM

from tuya_iot import (
    TuyaDevice,
    TuyaDeviceManager,
)

from .const import (
    DOMAIN,
    TUYA_DISCOVERY_NEW,
    LOGGER,
)

STREAM_EXPIRATION_TIMEDELTA = datetime.timedelta(minutes=9)
PLACEHOLDER = Path(__file__).parent / "placeholder.png"

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

    def __init__(self, device: TuyaDevice, device_manager: TuyaDeviceManager) -> None:
        super().__init__(device, device_manager)
        self._stream: str | None = None
        self._stream_refresh_time: datetime.timedelta | None = None
        self._stream_refresh_unsub: Callable[[], None] | None = None

    async def stream_source(self) -> str:
        """Return the source of the stream."""

        if not self._stream:
            self._stream = await self.hass.async_add_executor_job(
                self.device_manager.get_device_stream_allocate,
                self.device.id,
                "hls",
            )
            self._stream_refresh_time = STREAM_EXPIRATION_TIMEDELTA + utcnow()
            LOGGER.error(
                "Setup Initial stream: %s, expiry: %s",
                self._stream,
                self._stream_refresh_time.isoformat())
            # Schedule a stream refresh
            self._schedule_stream_refresh()

        assert self._stream
        return self._stream

    def _schedule_stream_refresh(self) -> None:
        """Schedules an alarm to refresh the stream url before expriation."""
        assert self._stream
        assert self._stream_refresh_time

        # Schedule an alarm to get a new stream
        if self._stream_refresh_unsub is not None:
            self._stream_refresh_unsub()

        self._stream_refresh_unsub = async_track_point_in_utc_time(
            self.hass,
            self._handle_stream_refresh,
            self._stream_refresh_time,
        )

    async def _handle_stream_refresh(self, now: datetime.datetime) -> None:
        """Alarm that fires to get a new stream."""
        self._stream = await self.hass.async_add_executor_job(
                self.device_manager.get_device_stream_allocate,
                self.device.id,
                "hls",
            )
        if not self.stream:
            await self.create_stream()
            LOGGER.error("Create new stream source")
        else:
            self.stream.update_source(self._stream)
            LOGGER.error("Update stream source")

        if not self.stream.available():
            self.stream.start()

        LOGGER.error(
            "Refresh stream: %s, expiry: %s",
            self._stream,
            self._stream_refresh_time.isoformat())
        self._stream_refresh_time = utcnow() + STREAM_EXPIRATION_TIMEDELTA

        # Schedule next stream refresh
        self._schedule_stream_refresh()
