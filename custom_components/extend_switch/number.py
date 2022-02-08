"""Platform for sensor integration."""
# This file shows the setup for the sensors associated with the cover.
# They are setup in the same way with the call to the async_setup_entry function
# via HA from the module __init__. Each sensor has a device_class, this tells HA how
# to display it in the UI (for know types). The unit_of_measurement property tells HA
# what the unit is, so it can display the correct range. For predefined types (such as
# battery), the unit_of_measurement should match what's expected.
import decimal
import random
import logging
from threading import Timer
import time
from xmlrpc.client import boolean
import homeassistant
from typing import Optional
from homeassistant.const import (
    STATE_UNKNOWN, STATE_UNAVAILABLE,
)

import asyncio

from homeassistant import components
from homeassistant import util
from homeassistant.helpers.entity import Entity

from .const import *
from homeassistant.exceptions import TemplateError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.helpers.event import async_track_state_change
from homeassistant.components.number import NumberEntity, NumberEntityDescription

import math

_LOGGER = logging.getLogger(__name__)

# See cover.py for more details.
# Note how both entities for each roller sensor (battry and illuminance) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.

ENTITY_ID_FORMAT = DOMAIN + ".{}"


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""

    hass.data[DOMAIN]["listener"] = []

    device = Device(NAME)

    new_devices = []

    for entity in config_entry.data.get(CONF_SWITCHES):
        _LOGGER.debug("add entity : %s, %s, %s",
                      entity[CONF_NAME], entity[CONF_SWITCH_ENTITY], entity[CONF_PUSH_WAIT_TIME])
        new_devices.append(
            ExtendSwitch(
                hass,
                device,
                entity[CONF_NAME],
                entity[CONF_SWITCH_ENTITY],
                entity[CONF_PUSH_WAIT_TIME]
            )
        )

    if new_devices:
        async_add_devices(new_devices)


class Device:
    """Dummy roller (device for HA) for Hello World example."""

    def __init__(self, name):
        """Init dummy roller."""
        self._id = name
        self.name = name
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        # Reports if the roller is moving up or down.
        # >0 is up, <0 is down. This very much just for demonstration.

        # Some static information about this device
        self.firmware_version = VERSION
        self.model = NAME
        self.manufacturer = NAME

    @property
    def device_id(self):
        """Return ID for roller."""
        return self._id

    def register_callback(self, callback):
        """Register callback, called when Roller changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback):
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changeds for the relevant device.
    async def publish_updates(self):
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

    def publish_updates(self):
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

# This base class shows the common properties and methods for a sensor as used in this
# example. See each sensor for further details about properties and methods that
# have been overridden.


class NumberBase(NumberEntity):
    """Base representation of a Hello World Sensor."""

    should_poll = False

    def __init__(self, device):
        """Initialize the sensor."""
        self._device = device

    # To link this entity to the cover device, this property must return an
    # identifiers value matching that used in the cover, but no other information such
    # as name. If name is returned, this entity will then also become a device in the
    # HA UI.
    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            # If desired, the name for the device could be different to the entity
            "name": self._device.device_id,
            "sw_version": self._device.firmware_version,
            "model": self._device.model,
            "manufacturer": self._device.manufacturer
        }

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return True

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._device.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._device.remove_callback(self.async_write_ha_state)


class ExtendSwitch(NumberBase):
    """Representation of a Thermal Comfort Sensor."""

    def __init__(self, hass, device, entity_name, switch_entity, push_wait_time):
        """Initialize the sensor."""
        super().__init__(device)

        self.hass = hass
        self._switch_entity = switch_entity

        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, "{}_{}".format(switch_entity, NAME), hass=hass)
        self._name = "{}".format(entity_name)
        # self._name = "{} {}".format(device.device_id, SENSOR_TYPES[sensor_type][1])
        self._unit_of_measurement = "push"
        self._state = None
        self._attributes = {}
        self._attributes["original entity id"] = switch_entity
        self._icon = None
        self._entity_picture = None
        self._reset_timer = None
        self._push_wait_time = push_wait_time

        # self._device_class = SENSOR_TYPES[sensor_type][0]
        self._unique_id = self.entity_id
        self._device = device
        self._value = PUSH_MIN

        self._attr_step = PUSH_STEP
        self._attr_min_value = PUSH_MIN
        self._attr_max_value = PUSH_MAX

        hass.data[DOMAIN]["listener"].append(async_track_state_change(
            self.hass, switch_entity, self.switch_entity_listener))
        state = self.hass.states.get(switch_entity)
        if _is_valid_state(state):
            self._attributes["switch state"] = state.state
            self._switch_state = state.state

    def switch_entity_listener(self, entity, old_state, new_state):
        _LOGGER.debug("call switch listener")
        try:
            """Handle temperature device state changes."""
            if _is_valid_state(new_state):
                if new_state.state == "on" or new_state.state == "off":
                    self._attributes["switch state"] = new_state.state
                    self.set_value(self._value + 1)

            self.async_schedule_update_ha_state(True)
        except:
            ''

    # def unique_id(self):
    #    """Return Unique ID string."""
    #    return self.unique_id

    """Sensor Properties"""

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return self._attributes

    @property
    def min_value(self):
        """Return the name of the sensor."""
        return self._attr_min_value

    @property
    def max_value(self):
        """Return the name of the sensor."""
        return self._attr_max_value

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        # return self._state
        return self._value

    # @property
    # def device_class(self) -> Optional[str]:
    #    """Return the device class of the sensor."""
    #    return self._device_class
    # @property
    # def entity_picture(self):
    #    """Return the entity_picture to use in the frontend, if any."""
    #    return self._entity_picture
    # @property
    # def unit_of_measurement(self):
    #    """Return the unit_of_measurement of the device."""
    #    return self._unit_of_measurement
    # @property
    # def should_poll(self):
    #    """No polling needed."""
    #    return False
    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        if self._unique_id is not None:
            return self._unique_id

    def update(self):
        """Update the state."""

    def set_value(self, value: float) -> None:
        _LOGGER.debug("set value : %d", value)
        if int(value) > 0:
            if self._reset_timer != None:
                self._reset_timer.cancel()
                _LOGGER.debug("cancel timer!!")
            self._reset_timer = Timer(self._push_wait_time, self.reset)
            self._reset_timer.start()

        self._value = int(value)
        self._device.publish_updates()

    def reset(self):
        _LOGGER.debug("reset")
        self.set_value(0)
        self._reset_timer = None


def _is_valid_state(state) -> bool:
    return state and state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE
