""" Platform for rpi sensor integration.

Example configuration.yaml entry:

sensor:
  - platform: rpi_sensor
    name: "Test0 Rpi"
    host: "rpi-test-0"
    scan_interval: 30

NOTE:
    HASS seems to have worked too hard to narrow the types of supported sensors. They would
    be much better off going with general types, "percentage", "number with range", "list", etc.
"""
from __future__ import annotations
from urllib import request
from urllib.error import URLError
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    PLATFORM_SCHEMA
)

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfLength,
    PERCENTAGE
)

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.helpers.config_validation as cv
import json
import logging


# this essentially caches the last result for at least this long
DATA_REFRESH_INTERVAL_MS = 10 * 1000

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_NAME): cv.string
    }
)


class RpiSensorType:
    # these are constants used in the sensor setup on its host
    RELATIVE_HUMIDITY = "relative_humidity"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    DISTANCE = "distance"
    PH = "ph"
    CONDUCTIVITY = "conductivity"
    CPU_TEMPERATURE = "cpu-temperature"


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    # get a sample record from the sensor to create the needed entities
    record = RpiSensor.api(config[CONF_HOST], {SensorDeviceClass.TIMESTAMP: 0}, 0)
    entities_to_add = []
    if RpiSensorType.RELATIVE_HUMIDITY in record:
        entities_to_add.append(RpiSensor(config, record, RpiSensorType.RELATIVE_HUMIDITY, SensorDeviceClass.HUMIDITY, PERCENTAGE))
    if RpiSensorType.PRESSURE in record:
        entities_to_add.append(RpiSensor(config, record, RpiSensorType.PRESSURE, SensorDeviceClass.PRESSURE,UnitOfPressure.HPA))
    if RpiSensorType.TEMPERATURE in record:
        entities_to_add.append(RpiSensor(config, record, RpiSensorType.TEMPERATURE, SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS))
    if RpiSensorType.CPU_TEMPERATURE in record:
        entities_to_add.append(RpiSensor(config, record, RpiSensorType.CPU_TEMPERATURE, SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS))
    if RpiSensorType.DISTANCE in record:
        entities_to_add.append(RpiSensor(config, record, RpiSensorType.DISTANCE, None, UnitOfLength.MILLIMETERS))
    if RpiSensorType.CONDUCTIVITY in record:
        entities_to_add.append(RpiSensor(config, record, RpiSensorType.CONDUCTIVITY, None, record["conductivity-unit"]))
    if RpiSensorType.PH in record:
        entities_to_add.append(RpiSensor(config, record, RpiSensorType.PH, None, ""))
    if len(entities_to_add) > 0:
        add_entities(entities_to_add)


class RpiSensor (SensorEntity):
    alt_type_names = {RpiSensorType.RELATIVE_HUMIDITY: SensorDeviceClass.HUMIDITY}

    @classmethod
    def get_type_name(cls, type_name):
        return (cls.alt_type_names[type_name] if type_name in cls.alt_type_names else type_name).capitalize()

    @staticmethod
    def api(host, fallback, refresh_interval):
        # the sensor api we will call to get data
        result = fallback
        try:
            now = datetime.timestamp(datetime.now()) * 1000
            if (now - fallback[SensorDeviceClass.TIMESTAMP]) > refresh_interval:
                url = f"http://{host}/sensor/now.json"
                req = request.Request(url)
                with request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
        except URLError as error:
            _LOGGER.error(f"Unable to retrieve data from Sensor host ({host}): {error.reason}")
        return result

    def __init__(self, config, record, type_name, device_class, unit_of_measurement):
        _LOGGER.debug(f"Adding '{type_name}' sensor from host: ({config[CONF_HOST]})")

        self._attr_name = f"{config[CONF_NAME]} {RpiSensor.get_type_name(type_name)}"
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._host = config[CONF_HOST]
        self._attr_unique_id = f"{config[CONF_HOST]}_{config[CONF_NAME]}_{RpiSensor.get_type_name(type_name)}".capitalize()
        self._type_name = type_name
        self._record = record
        self.update()

    def update(self):
        record = RpiSensor.api(self._host, self._record, DATA_REFRESH_INTERVAL_MS)
        if (record is not None) and (self._type_name in record):
            self._attr_native_value = record[self._type_name]
        self._record = record
