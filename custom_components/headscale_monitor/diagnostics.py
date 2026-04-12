"""Diagnostics support for Tailscale."""

from __future__ import annotations

import json
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HeadscaleDataUpdateCoordinator

TO_REDACT = {
    CONF_API_KEY,
    CONF_HOST,
    "ip_addresses",
    "device_id",
    "machine_key",
    "preAuthKey",
    "node_key",
    "disco_key",
    "user",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: HeadscaleDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Round-trip via JSON to trigger serialization
    nodes = [json.loads(node.to_json()) for node in coordinator.data.values()]
    return async_redact_data({"nodes": nodes}, TO_REDACT)
