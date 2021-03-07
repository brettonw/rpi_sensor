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
    try:
        now = datetime.timestamp(datetime.now()) * 1000
        if ((now - fallback["timestamp"]) > refreshInterval):
            url = "http://{}.local/sensor/now.json".format (host)
            req = request.Request(url)
            with request.urlopen(req) as response:
                result = json.loads(response.read().decode())
    except URLError as error:
        _LOGGER.error( "Unable to retrieve data from Sensor host ({}): {}".format(host, error.reason) )
    return result

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # we want to store multiple sensors in our HASS domain, so if it hasn't been initialized we need
    # a new dictionary
    if (not (DOMAIN in hass.data)):
        hass.data[DOMAIN] = { }
    dataHost = hass.data[DOMAIN]

    # get a sample record from the sensor to set up the configuration
    record = dataHost[config[CONF_HOST]] = api (config[CONF_HOST], { "timestamp": 0 }, 0)
    if ("humidity" in record):
        _LOGGER.debug( "Adding Humidity Sensor from host ({})".format(config[CONF_HOST]) )
        add_entities([RpiSensorHumidity(hass, config[CONF_HOST], config[CONF_NAME] + " Humidity")])
    if ("pressure" in record):
        _LOGGER.debug( "Adding Pressure Sensor from host ({})".format(config[CONF_HOST]) )
        add_entities([RpiSensorPressure(hass, config[CONF_HOST], config[CONF_NAME] + " Pressure")])
    if ("temperature" in record):
        _LOGGER.debug( "Adding Temperature Sensor from host ({})".format(config[CONF_HOST]) )
        add_entities([RpiSensorTemperature(hass, config[CONF_HOST], config[CONF_NAME] + " Temperature")])

class RpiSensor (Entity):
    def __init__(self, hass, host, name):
        self._hass = hass
        self._host = host
        self._name = name
        self.update()

    @property
    def name(self):
        return self._name

    def update(self):
        self._hass.data[DOMAIN][self._host] = api (self._host, self._hass.data[DOMAIN][self._host], DATA_REFRESH_INTERVAL_MS)

class RpiSensorTemperature(RpiSensor):
    def __init__(self, hass, host, name):
        RpiSensor.__init__(self, hass, host, name)

    @property
    def state(self):
        return self._hass.data[DOMAIN][self._host]["temperature"]

    @property
    def device_class (self):
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

class RpiSensorHumidity(RpiSensor):
    def __init__(self, hass, host, name):
        RpiSensor.__init__(self, hass, host, name)

    @property
    def state(self):
        return self._hass.data[DOMAIN][self._host]["humidity"]

    @property
    def device_class (self):
        return DEVICE_CLASS_HUMIDITY

    @property
    def unit_of_measurement(self):
        return PERCENTAGE

class RpiSensorPressure(RpiSensor):
    def __init__(self, hass, host, name):
        RpiSensor.__init__(self, hass, host, name)

    @property
    def state(self):
        return self._hass.data[DOMAIN][self._host]["pressure"]

    @property
    def device_class (self):
        return DEVICE_CLASS_PRESSURE

    @property
    def unit_of_measurement(self):
        return PRESSURE_HPA
