"""Support for One-Time Password (OTP)."""

from __future__ import annotations

import time

import pyotp
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType

DEFAULT_NAME = "OTP Sensor"

TIME_STEP = 30  # Default time step assumed by Google Authenticator


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the OTP sensor."""
    name = config[CONF_NAME]
    token = config[CONF_TOKEN]

    async_add_entities([TOTPSensor(name, token)], True)


# Only TOTP supported at the moment, HOTP might be added later
class TOTPSensor(SensorEntity):
    """Representation of a TOTP sensor."""

    _attr_icon = "mdi:update"
    _attr_should_poll = False
    _attr_native_value: StateType = None
    _next_expiration: float | None = None

    def __init__(self, name: str, token: str) -> None:
        """Initialize the sensor."""
        self._attr_name = name
        self._otp = pyotp.TOTP(token)

    async def async_added_to_hass(self) -> None:
        """Handle when an entity is about to be added to Home Assistant."""
        self._call_loop()

    @callback
    def _call_loop(self) -> None:
        self._attr_native_value = self._otp.now()
        self.async_write_ha_state()

        # Update must occur at even TIME_STEP, e.g. 12:00:00, 12:00:30,
        # 12:01:00, etc. in order to have synced time (see RFC6238)
        self._next_expiration = TIME_STEP - (time.time() % TIME_STEP)
        self.hass.loop.call_later(self._next_expiration, self._call_loop)
