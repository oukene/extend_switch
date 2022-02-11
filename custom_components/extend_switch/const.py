"""Constants for the Detailed Hello World Push integration."""
from typing import DefaultDict
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

# This is the internal name of the integration, it should also match the directory
# name for the integration.
DOMAIN = "extend_switch"
NAME = "Extend Switch"
VERSION = "1.1.1"

CONF_DEVICE_NAME = "device_name"
CONF_SWITCH_ENTITY = "switch_entity"
CONF_PUSH_WAIT_TIME = "push_wait_time"
CONF_SWITCHES = "switches"
CONF_ADD_ANODHER = "add_another"
CONF_NAME = "name"
CONF_PUSH_MAX = "push_max"


NUMBER_MIN = 0
NUMBER_MAX = 100
NUMBER_STEP = 1
PUSH_MAX = 10

OPTIONS = [
    (CONF_SWITCH_ENTITY, "", cv.string),
    (CONF_PUSH_WAIT_TIME, "0.5", vol.All(vol.Coerce(float), vol.Range(0, 1))),
]
