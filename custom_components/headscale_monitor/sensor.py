"""Support for Tailscale sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api.model import Node as HeadscaleDevice
from .const import DOMAIN
from .entity import HeadscaleEntity


@dataclass(frozen=True, kw_only=True)
class HeadscaleSensorEntityDescription(SensorEntityDescription):
    """Describes a Headscale sensor entity."""

    value_fn: Callable[[HeadscaleDevice], datetime | str | None]


SENSORS: tuple[HeadscaleSensorEntityDescription, ...] = (
    HeadscaleSensorEntityDescription(
        key="expires",
        translation_key="expires",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: (
            device.expiry if device.expiry and device.expiry.year > 2000 else None
        ),
    ),
    HeadscaleSensorEntityDescription(
        key="ip",
        translation_key="ip",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.ip_addresses[0] if device.ip_addresses else None,
    ),
    HeadscaleSensorEntityDescription(
        key="last_seen",
        translation_key="last_seen",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda device: device.last_seen,
    ),
    HeadscaleSensorEntityDescription(
        key="user",
        translation_key="user",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: (
            (device.user.display_name or device.user.name) if device.user else None
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Headscale sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        HeadscaleSensorEntity(
            coordinator=coordinator,
            node=node,
            description=description,
        )
        for node in coordinator.data.values()
        for description in SENSORS
    )


class HeadscaleSensorEntity(HeadscaleEntity, SensorEntity):
    """Defines a Headscale sensor."""

    entity_description: HeadscaleSensorEntityDescription

    @property
    def native_value(self) -> datetime | str | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data[self.device_id])
