"""Support for tracking the moon phases."""
from astral import Astral
import voluptuous as vol
import datetime

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
import homeassistant.util.dt as dt_util

DEFAULT_NAME = "Moon"
DAY_FULL_MOON = 14

STATE_FIRST_QUARTER = "first_quarter"
STATE_FULL_MOON = "full_moon"
STATE_LAST_QUARTER = "last_quarter"
STATE_NEW_MOON = "new_moon"
STATE_WANING_CRESCENT = "waning_crescent"
STATE_WANING_GIBBOUS = "waning_gibbous"
STATE_WAXING_GIBBOUS = "waxing_gibbous"
STATE_WAXING_CRESCENT = "waxing_crescent"

STATE_ATTR_NEXT_FULL_MOON = "next_full_moon"
STATE_ATTR_NEXT_NEW_MOON = "next_new_moon"

MOON_ICONS = {
    STATE_FIRST_QUARTER: "mdi:moon-first-quarter",
    STATE_FULL_MOON: "mdi:moon-full",
    STATE_LAST_QUARTER: "mdi:moon-last-quarter",
    STATE_NEW_MOON: "mdi:moon-new",
    STATE_WANING_CRESCENT: "mdi:moon-waning-crescent",
    STATE_WANING_GIBBOUS: "mdi:moon-waning-gibbous",
    STATE_WAXING_CRESCENT: "mdi:moon-waxing-crescent",
    STATE_WAXING_GIBBOUS: "mdi:moon-waxing-gibbous",
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string}
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Moon sensor."""
    name = config.get(CONF_NAME)

    async_add_entities([MoonSensor(name)], True)


class MoonSensor(Entity):
    """Representation of a Moon sensor."""

    def __init__(self, name):
        """Initialize the moon sensor."""
        self._name = name
        self._state = None
        self.next_full_moon = self.next_new_moon = None
        self._astral = Astral()

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def device_class(self):
        """Return the device class of the entity."""
        return "moon__phase"

    @property
    def state(self):
        """Return the state of the device."""
        if self._state == 0:
            return STATE_NEW_MOON
        if self._state < 7:
            return STATE_WAXING_CRESCENT
        if self._state == 7:
            return STATE_FIRST_QUARTER
        if self._state < DAY_FULL_MOON:
            return STATE_WAXING_GIBBOUS
        if self._state == DAY_FULL_MOON:
            return STATE_FULL_MOON
        if self._state < 21:
            return STATE_WANING_GIBBOUS
        if self._state == 21:
            return STATE_LAST_QUARTER
        return STATE_WANING_CRESCENT

    @property
    def state_attributes(self):
        """Return the state attributes of the moon."""
        return {
            STATE_ATTR_NEXT_FULL_MOON: self.next_full_moon,
            STATE_ATTR_NEXT_NEW_MOON: self.next_new_moon,
        }
    
    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return MOON_ICONS.get(self.state)

    async def async_update(self):
        """Get the time and updates the states."""
        today = dt_util.as_local(dt_util.utcnow()).date()
        self._state = self._astral.moon_phase(today)
        next_full_moon_days = DAY_FULL_MOON - self._state
        next_full_moon_days = next_full_moon_days + 28 if next_full_moon_days < 1 else next_full_moon_days
        self.next_full_moon = today + datetime.timedelta(days=next_full_moon_days)
        next_new_moon_days = self._state + 28 if self._state < 1 else self._state
        self.next_new_moon = today + datetime.timedelta(days=next_new_moon_days)
