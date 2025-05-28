# src/devices.py


##################### Superclasse Device ###################################################################################

class Device:
    def __init__(self, tag, area, descricao, tipo):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.tipo = tipo

    def __repr__(self):
        return f"Device(tag={self.tag}, area={self.area}, descricao={self.descricao}, tipo={self.tipo})"


##################### Subclasse AI Device ###################################################################################

class AIDevicePublisher(Device):
    def __init__(self, tag, area, descricao, range_min, range_max, unit):
        super().__init__(tag, area, descricao, "AI")
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        self.value = None  # Valor atual
        self.subscribers = []  # Lista de observadores #subscriber

    def attach(self, subscriber):
        self.subscribers.append(subscriber) # Adiciona observador

    def detach(self, subscriber):
        self.subscribers.remove(subscriber) # Remove observador

    def notify(self):
        for subscriber in self.subscribers:
            subscriber.update(self)  # Notifica observadores

    def update_value(self, new_value):
        self.value = new_value # Atualiza valor
        print(f"Atualizando {self.tag} com valor {self.value} {self.unit}")
        self.notify()  # Notifica os inscritos

    def __repr__(self):
        return (f"AIDevicePublisher(tag={self.tag}, area={self.area}, descricao={self.descricao}, "
                f"range_min={self.range_min}, range_max={self.range_max}, unit={self.unit}, value={self.value})")



##################### Subclasse DO Device ###################################################################################

class DODevice(Device):
    def __init__(self, tag, area, descricao):
        super().__init__(tag, area, descricao, "DO")

    def __repr__(self):
        return f"DODevice(tag={self.tag}, area={self.area}, descricao={self.descricao})"
