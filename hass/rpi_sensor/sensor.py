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
        add_entities([RpiSensor(hass, config[CONF_HOST], config[CONF_NAME], "humidity", DEVICE_CLASS_HUMIDITY, PERCENTAGE)])
    if ("pressure" in record):
        add_entities([RpiSensor(hass, config[CONF_HOST], config[CONF_NAME], "pressure", DEVICE_CLASS_PRESSURE, PRESSURE_HPA)])
    if ("temperature" in record):
        add_entities([RpiSensor(hass, config[CONF_HOST], config[CONF_NAME], "temperature", DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS)])

class RpiSensor (Entity):
    def __init__(self, hass, host, name, type, device_class, unit_of_measurement):
        _LOGGER.debug( "Adding {} sensor from host ({})".format(type, host) )
        self._hass = hass
        self._host = host
        self._name = "{} {}".format (name, type.capitalize ())
        self._type = type
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._hass.data[DOMAIN][self._host][self._type]

    @property
    def device_class (self):
        return self._device_class

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    def update(self):
        self._hass.data[DOMAIN][self._host] = api (self._host, self._hass.data[DOMAIN][self._host], DATA_REFRESH_INTERVAL_MS)
