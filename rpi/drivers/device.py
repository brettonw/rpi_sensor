from abc import ABC, abstractmethod
import json
from switch import Switch
from entity import Entity


class Device:
    DEVICE_NAME = "device"
    ENTITIES = "entities"

    # TODO could this be build dynamically?
    drivers = {
        "switch": lambda entity : Switch(entity),
    }

    def __init__(self, path:str):
        # save the path for the device schema and the drivers
        self._path = path
        self._data = Device.load_from_path (path)
        self._entities = []
        for entity in self._data[Device.ENTITIES]:
            self._entities.append (Device.drivers[entity[Entity.DRIVER]] ())

    @staticmethod
    def load_from_path(path: str) -> dict:
        # read the JSON file
        f = open(path)
        result = json.load(f)
        f.close()
        return result

    @staticmethod
    def save_to_path(path:str):
        pass

    def get(self):

        pass

    def update(self):
        # if anything changed, save out the schema
        pass

    def set(self, entity:str, value: str | int | float):
        # if anything changed, save out the schema
        pass
