"""DataUpdateCoordinator for the Headscale integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api.exceptions import HeadscaleAuthenticationError
from .api.headscale import Headscale
from .api.model import Node
from .const import DOMAIN, LOGGER, SCAN_INTERVAL


class HeadscaleDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Node]]):
    """The Headscale Data Update Coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the Headscale coordinator."""
        session = async_get_clientsession(hass)
        self.headscale = Headscale(
            session=session,
            host=config_entry.data[CONF_HOST],
            api_key=config_entry.data[CONF_API_KEY],
        )
        self.previous_devices: set[str] = set()

        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Node]:
        """Fetch devices from Headscale and remove stale devices from HA."""
        try:
            devices = await self.headscale.nodes()
        except HeadscaleAuthenticationError as err:
            raise ConfigEntryAuthFailed from err

        # Get current device IDs
        current_device_ids = set(devices.keys())

        # Find devices that were removed from Headscale
        if self.previous_devices:
            stale_device_ids = self.previous_devices - current_device_ids
            if stale_device_ids:
                await self._remove_stale_devices(stale_device_ids)

        # Update previous devices set for next comparison
        self.previous_devices = current_device_ids

        return devices

    async def _remove_stale_devices(self, stale_device_ids: set[str]) -> None:
        """Remove devices that no longer exist in Headscale."""
        device_registry = dr.async_get(self.hass)

        for device_id in stale_device_ids:
            device = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
            if device:
                LOGGER.debug("Removing stale device: %s", device_id)
                device_registry.async_remove_device(device.id)
