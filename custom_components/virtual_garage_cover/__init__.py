"""The Virtual Garage Cover integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import cover as cover_module  # noqa: F401 - pre-import for event loop
from .const import (
    CONF_CLOSING_TIME,
    CONF_OPENING_TIME,
    CONF_TRAVEL_TIME,
    DEFAULT_TRAVEL_TIME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.COVER]


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entry from an older version."""
    if entry.version < 2:
        _LOGGER.info(
            "Migrating config entry %s from version %s to 2",
            entry.entry_id,
            entry.version,
        )
        new_data = {**entry.data}
        travel_time = new_data.pop(CONF_TRAVEL_TIME, DEFAULT_TRAVEL_TIME)
        new_data.setdefault(CONF_OPENING_TIME, travel_time)
        new_data.setdefault(CONF_CLOSING_TIME, travel_time)

        new_options = {**entry.options}
        if CONF_TRAVEL_TIME in new_options:
            opt_travel = new_options.pop(CONF_TRAVEL_TIME)
            new_options.setdefault(CONF_OPENING_TIME, opt_travel)
            new_options.setdefault(CONF_CLOSING_TIME, opt_travel)

        hass.config_entries.async_update_entry(
            entry, data=new_data, options=new_options, version=2
        )
        _LOGGER.info(
            "Migration complete: opening_time=%s, closing_time=%s",
            new_data[CONF_OPENING_TIME],
            new_data[CONF_CLOSING_TIME],
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Virtual Garage Cover from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
