from __future__ import annotations
import logging
from homeassistant import core, config_entries
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import ServiceCall, callback

from .const import (
    DOMAIN,
    CONF_PILL_NAME,
    CONF_PILL_SIZE,
    CONF_PILLS,
    PILLS_MORNING,
    PILLS_NOON,
    PILLS_EVENING,
    PILLS_NIGHT
)

from .pill import Pill

_LOGGER = logging.getLogger(__name__)



async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Pills component."""
    hass.data.setdefault(DOMAIN, {})
    
    return True



async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    
    pill_object = Pill(hass, entry.data)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = pill_object
    
    device_registry = dr.async_get(hass)

    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        entry_type=DeviceEntryType.SERVICE,
        manufacturer="Nils",
        model=entry.data[CONF_PILL_NAME]+" "+entry.data.get(CONF_PILL_SIZE, ""),
        name=entry.data[CONF_PILL_NAME]+" "+entry.data.get(CONF_PILL_SIZE, ""),
        identifiers={(DOMAIN, entry.data[CONF_PILL_NAME].lower()+"-"+entry.data.get(CONF_PILL_SIZE, "").lower())},
    )
    
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "number")
    )
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    hass.async_create_task(
      hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )
    return True


