import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from typing import Any, Callable, Dict, Optional

from homeassistant import config_entries, core
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import Entity, DeviceInfo, generate_entity_id
from homeassistant.components.number import NumberEntity, RestoreNumber
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import EntityCategory
from .const import *
from .pill import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
      SERVICE_TAKE,
      { },
      "take",
    )

    sensors = [
      PillNumber(hass, config, PILLS_SUPPLY), 
      PillNumber(hass, config, PILLS_MORNING), 
      PillNumber(hass, config, PILLS_NOON),
      PillNumber(hass, config, PILLS_EVENING),
      PillNumber(hass, config, PILLS_NIGHT)
    ]
    async_add_entities(sensors, update_before_add=True)


class PillNumber(RestoreNumber):
    _attr_has_entity_name = True
    
  
    def __init__(self, hass, pill: Pill, time):
        super().__init__()
        self.pill = pill
        self._device_id = self.pill.device_id
        self._unique_id = self._device_id+"_"+time
        self._time = time
        self._available = True
        if time != PILLS_SUPPLY:
          self.attrs = { 'dose': 'dose', 'time': time }
        else:
          self.attrs = {}
        self.entity_id = generate_entity_id("number.{}", self._unique_id, hass=hass)
        self.pill.add_listener(self)
    

    def set_native_value(self, value: float) -> None:
        self.pill.set_n(value, self._time)
    
    async def async_added_to_hass(self):
      try: 
        last_number_data = (await self.async_get_last_number_data()).as_dict()
        self.set_native_value(last_number_data["native_value"])
      except AttributeError:
        self.set_native_value(0.0)
    
    
    def take(self):
      _LOGGER.debug("Calling service_take")
      self.pill.take(self._time)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self.attrs
    
    @property
    def entity_category(self):
      if self._time != PILLS_SUPPLY:
        return EntityCategory.CONFIG

    @property
    def native_value(self):
        return self.pill.get_n(self._time)

    @property
    def unique_id(self) -> str:
        return self._unique_id
    
    @property
    def native_step(self) -> float:
        return 0.25
    
    @property
    def translation_key(self) -> str:
      if self._time == PILLS_MORNING:
        return STRING_MORNING_ENTITY
      elif self._time == PILLS_NOON:
        return STRING_NOON_ENTITY
      elif self._time == PILLS_EVENING:
        return STRING_EVENING_ENTITY
      elif self._time == PILLS_NIGHT: 
        return STRING_NIGHT_ENTITY
      else:
        return STRING_SUPPLY_ENTITY
      
    
    @property
    def icon(self):
      if self._time == PILLS_SUPPLY:
        return "mdi:medication"
      else:
        return "mdi:pill-multiple"
    
    @property
    def native_min_value(self):
        return 0.0

    @property
    def native_max_value(self):
      if self._time == PILLS_SUPPLY:
        return 100000.0
      else:
        return 5.0
    
    @property
    def native_unit_of_measurement(self):
        return UNIT
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={ (DOMAIN, self._device_id) },
            name=self.name
          )
    
