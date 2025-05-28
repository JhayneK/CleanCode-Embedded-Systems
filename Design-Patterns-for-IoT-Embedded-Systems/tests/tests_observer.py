import os
import sys
import pytest
from unittest.mock import patch, MagicMock, Mock, call
import io
import time

# Adicionando os caminhos necessários para importação
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

if src_dir not in sys.path:
    sys.path.append(src_dir)

# Importando os módulos a serem testados
from src.devices import Device, AIDevicePublisher, DODevice

# Marcadores específicos para testes do padrão Observer
pytestmark = [pytest.mark.unit, pytest.mark.devices, pytest.mark.observer]

# Implementação simplificada do Subscriber para testes
class SimpleSubscriber:
    def __init__(self, name):
        self.name = name
        self.notifications = []
        self.last_value = None
        
    def update(self, subject):
        notification = f"Notificação para {self.name}: {subject.tag} mudou para {subject.value} {subject.unit}"
        self.notifications.append(notification)
        self.last_value = subject.value

# Fixtures para os testes
@pytest.fixture
def ai_device():
    """Cria um dispositivo AI para teste."""
    return AIDevicePublisher(
        tag="A1-AI-TIT01",
        area="Área 1",
        descricao="Sensor de Temperatura",
        range_min=0,
        range_max=100,
        unit="°C"
    )

@pytest.fixture
def subscribers():
    """Cria múltiplos subscribers reais para teste."""
    return [
        SimpleSubscriber(f"Subscriber{i}")
        for i in range(1, 4)
    ]

# Testes de integração para o padrão Observer
class TestObserverPattern:
    """Testes focados na implementação do padrão Observer."""
    
    def test_attach_detach_subscribers(self, ai_device, subscribers):
        """Testa a adição e remoção de subscribers."""
        # Inicialmente, não há subscribers
        assert len(ai_device.subscribers) == 0
        
        # Adiciona todos os subscribers
        for subscriber in subscribers:
            ai_device.attach(subscriber)
            
        # Verifica se todos foram adicionados
        assert len(ai_device.subscribers) == 3
        for subscriber in subscribers:
            assert subscriber in ai_device.subscribers
        
        # Remove um subscriber específico
        ai_device.detach(subscribers[1])
        
        # Verifica se foi removido corretamente
        assert len(ai_device.subscribers) == 2
        assert subscribers[1] not in ai_device.subscribers
        assert subscribers[0] in ai_device.subscribers
        assert subscribers[2] in ai_device.subscribers
    
    def test_notify_chain(self, ai_device, subscribers):
        """Testa a cadeia de notificações para todos os subscribers."""
        # Adiciona todos os subscribers
        for subscriber in subscribers:
            ai_device.attach(subscriber)
        
        # Atualiza o valor do dispositivo
        ai_device.update_value(25.5)
        
        # Verifica se todos os subscribers foram notificados
        for subscriber in subscribers:
            assert len(subscriber.notifications) == 1
            assert subscriber.last_value == 25.5
            assert f"{ai_device.tag} mudou para {ai_device.value} {ai_device.unit}" in subscriber.notifications[0]
    
    def test_selective_notification(self, ai_device, subscribers):
        """Testa a notificação seletiva de subscribers."""
        # Adiciona apenas o primeiro e o terceiro subscriber
        ai_device.attach(subscribers[0])
        ai_device.attach(subscribers[2])
        
        # Atualiza o valor do dispositivo
        ai_device.update_value(30.0)
        
        # Verifica se apenas os subscribers adicionados foram notificados
        assert len(subscribers[0].notifications) == 1
        assert len(subscribers[1].notifications) == 0  # Não adicionado, não deve ser notificado
        assert len(subscribers[2].notifications) == 1
        
        # Verifica os valores recebidos
        assert subscribers[0].last_value == 30.0
        assert subscribers[1].last_value is None  # Não recebeu notificação
        assert subscribers[2].last_value == 30.0
    
    def test_multiple_updates(self, ai_device, subscribers):
        """Testa múltiplas atualizações de valores e notificações."""
        # Adiciona todos os subscribers
        for subscriber in subscribers:
            ai_device.attach(subscriber)
        
        # Atualiza o valor várias vezes
        test_values = [10.0, 20.0, 30.0, 40.0, 50.0]
        for value in test_values:
            ai_device.update_value(value)
        
        # Verifica se todos os subscribers receberam todas as notificações
        for subscriber in subscribers:
            assert len(subscriber.notifications) == len(test_values)
            assert subscriber.last_value == test_values[-1]
            
            # Verifica se as notificações foram recebidas na ordem correta
            for i, value in enumerate(test_values):
                assert f"mudou para {value}" in subscriber.notifications[i]
    
    def test_detach_during_notification(self, ai_device, subscribers):
        """Testa a remoção de um subscriber durante o ciclo de notificação."""
        # Implementa um subscriber especial que se remove após ser notificado
        class SelfRemovingSubscriber:
            def __init__(self, name, device):
                self.name = name
                self.device = device
                self.notifications = []
                self.last_value = None
                
            def update(self, subject):
                notification = f"Notificação para {self.name}: {subject.tag} mudou para {subject.value} {subject.unit}"
                self.notifications.append(notification)
                self.last_value = subject.value
                # Remove a si mesmo após receber a notificação
                self.device.detach(self)
        
        # Cria um subscriber que se remove
        self_removing = SelfRemovingSubscriber("AutoRemove", ai_device)
        
        # Adiciona todos os subscribers, incluindo o que se remove
        ai_device.attach(subscribers[0])
        ai_device.attach(self_removing)
        ai_device.attach(subscribers[1])
        
        # Verifica o estado inicial
        assert len(ai_device.subscribers) == 3
        
        # Atualiza o valor
        ai_device.update_value(25.5)
        
        # Verifica se o subscriber se removeu
        assert len(ai_device.subscribers) == 2
        assert self_removing not in ai_device.subscribers
        
        # Verifica se todos receberam a primeira notificação
        assert len(subscribers[0].notifications) == 1
        assert len(self_removing.notifications) == 1
        assert len(subscribers[1].notifications) == 1
        
        # Atualiza o valor novamente
        ai_device.update_value(30.0)
        
        # Verifica se apenas os subscribers que permaneceram receberam a segunda notificação
        assert len(subscribers[0].notifications) == 2
        assert len(self_removing.notifications) == 1  # Não recebeu a segunda notificação
        assert len(subscribers[1].notifications) == 2
    
    def test_concurrent_attach_detach(self, ai_device, subscribers):
        """Testa operações concorrentes de attach e detach."""
        # Adiciona todos os subscribers
        for subscriber in subscribers:
            ai_device.attach(subscriber)
        
        # Simula operações concorrentes
        ai_device.attach(subscribers[0])  # Adiciona novamente (duplicidade)
        ai_device.detach(subscribers[1])  # Remove um subscriber
        
        # Atualiza o valor
        ai_device.update_value(25.5)
        
        # Verifica o estado dos subscribers
        assert len(ai_device.subscribers) == 3  # 3 iniciais + 1 duplicado - 1 removido = 3
        assert subscribers[0] in ai_device.subscribers
        assert subscribers[0] in ai_device.subscribers  # Pode aparecer duas vezes
        assert subscribers[1] not in ai_device.subscribers
        assert subscribers[2] in ai_device.subscribers
        
        # Verifica as notificações recebidas
        assert len(subscribers[0].notifications) >= 1  # Pode ter recebido múltiplas
        assert len(subscribers[1].notifications) == 0  # Foi removido
        assert len(subscribers[2].notifications) == 1  # Normal
    
    def test_performance_many_subscribers(self, ai_device):
        """Testa o desempenho com muitos subscribers."""
        # Cria um grande número de subscribers
        NUM_SUBSCRIBERS = 100
        many_subscribers = [SimpleSubscriber(f"Sub{i}") for i in range(NUM_SUBSCRIBERS)]
        
        # Adiciona todos os subscribers
        for subscriber in many_subscribers:
            ai_device.attach(subscriber)
        
        # Mede o tempo para notificar todos
        start_time = time.time()
        ai_device.update_value(25.5)
        end_time = time.time()
        
        # Verifica o tempo total e médio
        total_time = end_time - start_time
        avg_time = total_time / NUM_SUBSCRIBERS
        
        print(f"\nTempo total para notificar {NUM_SUBSCRIBERS} subscribers: {total_time:.6f}s")
        print(f"Tempo médio por subscriber: {avg_time*1000:.6f}ms")
        
        # Verifica se todos receberam a notificação
        for subscriber in many_subscribers:
            assert len(subscriber.notifications) == 1
            assert subscriber.last_value == 25.5
        
        # O limite depende da máquina, mas deve ser razoável
        assert avg_time < 0.001, f"Notificação muito lenta: {avg_time*1000:.6f}ms por subscriber"
    
    def test_exception_handling_in_subscriber(self, ai_device, subscribers, capsys):
        """Testa o tratamento de exceções em subscribers."""
        # Implementa um subscriber que lança exceção
        class ExceptionSubscriber:
            def __init__(self, name):
                self.name = name
                self.was_called = False
                
            def update(self, subject):
                self.was_called = True
                raise RuntimeError(f"Erro proposital em {self.name}")
        
        # Cria um subscriber com erro
        error_subscriber = ExceptionSubscriber("ErrorSub")
        
        # Adiciona os subscribers na ordem: normal, erro, normal
        ai_device.attach(subscribers[0])
        ai_device.attach(error_subscriber)
        ai_device.attach(subscribers[1])
        
        # Captura a saída stderr para verificar o erro
        with pytest.raises(RuntimeError):
            # Atualiza o valor - isso deve gerar a exceção
            ai_device.update_value(25.5)
        
        # Verifica se o subscriber com erro foi chamado
        assert error_subscriber.was_called is True
        
        # Verifica se os outros subscribers receberam notificação
        # Note: como há uma exceção, o fluxo de notificação é interrompido
        assert len(subscribers[0].notifications) == 1  # Notificado antes do erro
        assert len(subscribers[1].notifications) == 0  # Não notificado devido ao erro

    def test_empty_subscriber_list(self, ai_device):
        """Testa o comportamento com lista vazia de subscribers."""
        # Garante que a lista está vazia
        ai_device.subscribers = []
        
        # Atualiza o valor
        ai_device.update_value(25.5)
        
        # Verifica se o valor foi atualizado mesmo sem subscribers
        assert ai_device.value == 25.5
    
    def test_device_independence(self, subscribers):
        """Testa a independência entre diferentes dispositivos."""
        # Cria dois dispositivos
        device1 = AIDevicePublisher("A1-AI-TIT01", "Área 1", "Sensor 1", 0, 100, "°C")
        device2 = AIDevicePublisher("A1-AI-TIT02", "Área 1", "Sensor 2", 0, 100, "°C")
        
        # Adiciona subscribers diferentes a cada dispositivo
        device1.attach(subscribers[0])
        device1.attach(subscribers[1])
        device2.attach(subscribers[1])
        device2.attach(subscribers[2])
        
        # Atualiza os valores
        device1.update_value(25.5)
        device2.update_value(30.0)
        
        # Verifica as notificações
        assert len(subscribers[0].notifications) == 1  # Apenas do device1
        assert len(subscribers[1].notifications) == 2  # De ambos os devices
        assert len(subscribers[2].notifications) == 1  # Apenas do device2
        
        # Verifica os valores
        assert "A1-AI-TIT01" in subscribers[0].notifications[0]
        assert "25.5" in subscribers[0].notifications[0]
        
        assert "A1-AI-TIT01" in subscribers[1].notifications[0]
        assert "25.5" in subscribers[1].notifications[0]
        assert "A1-AI-TIT02" in subscribers[1].notifications[1]
        assert "30.0" in subscribers[1].notifications[1]
        
        assert "A1-AI-TIT02" in subscribers[2].notifications[0]
        assert "30.0" in subscribers[2].notifications[0]

if __name__ == "__main__":
    # Executa os testes
    pytest.main(["-v", __file__])