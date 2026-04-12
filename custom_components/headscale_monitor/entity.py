"""The Tailscale integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api.model import Node as HeadscaleNode
from .const import DOMAIN


class HeadscaleEntity(CoordinatorEntity):
    """Defines a Headscale base entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        coordinator: DataUpdateCoordinator,
        node: HeadscaleNode,
        description: EntityDescription,
    ) -> None:
        """Initialize a Headscale sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self.device_id = node.id
        self._attr_unique_id = f"{node.id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        node: HeadscaleNode = self.coordinator.data[self.device_id]

        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, node.id)},
            manufacturer="Headscale",
            name=node.given_name or node.name,
        )
