from abc import ABC, abstractmethod


class Entity(ABC):
    VALUE = "value"
    LAST_UPDATED = "last_updated"
    LAST_CHANGED = "last_changed"
    RANGE = "range"
    STATES = "states"
    DRIVER = "driver"
    REPORT = "report"

    def __init__(self, entity:dict):
        self._entity = entity

    @property
    def value(self) -> str | int | float | bool:
        return self._entity[Entity.VALUE]

    @property
    def report(self) -> bool:
        return self._entity[Entity.REPORT]

    @abstractmethod
    def update(self) -> bool:
        pass

    def updateValue(self, value: str | int | float | bool) -> bool:
        # store the last updated timestamp

        # check if the value actually changed
        if value != self.value:
            # store the updated value

            # store the last changed timestamp
            return True
        return False

class Control(Entity):
    def __init__(self, entity:dict):
        super().__init__(entity)

    """
    return true if the value is changed
    """
    @abstractmethod
    def set(self, value: str | int | float | bool) -> bool:
        pass

    def update(self) -> bool:
        return False
