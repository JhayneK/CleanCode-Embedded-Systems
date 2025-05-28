# src/observer.py

class Observer:
    def update(self, device):
        pass


class GenericSubscriber(Observer):
    def __init__(self, name):
        self.name = name
        self.notifications = []

    def update(self, device):
        if device.value is not None:
            message = f"Observer {self.name}: TAG = {device.tag} mudou para {device.value} {device.unit}"
            print(message)
            self.notifications.append(message)
        else:
            message = f"Observer {self.name}: TAG = {device.tag} recebeu um valor inválido."
            print(message)
            self.notifications.append(message)
