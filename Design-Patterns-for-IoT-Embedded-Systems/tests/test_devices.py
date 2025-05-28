import os
import sys
import pytest
from unittest.mock import patch, MagicMock, Mock, call

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

# Marcador para testes unitários de dispositivos
pytestmark = [pytest.mark.unit, pytest.mark.devices]

# Fixtures para os testes
@pytest.fixture
def basic_device():
    """Cria um dispositivo básico para teste."""
    return Device(
        tag="A1-DI-TEST01",
        area="Área 1",
        descricao="Dispositivo de Teste",
        tipo="DI"
    )

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
def do_device():
    """Cria um dispositivo DO para teste."""
    return DODevice(
        tag="A1-DO-SOL01",
        area="Área 1",
        descricao="Solenoide de Controle"
    )

@pytest.fixture
def mock_subscriber():
    """Cria um subscriber mock para teste."""
    subscriber = MagicMock()
    subscriber.update = Mock()
    return subscriber

# Testes para a classe Device
class TestDevice:
    """Testes para a classe base Device."""
    
    def test_init(self, basic_device):
        """Testa a inicialização da classe Device."""
        assert basic_device.tag == "A1-DI-TEST01"
        assert basic_device.area == "Área 1"
        assert basic_device.descricao == "Dispositivo de Teste"
        assert basic_device.tipo == "DI"
    
    def test_repr(self, basic_device):
        """Testa a representação string da classe Device."""
        expected_repr = "Device(tag=A1-DI-TEST01, area=Área 1, descricao=Dispositivo de Teste, tipo=DI)"
        assert repr(basic_device) == expected_repr

# Testes para a classe AIDevicePublisher
class TestAIDevicePublisher:
    """Testes para a classe AIDevicePublisher."""
    
    def test_init(self, ai_device):
        """Testa a inicialização da classe AIDevicePublisher."""
        assert ai_device.tag == "A1-AI-TIT01"
        assert ai_device.area == "Área 1"
        assert ai_device.descricao == "Sensor de Temperatura"
        assert ai_device.tipo == "AI"  # Herdado da classe base
        assert ai_device.range_min == 0
        assert ai_device.range_max == 100
        assert ai_device.unit == "°C"
        assert ai_device.value is None
        assert ai_device.subscribers == []
    
    def test_attach(self, ai_device, mock_subscriber):
        """Testa o método attach para adicionar subscribers."""
        # Inicialmente, não há subscribers
        assert len(ai_device.subscribers) == 0
        
        # Adiciona um subscriber
        ai_device.attach(mock_subscriber)
        assert len(ai_device.subscribers) == 1
        assert mock_subscriber in ai_device.subscribers
        
        # Adiciona outro subscriber
        another_subscriber = MagicMock()
        ai_device.attach(another_subscriber)
        assert len(ai_device.subscribers) == 2
        assert another_subscriber in ai_device.subscribers
    
    def test_detach(self, ai_device, mock_subscriber):
        """Testa o método detach para remover subscribers."""
        # Primeiro, adiciona um subscriber
        ai_device.attach(mock_subscriber)
        assert mock_subscriber in ai_device.subscribers
        
        # Remove o subscriber
        ai_device.detach(mock_subscriber)
        assert mock_subscriber not in ai_device.subscribers
        assert len(ai_device.subscribers) == 0
    
    def test_notify(self, ai_device, mock_subscriber):
        """Testa o método notify para notificar subscribers."""
        # Adiciona um subscriber
        ai_device.attach(mock_subscriber)
        
        # Chama o método notify
        ai_device.notify()
        
        # Verifica se o método update do subscriber foi chamado com o dispositivo como argumento
        mock_subscriber.update.assert_called_once_with(ai_device)
    
    def test_notify_multiple_subscribers(self, ai_device):
        """Testa a notificação para múltiplos subscribers."""
        # Cria e adiciona múltiplos subscribers
        subscribers = [MagicMock() for _ in range(3)]
        for subscriber in subscribers:
            subscriber.update = Mock()
            ai_device.attach(subscriber)
        
        # Chama o método notify
        ai_device.notify()
        
        # Verifica se todos os subscribers foram notificados
        for subscriber in subscribers:
            subscriber.update.assert_called_once_with(ai_device)
    
    def test_update_value(self, ai_device, mock_subscriber, capsys):
        """Testa o método update_value para atualizar o valor e notificar."""
        # Adiciona um subscriber
        ai_device.attach(mock_subscriber)
        
        # Chama o método update_value com um novo valor
        ai_device.update_value(25.5)
        
        # Verifica se o valor foi atualizado
        assert ai_device.value == 25.5
        
        # Verifica se o subscriber foi notificado
        mock_subscriber.update.assert_called_once_with(ai_device)
        
        # Verifica a mensagem de log impressa
        captured = capsys.readouterr()
        assert f"Atualizando {ai_device.tag} com valor {ai_device.value} {ai_device.unit}" in captured.out
    
    def test_update_value_without_subscribers(self, ai_device, capsys):
        """Testa o método update_value sem subscribers."""
        # Chama o método update_value com um novo valor
        ai_device.update_value(30.0)
        
        # Verifica se o valor foi atualizado
        assert ai_device.value == 30.0
        
        # Verifica a mensagem de log impressa
        captured = capsys.readouterr()
        assert f"Atualizando {ai_device.tag} com valor {ai_device.value} {ai_device.unit}" in captured.out
    
    def test_repr(self, ai_device):
        """Testa a representação string da classe AIDevicePublisher."""
        # Define um valor para o dispositivo
        ai_device.value = 25.5
        
        expected_repr = (
            "AIDevicePublisher(tag=A1-AI-TIT01, area=Área 1, descricao=Sensor de Temperatura, "
            "range_min=0, range_max=100, unit=°C, value=25.5)"
        )
        assert repr(ai_device) == expected_repr

# Testes para a classe DODevice
class TestDODevice:
    """Testes para a classe DODevice."""
    
    def test_init(self, do_device):
        """Testa a inicialização da classe DODevice."""
        assert do_device.tag == "A1-DO-SOL01"
        assert do_device.area == "Área 1"
        assert do_device.descricao == "Solenoide de Controle"
        assert do_device.tipo == "DO"  # Definido no construtor
    
    def test_repr(self, do_device):
        """Testa a representação string da classe DODevice."""
        expected_repr = "DODevice(tag=A1-DO-SOL01, area=Área 1, descricao=Solenoide de Controle)"
        assert repr(do_device) == expected_repr

# Testes adicionais para cenários específicos
def test_subscriber_removal_error(ai_device):
    """Testa o erro ao tentar remover um subscriber que não existe."""
    non_existent_subscriber = MagicMock()
    
    # Tenta remover um subscriber que não existe
    with pytest.raises(ValueError):
        ai_device.detach(non_existent_subscriber)

def test_update_value_with_none(ai_device, mock_subscriber):
    """Testa a atualização do valor para None."""
    # Adiciona um subscriber
    ai_device.attach(mock_subscriber)
    
    # Define um valor inicial
    ai_device.value = 25.5
    
    # Atualiza o valor para None
    ai_device.update_value(None)
    
    # Verifica se o valor foi atualizado
    assert ai_device.value is None
    
    # Verifica se o subscriber foi notificado
    mock_subscriber.update.assert_called_once_with(ai_device)

def test_inheritance_hierarchy():
    """Testa a hierarquia de herança das classes."""
    # Verifica se AIDevicePublisher é subclasse de Device
    assert issubclass(AIDevicePublisher, Device)
    
    # Verifica se DODevice é subclasse de Device
    assert issubclass(DODevice, Device)
    
    # Cria instâncias
    ai_device = AIDevicePublisher("A1-AI-TIT01", "Área 1", "Sensor", 0, 100, "°C")
    do_device = DODevice("A1-DO-SOL01", "Área 1", "Solenoide")
    
    # Verifica se as instâncias são do tipo correto
    assert isinstance(ai_device, AIDevicePublisher)
    assert isinstance(ai_device, Device)
    assert isinstance(do_device, DODevice)
    assert isinstance(do_device, Device)

def test_device_attributes():
    """Testa os atributos das classes de dispositivos."""
    # Testa os atributos da classe Device
    assert hasattr(Device, '__init__')
    assert hasattr(Device, '__repr__')
    
    # Testa os atributos da classe AIDevicePublisher
    assert hasattr(AIDevicePublisher, '__init__')
    assert hasattr(AIDevicePublisher, '__repr__')
    assert hasattr(AIDevicePublisher, 'attach')
    assert hasattr(AIDevicePublisher, 'detach')
    assert hasattr(AIDevicePublisher, 'notify')
    assert hasattr(AIDevicePublisher, 'update_value')
    
    # Testa os atributos da classe DODevice
    assert hasattr(DODevice, '__init__')
    assert hasattr(DODevice, '__repr__')

def test_subscriber_interaction(ai_device):
    """Testa a interação completa com subscribers."""
    # Cria mock subscribers
    subscribers = [MagicMock() for _ in range(3)]
    for i, subscriber in enumerate(subscribers):
        subscriber.update = Mock()
        subscriber.name = f"Subscriber {i+1}"
    
    # Adiciona todos os subscribers
    for subscriber in subscribers:
        ai_device.attach(subscriber)
    
    # Atualiza o valor
    ai_device.update_value(25.5)
    
    # Verifica se todos foram notificados
    for subscriber in subscribers:
        subscriber.update.assert_called_once_with(ai_device)
    
    # Remove o primeiro subscriber
    ai_device.detach(subscribers[0])
    
    # Atualiza o valor novamente
    ai_device.update_value(30.0)
    
    # Verifica as chamadas ao método update
    # O primeiro subscriber só deve ter sido chamado uma vez (na primeira atualização)
    assert subscribers[0].update.call_count == 1
    
    # Os outros subscribers devem ter sido chamados duas vezes
    assert subscribers[1].update.call_count == 2
    assert subscribers[2].update.call_count == 2

def test_ai_device_value_range(ai_device):
    """Testa se os valores estão dentro dos limites definidos no dispositivo."""
    # Define uma função para verificar se o valor está dentro do range
    def is_in_range(value, min_val, max_val):
        return min_val <= value <= max_val
    
    # Atualiza o valor para algo dentro do range
    ai_device.update_value(50.0)
    assert is_in_range(ai_device.value, ai_device.range_min, ai_device.range_max) is True
    
    # Atualiza o valor para algo no limite inferior
    ai_device.update_value(0.0)
    assert is_in_range(ai_device.value, ai_device.range_min, ai_device.range_max) is True
    
    # Atualiza o valor para algo no limite superior
    ai_device.update_value(100.0)
    assert is_in_range(ai_device.value, ai_device.range_min, ai_device.range_max) is True
    
    # Atualiza o valor para algo abaixo do limite inferior
    ai_device.update_value(-10.0)
    assert is_in_range(ai_device.value, ai_device.range_min, ai_device.range_max) is False
    
    # Atualiza o valor para algo acima do limite superior
    ai_device.update_value(110.0)
    assert is_in_range(ai_device.value, ai_device.range_min, ai_device.range_max) is False

if __name__ == "__main__":
    # Executa os testes
    pytest.main(["-v", __file__])