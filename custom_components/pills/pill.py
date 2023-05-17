from __future__ import annotations

import asyncio
import random

from .const import *

from homeassistant.core import HomeAssistant

class Pill:
  def __init__(self, hass: HomeAssistant, d) -> None:
    self._hass = hass
    self._data = d
    self._numbers = {}
    self._listeners = []
    
  def d(self):
    return self._data
  
  def take(self, time):
    if self.supply == 0.0: 
      return
    self.set_n(self.supply - self.get_n(time), PILLS_SUPPLY)
  
  @property
  def name(self) -> str:
    return self._data[CONF_PILL_NAME]+" "+self._data.get(CONF_PILL_SIZE, "")
  
  @property
  def days_remaining(self) -> int:
    daily = self.daily
    supply = self.supply
    
    if daily > 0:
      daysRemaining = supply / daily
    else:
      daysRemaining = 10000
    return daysRemaining
  
  @property
  def device_id(self):
    return self._data[CONF_PILL_NAME].lower()+"-"+self._data.get(CONF_PILL_SIZE, "").lower()

  def add_listener(self, listener) -> None:
    self._listeners.append(listener)

  def set_supply_entity(self, number_entity) -> None:
    self._supply = number_entity
  
  def set_n(self, val: float, time) -> None:
    self._numbers[time] = val
    [l.async_write_ha_state() for l in self._listeners]
  
  @property
  def daily(self) -> float:
    s = 0
    s += self.morning
    s += self.noon
    s += self.evening
    s += self.night
    return s
  
  def get_n(self, c) -> float:
    return self._numbers.setdefault(c, 0)
  
  @property
  def supply(self) -> float:
    return self._numbers.setdefault(PILLS_SUPPLY, 0)
  
  
  @property
  def morning(self) -> float:
    return self._numbers.setdefault(PILLS_MORNING, 0)
  
  @property
  def noon(self) -> float:
    return self._numbers.setdefault(PILLS_NOON, 0)

  @property
  def evening(self) -> float:
    return self._numbers.setdefault(PILLS_EVENING, 0)

  @property
  def night(self) -> float:
    return self._numbers.setdefault(PILLS_NIGHT, 0)

