import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Adicionar diretórios necessários ao path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

if src_dir not in sys.path:
    sys.path.append(src_dir)

# Importações dos módulos a serem testados
from src.builders import AIDeviceBuilder
from src.devices import AIDevicePublisher

# Marcador para testes unitários
pytestmark = pytest.mark.unit

# Fixture para o AIDeviceBuilder
@pytest.fixture
def ai_device_builder():
    """Retorna uma nova instância de AIDeviceBuilder para cada teste."""
    return AIDeviceBuilder()

# Mocking do AIDevicePublisher para testes independentes
@pytest.fixture
def mock_ai_device_publisher(monkeypatch):
    """Mock para a classe AIDevicePublisher."""
    mock_device = MagicMock(spec=AIDevicePublisher)
    
    # Mock para o construtor da classe AIDevicePublisher
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
    
    # Aplicar o mock
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    return mock_device

# Testes para o método set_tag
def test_set_tag(ai_device_builder):
    """Testa se o método set_tag atribui corretamente o valor e retorna o builder."""
    # Executa o método
    result = ai_device_builder.set_tag("A1-AI-TIT01")
    
    # Verifica se o valor foi atribuído corretamente
    assert ai_device_builder._tag == "A1-AI-TIT01"
    
    # Verifica se o método retorna o próprio builder (encadeamento)
    assert result is ai_device_builder

# Testes para o método set_area
def test_set_area(ai_device_builder):
    """Testa se o método set_area atribui corretamente o valor e retorna o builder."""
    # Executa o método
    result = ai_device_builder.set_area("Área 1")
    
    # Verifica se o valor foi atribuído corretamente
    assert ai_device_builder._area == "Área 1"
    
    # Verifica se o método retorna o próprio builder (encadeamento)
    assert result is ai_device_builder

# Testes para o método set_descricao
def test_set_descricao(ai_device_builder):
    """Testa se o método set_descricao atribui corretamente o valor e retorna o builder."""
    # Executa o método
    result = ai_device_builder.set_descricao("Sensor de Temperatura")
    
    # Verifica se o valor foi atribuído corretamente
    assert ai_device_builder._descricao == "Sensor de Temperatura"
    
    # Verifica se o método retorna o próprio builder (encadeamento)
    assert result is ai_device_builder

# Testes para o método set_range_min
def test_set_range_min(ai_device_builder):
    """Testa se o método set_range_min atribui corretamente o valor e retorna o builder."""
    # Executa o método
    result = ai_device_builder.set_range_min(0)
    
    # Verifica se o valor foi atribuído corretamente
    assert ai_device_builder._range_min == 0
    
    # Verifica se o método retorna o próprio builder (encadeamento)
    assert result is ai_device_builder

# Testes para o método set_range_max
def test_set_range_max(ai_device_builder):
    """Testa se o método set_range_max atribui corretamente o valor e retorna o builder."""
    # Executa o método
    result = ai_device_builder.set_range_max(100)
    
    # Verifica se o valor foi atribuído corretamente
    assert ai_device_builder._range_max == 100
    
    # Verifica se o método retorna o próprio builder (encadeamento)
    assert result is ai_device_builder

# Testes para o método set_unit
def test_set_unit(ai_device_builder):
    """Testa se o método set_unit atribui corretamente o valor e retorna o builder."""
    # Executa o método
    result = ai_device_builder.set_unit("°C")
    
    # Verifica se o valor foi atribuído corretamente
    assert ai_device_builder._unit == "°C"
    
    # Verifica se o método retorna o próprio builder (encadeamento)
    assert result is ai_device_builder

# Teste para o método build
def test_build(ai_device_builder, monkeypatch):
    """Testa se o método build cria corretamente um objeto AIDevicePublisher."""
    # Configurar o mock para AIDevicePublisher
    mock_device = MagicMock(spec=AIDevicePublisher)
    
    # Mock para o construtor
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        return None
    
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    # Configurar o builder com todos os valores
    ai_device_builder.set_tag("A1-AI-TIT01")
    ai_device_builder.set_area("Área 1")
    ai_device_builder.set_descricao("Sensor de Temperatura")
    ai_device_builder.set_range_min(0)
    ai_device_builder.set_range_max(100)
    ai_device_builder.set_unit("°C")
    
    # Executar o método build
    device = ai_device_builder.build()
    
    # Verificar se o dispositivo foi criado corretamente
    assert isinstance(device, AIDevicePublisher)
    assert device.tag == "A1-AI-TIT01"
    assert device.area == "Área 1"
    assert device.descricao == "Sensor de Temperatura"
    assert device.range_min == 0
    assert device.range_max == 100
    assert device.unit == "°C"

# Teste para fluxo completo usando encadeamento de métodos
def test_builder_fluent_interface(ai_device_builder, monkeypatch):
    """Testa o uso da interface fluente (encadeamento de métodos) do builder."""
    # Configurar o mock para AIDevicePublisher
    mock_device = MagicMock(spec=AIDevicePublisher)
    
    # Mock para o construtor
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        return None
    
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    # Usar o builder com encadeamento de métodos
    device = ai_device_builder \
        .set_tag("A1-AI-TIT01") \
        .set_area("Área 1") \
        .set_descricao("Sensor de Temperatura") \
        .set_range_min(0) \
        .set_range_max(100) \
        .set_unit("°C") \
        .build()
    
    # Verificar se o dispositivo foi criado corretamente
    assert isinstance(device, AIDevicePublisher)
    assert device.tag == "A1-AI-TIT01"
    assert device.area == "Área 1"
    assert device.descricao == "Sensor de Temperatura"
    assert device.range_min == 0
    assert device.range_max == 100
    assert device.unit == "°C"

# Teste para valores padrão
def test_builder_default_values(ai_device_builder, monkeypatch):
    """Testa a construção com valores padrão (atributos não configurados)."""
    # Configurar o mock para AIDevicePublisher
    mock_device = MagicMock(spec=AIDevicePublisher)
    
    # Mock para o construtor
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        return None
    
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    # Configurar apenas alguns atributos
    ai_device_builder.set_tag("A1-AI-TIT01")
    ai_device_builder.set_unit("°C")
    
    # Executar o método build
    device = ai_device_builder.build()
    
    # Verificar os valores configurados
    assert device.tag == "A1-AI-TIT01"
    assert device.unit == "°C"
    
    # Verificar os valores padrão (None)
    assert device.area is None
    assert device.descricao is None
    assert device.range_min is None
    assert device.range_max is None

# Teste para validação de tipos de entrada
def test_builder_input_types(ai_device_builder):
    """Testa se o builder aceita diferentes tipos de entrada."""
    # String para tag
    ai_device_builder.set_tag("A1-AI-TIT01")
    assert ai_device_builder._tag == "A1-AI-TIT01"
    
    # String para area
    ai_device_builder.set_area("Área 1")
    assert ai_device_builder._area == "Área 1"
    
    # String para descrição
    ai_device_builder.set_descricao("Sensor de Temperatura")
    assert ai_device_builder._descricao == "Sensor de Temperatura"
    
    # Int para range_min
    ai_device_builder.set_range_min(0)
    assert ai_device_builder._range_min == 0
    
    # Float para range_max
    ai_device_builder.set_range_max(100.5)
    assert ai_device_builder._range_max == 100.5
    
    # String para unit
    ai_device_builder.set_unit("°C")
    assert ai_device_builder._unit == "°C"

# Teste para reinicialização do builder após construção
def test_builder_reuse(ai_device_builder, monkeypatch):
    """Testa a reutilização do builder após a construção de um objeto."""
    # Configurar o mock para AIDevicePublisher
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        return None
    
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    # Primeiro uso do builder
    ai_device_builder \
        .set_tag("A1-AI-TIT01") \
        .set_area("Área 1") \
        .set_unit("°C")
    
    device1 = ai_device_builder.build()
    
    # Verificar primeiro dispositivo
    assert device1.tag == "A1-AI-TIT01"
    assert device1.area == "Área 1"
    assert device1.unit == "°C"
    
    # Segundo uso do builder (substituindo apenas alguns valores)
    ai_device_builder \
        .set_tag("A1-AI-TIT02") \
        .set_area("Área 2")
    
    device2 = ai_device_builder.build()
    
    # Verificar segundo dispositivo
    assert device2.tag == "A1-AI-TIT02"
    assert device2.area == "Área 2"
    assert device2.unit == "°C"  # Este valor permanece do primeiro uso

if __name__ == "__main__":
    # Executa os testes
    pytest.main(["-v", __file__])