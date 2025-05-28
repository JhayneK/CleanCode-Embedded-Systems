# src/factories.py

from src.devices import DODevice

##################### classe DODeviceFactory ###################################################################################

class DODeviceFactory:
    def criar_device(self, tag, area, descricao):
        return DODevice(tag, area, descricao)

