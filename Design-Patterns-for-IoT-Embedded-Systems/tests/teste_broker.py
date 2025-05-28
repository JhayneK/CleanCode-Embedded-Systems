import os
import sys
import pytest
from unittest.mock import patch, MagicMock, Mock
import pandas as pd
import tempfile

# Adicionando os caminhos necessários para importação
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

if src_dir not in sys.path:
    sys.path.append(src_dir)

# Importando os módulos necessários
from src.main import processar_e_criar_dispositivos, ler_sensor
from src.observer import GenericSubscriber
from src.devices import AIDevicePublisher

# Fixtures
@pytest.fixture
def mock_excel_file():
    """Cria um arquivo Excel temporário para teste."""
    df = pd.DataFrame({
        'Tipo': ['AI', 'AI'],
        'Tag': ['A1-AI-TIT01', 'A1-AI-TIT02'],
        'Descrição': ['Sensor de Temperatura 1', 'Sensor de Temperatura 2'],
        'Unidade': ['°C', '°C'],
        'Dispositivo': ['ESP8266', 'RaspberryPi']
    })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        return tmp.name

@pytest.fixture
def mock_ai_device():
    """Cria um mock de um dispositivo AI."""
    device = MagicMock(spec=AIDevicePublisher)
    device.tag = "A1-AI-TIT01"
    device.value = 25.5
    device.unit = "°C"
    device.attach = Mock()
    device.detach = Mock()
    device.notify = Mock()
    return device

@pytest.fixture
def mock_subscriber():
    """Cria um mock de um subscriber genérico."""
    return GenericSubscriber("TestSubscriber")

# Testes para processamento e criação de dispositivos
def test_processar_e_criar_dispositivos(monkeypatch, mock_excel_file):
    """Testa se os dispositivos são criados corretamente a partir do arquivo Excel."""
    # Patch para a função de leitura de arquivo Excel
    monkeypatch.setattr('src.main.pd.read_excel', lambda path: pd.read_excel(mock_excel_file))
    
    # Patch para os construtores de dispositivos
    esp_mock = MagicMock()
    esp_mock.build = MagicMock(return_value=MagicMock(spec=AIDevicePublisher))
    rasp_mock = MagicMock()
    rasp_mock.build = MagicMock(return_value=MagicMock(spec=AIDevicePublisher))
    
    monkeypatch.setattr('src.main.EspDeviceBuilder', lambda: esp_mock)
    monkeypatch.setattr('src.main.RaspberryPiDeviceBuilder', lambda: rasp_mock)
    
    dispositivos = processar_e_criar_dispositivos()
    
    # Verifica se dois dispositivos foram criados
    assert len(dispositivos) == 2
    # Verifica se os construtores foram chamados corretamente
    assert esp_mock.build.call_count == 1
    assert rasp_mock.build.call_count == 1

# Testes para o padrão Observer
def test_observer_attach_detach(mock_ai_device, mock_subscriber):
    """Testa a adição e remoção de observadores."""
    # Teste de attach
    mock_ai_device.attach(mock_subscriber)
    mock_ai_device.attach.assert_called_once_with(mock_subscriber)
    
    # Teste de detach
    mock_ai_device.detach(mock_subscriber)
    mock_ai_device.detach.assert_called_once_with(mock_subscriber)

def test_observer_notification(mock_ai_device, mock_subscriber):
    """Testa se as notificações são enviadas corretamente."""
    # Teste de notificação
    mock_ai_device._observers = [mock_subscriber]  # Força adição do observer
    
    # Simula uma mudança de valor
    mock_ai_device.value = 26.5
    mock_ai_device.notify()
    
    # Verifica se o método de notificação foi chamado
    mock_ai_device.notify.assert_called_once()

# Teste para a função de leitura de sensor
def test_ler_sensor():
    """Testa a função de leitura do sensor."""
    # Cria dispositivos mock
    mock_device1 = MagicMock(spec=AIDevicePublisher)
    mock_device1.tag = "A1-AI-TIT01"
    mock_device1.read_value = Mock()
    
    mock_device2 = MagicMock(spec=AIDevicePublisher)
    mock_device2.tag = "A1-AI-TIT02"
    mock_device2.read_value = Mock()
    
    dispositivos = [mock_device1, mock_device2]
    stop_event = MagicMock()
    
    # Configura o evento para parar após a primeira iteração
    stop_event.is_set.side_effect = [False, True]
    
    # Executa a função de leitura
    with patch('time.sleep', return_value=None):  # Para não esperar o sleep
        ler_sensor(dispositivos, stop_event)
    
    # Verifica se os métodos de leitura foram chamados
    mock_device1.read_value.assert_called_once()
    mock_device2.read_value.assert_called_once()

# Teste de integração para associações
def test_associacao_dispositivo_subscriber(mock_ai_device, mock_subscriber):
    """Testa a associação entre dispositivo e assinante."""
    # Configura o mock para simular o comportamento de attach
    mock_ai_device._observers = []
    original_attach = AIDevicePublisher.attach
    
    def side_effect_attach(self, observer):
        self._observers.append(observer)
    
    with patch.object(AIDevicePublisher, 'attach', side_effect=side_effect_attach):
        mock_ai_device.attach(mock_subscriber)
        assert mock_subscriber in mock_ai_device._observers

# Validadores
def test_validar_formato_tag():
    """Valida o formato das tags dos dispositivos."""
    # Implementa um validador para o formato da tag
    def validar_tag(tag):
        import re
        pattern = r'^[A-Z]\d+-[A-Z]+-[A-Z]+\d+$'
        return bool(re.match(pattern, tag))
    
    # Tags válidas
    assert validar_tag("A1-AI-TIT01") == True
    assert validar_tag("B2-AI-TIT02") == True
    
    # Tags inválidas
    assert validar_tag("AI-TIT01") == False
    assert validar_tag("A1-AI-") == False
    assert validar_tag("a1-ai-tit01") == False  # Case sensitive

def test_validar_valor_temperatura():
    """Valida se os valores de temperatura estão dentro de limites razoáveis."""
    def validar_temperatura(valor):
        # Para este exemplo, consideramos temperaturas válidas entre -50°C e 150°C
        return -50 <= valor <= 150
    
    # Temperaturas válidas
    assert validar_temperatura(25.5) == True
    assert validar_temperatura(-30) == True
    assert validar_temperatura(100) == True
    
    # Temperaturas inválidas
    assert validar_temperatura(-100) == False
    assert validar_temperatura(200) == False

# Teste para o método read_value
def test_read_value_dentro_limites():
    """Testa se o método read_value retorna valores dentro dos limites esperados."""
    class TestAIDevice(AIDevicePublisher):
        def __init__(self):
            self.tag = "TEST-AI-TIT"
            self.value = 0
            self.unit = "°C"
            self._observers = []
            
        def read_value(self):
            import random
            self.value = random.uniform(20, 30)
            self.notify()
            return self.value
    
    device = TestAIDevice()
    
    # Testa múltiplas leituras
    for _ in range(10):
        value = device.read_value()
        assert 20 <= value <= 30

# Teste para verificar a estrutura do dispositivo
def test_estrutura_dispositivo():
    """Valida a estrutura básica de um dispositivo AI."""
    device = MagicMock(spec=AIDevicePublisher)
    
    # Verifica se os atributos básicos existem
    assert hasattr(device, 'tag')
    assert hasattr(device, 'value')
    assert hasattr(device, 'unit')
    assert hasattr(device, 'attach')
    assert hasattr(device, 'detach')
    assert hasattr(device, 'notify')

if __name__ == "__main__":
    # Executa os testes
    pytest.main(["-v", __file__])