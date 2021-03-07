""" Platform for rpi sensor integration.

Example configuration.yaml entry:


sensor:
  - platform: rpi_sensor
    name: "Test0 Rpi"
    host: "rpi-test-0"
    scan_interval: 30

"""

from homeassistant.const import CONF_HOST, CONF_NAME, TEMP_CELSIUS, PRESSURE_HPA, PERCENTAGE, DEVICE_CLASS_TIMESTAMP, DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_PRESSURE
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from urllib import request, parse
from urllib.error import URLError
import json
import logging
from datetime import timedelta, datetime

_LOGGER = logging.getLogger(__name__)

DOMAIN = "rpi_sensor"
DOMAIN_DATA = DOMAIN + "data"

DATA_REFRESH_INTERVAL_MS = 10 * 1000

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_NAME): cv.string
    }
)

def api(host, fallback, refreshInterval):
    result = fallback
    now = datetime.timestamp(datetime.now()) * 1000
    if ((now - fallback["timestamp"]) > refreshInterval):
        url = "http://{}.local/sensor/now.json".format (host)
        req = request.Request(url)
        with request.urlopen(req) as response:
            result = json.loads(response.read().decode())
    return result

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # we want to store multiple sensors in our HASS domain, so if it hasn't been initialized we need
    # a new dictionary
    if (not (DOMAIN in hass.data)):
      hass.data[DOMAIN] = { }
    dataHost = hass.data[DOMAIN]
    record = dataHost[config[CONF_HOST]] = api (config[CONF_HOST], { "timestamp": 0 }, 0)
    if (record["temperature"] != "-"):
        add_entities([RpiTemperatureSensor(hass, config[CONF_HOST], config[CONF_NAME] + "_temperature")])
    if (record["humidity"] != "-"):
        add_entities([RpiHumiditySensor(hass, config[CONF_HOST], config[CONF_NAME] + "_humidity")])
    if (record["pressure"] != "-"):
        add_entities([RpiPressureSensor(hass, config[CONF_HOST], config[CONF_NAME] + "_pressure")])


class RpiTemperatureSensor(Entity):
    def __init__(self, hass, host, name):
        self._hass = hass
        self._host = host
        self._name = name
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._hass.data[DOMAIN][self._host]["temperature"]

    @property
    def device_class (self):
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    def update(self):
        try:
            self._hass.data[DOMAIN][self._host] = api (self._host, self._hass.data[DOMAIN][self._host], DATA_REFRESH_INTERVAL_MS)
        except URLError as error:
            _LOGGER.error( "Unable to retrieve data from Sensor host ({}): {}".format(self._host, error.reason) )
            return

class RpiHumiditySensor(Entity):
    def __init__(self, hass, host, name):
        self._hass = hass
        self._host = host
        self._name = name
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._hass.data[DOMAIN][self._host]["humidy"]

    @property
    def device_class (self):
        return DEVICE_CLASS_HUMIDITY

    @property
    def unit_of_measurement(self):
        return PERCENTAGE

    def update(self):
        try:
            self._hass.data[DOMAIN][self._host] = api (self._host, self._hass.data[DOMAIN][self._host], DATA_REFRESH_INTERVAL_MS)
        except URLError as error:
            _LOGGER.error( "Unable to retrieve data from Sensor host ({}): {}".format(self._host, error.reason) )
            return

class RpiPressureSensor(Entity):
    def __init__(self, hass, host, name):
        self._hass = hass
        self._host = host
        self._name = name
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._hass.data[DOMAIN][self._host]["pressure"]

    @property
    def device_class (self):
        return DEVICE_CLASS_PRESSURE

    @property
    def unit_of_measurement(self):
        return PRESSURE_HPA

    def update(self):
        try:
            self._hass.data[DOMAIN][self._host] = api (self._host, self._hass.data[DOMAIN][self._host], DATA_REFRESH_INTERVAL_MS)
        except URLError as error:
            _LOGGER.error( "Unable to retrieve data from Sensor host ({}): {}".format(self._host, error.reason) )
            return
