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
    CONF_NAME
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
    sensor_types = [
        "humidity",
        "temperature",
        "pressure",
        "distance",
        "ph",
        "conductivity",
        "cpu-temperature"
    ]

    sensor_subtypes = {
        "cpu-load": ["usr", "sys", "idle"],
        "memory": ["mem-total", "mem-used", "mem-free", "swap-total", "swap-used", "swap-used"]
    }

    # home assistant might already have device classes for some types we use, but they don't know
    # the names we use as those, so this is a simple mapping for our wierd classes
    ha_device_classes = {
        "cpu-temperature": SensorDeviceClass.TEMPERATURE,
        "memory": SensorDeviceClass.DATA_SIZE
    }


class RpiSensor (SensorEntity):
    @staticmethod
    def api(host, fallback, refresh_interval):
        # the sensor api we will call to get data
        result = fallback
        try:
            now = datetime.timestamp(datetime.now()) * 1000
            if (now - fallback["timestamp"]) > refresh_interval:
                url = f"http://{host}/sensor/now.json"
                req = request.Request(url)
                with request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
        except URLError as error:
            _LOGGER.error(f"Unable to retrieve data from Sensor host ({host}): {error.reason}")
        return result

    def __init__(self, config, record, sensor_type: str, sensor_subtype: str = ""):
        _LOGGER.debug(f"Adding '{sensor_type}'" + ("" if sensor_subtype == "" else f"-{sensor_subtype}") + " sensor from host: ({config[CONF_HOST]})")

        name = config[CONF_NAME]
        self._host = config[CONF_HOST]
        host = self._host.removesuffix(".local")
        self._attr_name = f"{name} {sensor_type}" + ("" if sensor_subtype == "" else f" {sensor_subtype}")
        self._attr_unique_id = (f"{host}_{name}_{sensor_type}" + ("" if sensor_subtype == "" else f"_{sensor_subtype}")).lower()

        self._attr_native_unit_of_measurement = record[sensor_type + "-unit"]
        self._attr_device_class = RpiSensorType.ha_device_classes.get(sensor_type, sensor_type)
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._sensor_type = sensor_type
        self._sensor_subtype = sensor_subtype
        self._record = record
        self.update()

    def update(self):
        record = RpiSensor.api(self._host, self._record, DATA_REFRESH_INTERVAL_MS)
        if (record is not None) and (self._sensor_type in record):
            if self._sensor_subtype == "":
                self._attr_native_value = record[self._sensor_type]
            else:
                self._attr_native_value = record[self._sensor_type][self._sensor_subtype]
        self._record = record


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    # get a sample record from the sensor to create the needed entities
    record = RpiSensor.api(config[CONF_HOST], {SensorDeviceClass.TIMESTAMP: 0}, 0)
    entities_to_add = []

    # add the root sensor types
    for sensor_type in RpiSensorType.sensor_types:
        if sensor_type in record:
            entities_to_add.append(RpiSensor(config, record, sensor_type))

    # add the sub sensor types
    for sensor_type in RpiSensorType.sensor_subtypes:
        if sensor_type in record:
            subrecord = record[sensor_type]
            for sensor_subtype in RpiSensorType.sensor_subtypes[sensor_type]:
                if sensor_subtype in subrecord:
                    entities_to_add.append(RpiSensor(config, record, sensor_type, sensor_subtype))

    if len(entities_to_add) > 0:
        add_entities(entities_to_add)
