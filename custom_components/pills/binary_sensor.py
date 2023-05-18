from datetime import datetime, timedelta
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from typing import Any, Callable, Dict, Optional
import functools
from homeassistant import config_entries, core
from homeassistant.helpers.entity import Entity, DeviceInfo, generate_entity_id
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util.dt import now
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from homeassistant.const import (
    ATTR_NAME,
    CONF_ACCESS_TOKEN,
    CONF_NAME,
    CONF_PATH,
    CONF_URL,
)
from .const import *
from .pill import Pill


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [WarnSensor(hass, config)]
    async_add_entities(sensors, update_before_add=True)
    
class WarnSensor(BinarySensorEntity):
    _attr_has_entity_name = True
    

    def __init__(self, hass, pill: Pill):
        super().__init__()
        self.pill = pill
        self.pill.add_listener(self)
        self._device_id = self.pill.device_id
        self._unique_id = self._device_id+"_supply_problem"
        self._available = True
        self.attrs = {}
        self.entity_id = generate_entity_id("number.{}", self._unique_id, hass=hass)
        
    @property
    def is_on(self) -> bool:
        return self.pill.days_remaining < self.pill.d()[CONF_SENSOR_BEFORE_EMPTY]

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id
    
    @property
    def should_poll(self):
        return False
    
    @property
    def device_class(self):
        return BinarySensorDeviceClass.PROBLEM
    
    @property
    def translation_key(self) -> str | None:
        return STRING_PROBLEM_ENTITY

    @property
    def native_value(self):
        daily = self.pill.daily
        
        supply = self.pill.supply
        self.attrs[ATTR_DAILY] = daily
        
        if daily > 0:
          daysRemaining = supply / daily
        else:
          daysRemaining = 10000
  
        self.attrs[ATTR_DAYS_REMAINING] = daysRemaining
        self._state = now() + timedelta(days=daysRemaining)
        return self._state
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self.attrs
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                    (DOMAIN, self._device_id)
                },
            name=self.pill.name,
            )
    
    
  