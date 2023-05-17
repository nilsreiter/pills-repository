import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, CONF_PATH, CONF_URL
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import *

_LOGGER = logging.getLogger(__name__)

PILL_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PILL_NAME): cv.string,
        vol.Optional(CONF_PILL_SIZE): cv.string,
        vol.Optional(CONF_PILL_AGENT): cv.string,
        vol.Optional(CONF_PILL_VENDOR): cv.string,
        vol.Required(CONF_SENSOR_BEFORE_EMPTY, default=10): cv.positive_int
    }
)

class PillsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Github Custom config flow."""

    data: Optional[Dict[str, Any]]
    
    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            
            # Input is valid, set data.
            self.data = user_input
            # Return the form of the next step.
            return self.async_create_entry(
              title=self.data[CONF_PILL_NAME]+" "+self.data.get(CONF_PILL_SIZE, ""), 
              data=self.data
            )

        return self.async_show_form(
            step_id="user", data_schema=PILL_SCHEMA, errors=errors
        )

