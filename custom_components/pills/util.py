import json
import os.path
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


def daily_consumption(d):
  c = 0
  for t in [PILLS_MORNING, PILLS_NOON, PILLS_EVENING, PILLS_NIGHT]:
    c += d.get(t, 0)
  return c