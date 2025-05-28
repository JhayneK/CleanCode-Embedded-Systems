import os
import sys
import pytest
import time
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

# Marcadores específicos para testes de desempenho
pytestmark = [pytest.mark.performance, pytest.mark.builder]

# Fixtures
@pytest.fixture
def ai_device_builder():
    """Retorna uma nova instância de AIDeviceBuilder para cada teste."""
    return AIDeviceBuilder()

# Testes de validação de entradas extremas
@pytest.mark.parametrize("tag", [
    "A1-AI-TIT01",  # Tag normal
    "Z9-AI-TIT99",  # Tag extrema, mas válida
    "A" * 50 + "-AI-TIT01",  # Tag muito longa
    "",  # Tag vazia
    None,  # Tag None
])
def test_builder_tag_robustness(ai_device_builder, tag, monkeypatch):
    """Testa a robustez do builder com diferentes tipos de tags."""
    # Mock para impedir erros no construtor de AIDevicePublisher
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        return None
    
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    # Testa o método set_tag
    if tag is None:
        # Para valores None, esperamos um AttributeError
        with pytest.raises(AttributeError):
            ai_device_builder.set_tag(tag)
    else:
        # Para outros valores, esperamos que funcione normalmente
        ai_device_builder.set_tag(tag)
        assert ai_device_builder._tag == tag
        
        # Testa a construção do dispositivo
        device = ai_device_builder.build()
        assert device.tag == tag

@pytest.mark.parametrize("range_value", [
    0,  # Valor normal
    -100,  # Valor negativo
    1000,  # Valor positivo grande
    0.5,  # Valor decimal
    "10",  # String numérica
    "abc",  # String não numérica
    None,  # None
])
def test_builder_range_robustness(ai_device_builder, range_value, monkeypatch):
    """Testa a robustez do builder com diferentes tipos de valores de range."""
    # Mock para impedir erros no construtor de AIDevicePublisher
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        return None
    
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    # Configura os valores básicos para o builder
    ai_device_builder.set_tag("A1-AI-TIT01")
    
    # Testa os métodos de range
    try:
        ai_device_builder.set_range_min(range_value)
        assert ai_device_builder._range_min == range_value
        
        ai_device_builder.set_range_max(range_value)
        assert ai_device_builder._range_max == range_value
        
        # Testa a construção do dispositivo
        device = ai_device_builder.build()
        assert device.range_min == range_value
        assert device.range_max == range_value
    except Exception as e:
        # Se estamos testando com valores que devem causar exceções,
        # registramos isso, mas não falhamos o teste
        if range_value in ["abc", None]:
            pytest.xfail(f"Falha esperada para valor {range_value}: {str(e)}")
        else:
            # Se não esperávamos uma exceção, propagamos o erro
            raise

# Teste de desempenho
def test_builder_performance(ai_device_builder, monkeypatch):
    """Teste de desempenho para o padrão Builder."""
    # Mock para AIDevicePublisher
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        return None
    
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    # Medição de tempo para criação de múltiplas instâncias
    start_time = time.time()
    
    # Cria 1000 instâncias usando o builder
    NUM_INSTANCES = 1000
    for i in range(NUM_INSTANCES):
        device = ai_device_builder \
            .set_tag(f"A1-AI-TIT{i:02d}") \
            .set_area(f"Área {i}") \
            .set_descricao(f"Sensor de Temperatura {i}") \
            .set_range_min(0) \
            .set_range_max(100) \
            .set_unit("°C") \
            .build()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Verificar desempenho
    average_time = total_time / NUM_INSTANCES
    print(f"\nTempo total para criar {NUM_INSTANCES} instâncias: {total_time:.4f} segundos")
    print(f"Tempo médio por instância: {average_time*1000:.4f} ms")
    
    # A tolerância depende da máquina de teste, mas é um ponto de referência
    assert average_time < 0.001, f"Construção muito lenta: {average_time*1000:.4f} ms por instância"

# Teste para padrões extremos de uso do Builder
def test_builder_extreme_patterns(ai_device_builder, monkeypatch):
    """Testa padrões extremos de uso do Builder."""
    # Mock para AIDevicePublisher
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        return None
    
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    # Teste 1: Configurar o mesmo atributo várias vezes
    device = ai_device_builder \
        .set_tag("A1-AI-TIT01") \
        .set_tag("A1-AI-TIT02") \
        .set_tag("A1-AI-TIT03") \
        .build()
    
    assert device.tag == "A1-AI-TIT03"  # Deve usar o último valor definido
    
    # Teste 2: Chamar build múltiplas vezes
    ai_device_builder.set_tag("A1-AI-TIT04")
    device1 = ai_device_builder.build()
    device2 = ai_device_builder.build()
    
    assert device1.tag == "A1-AI-TIT04"
    assert device2.tag == "A1-AI-TIT04"
    assert device1 is not device2  # Devem ser instâncias diferentes
    
    # Teste 3: Encadeamento extremo (embora não mude nada)
    device = ai_device_builder \
        .set_tag("A1-AI-TIT05") \
        .set_tag("A1-AI-TIT05") \
        .set_area("Área") \
        .set_area("Área") \
        .set_descricao("Descricao") \
        .set_descricao("Descricao") \
        .set_range_min(0) \
        .set_range_min(0) \
        .set_range_max(100) \
        .set_range_max(100) \
        .set_unit("°C") \
        .set_unit("°C") \
        .build()
    
    assert device.tag == "A1-AI-TIT05"
    assert device.area == "Área"
    assert device.descricao == "Descricao"
    assert device.range_min == 0
    assert device.range_max == 100
    assert device.unit == "°C"

# Teste para verificar a independência das instâncias
def test_builder_instance_independence(monkeypatch):
    """Testa a independência entre várias instâncias do builder."""
    # Mock para AIDevicePublisher
    def mock_init(self, tag, area, descricao, range_min, range_max, unit):
        self.tag = tag
        self.area = area
        self.descricao = descricao
        self.range_min = range_min
        self.range_max = range_max
        self.unit = unit
        return None
    
    monkeypatch.setattr(AIDevicePublisher, '__init__', mock_init)
    
    # Criar dois builders separados
    builder1 = AIDeviceBuilder()
    builder2 = AIDeviceBuilder()
    
    # Configurar o primeiro builder
    builder1.set_tag("A1-AI-TIT01")
    builder1.set_unit("°C")
    
    # Configurar o segundo builder
    builder2.set_tag("A2-AI-TIT02")
    builder2.set_unit("°F")
    
    # Verificar se as configurações estão independentes
    assert builder1._tag == "A1-AI-TIT01"
    assert builder1._unit == "°C"
    assert builder2._tag == "A2-AI-TIT02"
    assert builder2._unit == "°F"
    
    # Construir os dispositivos
    device1 = builder1.build()
    device2 = builder2.build()
    
    # Verificar a independência dos dispositivos criados
    assert device1.tag == "A1-AI-TIT01"
    assert device1.unit == "°C"
    assert device2.tag == "A2-AI-TIT02"
    assert device2.unit == "°F"

if __name__ == "__main__":
    # Executa os testes
    pytest.main(["-v", __file__])