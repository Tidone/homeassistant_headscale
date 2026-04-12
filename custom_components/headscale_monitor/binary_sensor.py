"""Support for Tailscale binary sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api.model import Node
from .const import DOMAIN
from .entity import HeadscaleEntity


@dataclass(frozen=True, kw_only=True)
class HeadscaleBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Headscale binary sensor entity."""

    is_on_fn: Callable[[Node], bool | None]


BINARY_SENSORS: tuple[HeadscaleBinarySensorEntityDescription, ...] = (
    HeadscaleBinarySensorEntityDescription(
        key="online",
        translation_key="client",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda device: device.online,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Headscale binary sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        HeadscaleBinarySensorEntity(
            coordinator=coordinator,
            node=node,
            description=description,
        )
        for node in coordinator.data.values()
        for description in BINARY_SENSORS
    )


class HeadscaleBinarySensorEntity(HeadscaleEntity, BinarySensorEntity):
    """Defines a Headscale binary sensor."""

    entity_description: HeadscaleBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        return self.entity_description.is_on_fn(self.coordinator.data[self.device_id])
