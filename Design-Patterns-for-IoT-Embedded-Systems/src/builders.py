# src/builders.py

from src.devices import AIDevicePublisher


##################### classe AIDeviceBuilder ###################################################################################

class AIDeviceBuilder:
    def __init__(self):
        self._tag = None
        self._area = None
        self._descricao = None
        self._range_min = None
        self._range_max = None
        self._unit = None

    def set_tag(self, tag):
        self._tag = tag
        return self

    def set_area(self, area):
        self._area = area
        return self

    def set_descricao(self, descricao):
        self._descricao = descricao
        return self

    def set_range_min(self, range_min):
        self._range_min = range_min
        return self

    def set_range_max(self, range_max):
        self._range_max = range_max
        return self

    def set_unit(self, unit):
        self._unit = unit
        return self

    def build(self):
        return AIDevicePublisher(self._tag, self._area, self._descricao, self._range_min, self._range_max, self._unit)
