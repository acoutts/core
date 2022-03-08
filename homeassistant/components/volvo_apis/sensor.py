"""Support for the VolvoApis sensors."""
from __future__ import annotations

from datetime import timedelta
import json
import logging

from aiohttp import ClientConnectorError
from async_timeout import timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up volvo apis sensors."""
    coordinator = VolvoApisDataUpdateCoordinator(hass)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    sensors: list[VolvoApisSensor] = [
        VolvoApisSensor("car_locked", coordinator),
    ]

    async_add_entities(sensors)


class VolvoApisDataUpdateCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass):
        """Initialize my coordinator."""

        update_interval = timedelta(seconds=10)

        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="VolvoAPIs",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with timeout(10):
                print("Fetching data from volvo")
                data = {
                    "car_locked": True,
                }

        except (ClientConnectorError) as err:
            raise UpdateFailed(err) from err
        print("Returning data " + json.dumps(data))
        return data


class VolvoApisSensor(CoordinatorEntity, SensorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(
        self,
        name: str,
        coordinator: VolvoApisDataUpdateCoordinator,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_name = name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update from the coordinator."""
        print("Update from coordinator")
        self.async_write_ha_state()
