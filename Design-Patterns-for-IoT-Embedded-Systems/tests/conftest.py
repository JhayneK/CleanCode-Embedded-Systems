import os
import sys
import pytest
from unittest.mock import MagicMock
import pandas as pd
import tempfile

# Ajustar os caminhos para importações
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

if src_dir not in sys.path:
    sys.path.append(src_dir)

# Importações para fixtures globais
try:
    from src.observer import GenericSubscriber
    from src.devices import AIDevicePublisher
except ImportError:
    # Mocks para permitir testes mesmo sem as classes reais
    class GenericSubscriber:
        def __init__(self, name):
            self.name = name
            self.notifications = []
            
        def update(self, subject):
            message = f"Valor mudou para {subject.value}{subject.unit}"
            self.notifications.append(message)
    
    class AIDevicePublisher:
        def __init__(self):
            self._observers = []
            self.tag = ""
            self.value = 0
            self.unit = ""
            
        def attach(self, observer):
            if observer not in self._observers:
                self._observers.append(observer)
                
        def detach(self, observer):
            if observer in self._observers:
                self._observers.remove(observer)
                
        def notify(self):
            for observer in self._observers:
                observer.update(self)
                
        def read_value(self):
            # Método a ser sobrescrito pelas subclasses
            pass

# Fixtures compartilhadas entre todos os testes
@pytest.fixture(scope="session")
def sample_excel_file():
    """Cria um arquivo Excel temporário para teste que persiste na sessão."""
    df = pd.DataFrame({
        'Tipo': ['AI', 'AI', 'AI'],
        'Tag': ['A1-AI-TIT01', 'A1-AI-TIT02', 'A1-AI-TIT03'],
        'Descrição': ['Sensor de Temperatura 1', 'Sensor de Temperatura 2', 'Sensor de Temperatura 3'],
        'Unidade': ['°C', '°C', '°C'],
        'Dispositivo': ['ESP8266', 'RaspberryPi', 'ESP8266']
    })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        file_path = tmp.name
    
    yield file_path
    
    # Limpeza após a execução dos testes
    if os.path.exists(file_path):
        os.unlink(file_path)

@pytest.fixture
def mock_ai_device():
    """Cria um mock de um dispositivo AI para uso nos testes."""
    device = MagicMock(spec=AIDevicePublisher)
    device.tag = "A1-AI-TIT01"
    device.value = 25.5
    device.unit = "°C"
    device._observers = []
    
    # Mock dos métodos
    original_attach = AIDevicePublisher.attach
    original_detach = AIDevicePublisher.detach
    original_notify = AIDevicePublisher.notify
    
    def mock_attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def mock_detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)
    
    def mock_notify(self):
        for observer in self._observers:
            observer.update(self)
    
    device.attach = lambda observer: mock_attach(device, observer)
    device.detach = lambda observer: mock_detach(device, observer)
    device.notify = lambda: mock_notify(device)
    device.read_value = MagicMock(return_value=device.value)
    
    return device

@pytest.fixture
def mock_device_list():
    """Cria uma lista de dispositivos mock para testes."""
    devices = []
    
    # Dispositivo 1
    device1 = MagicMock(spec=AIDevicePublisher)
    device1.tag = "A1-AI-TIT01"
    device1.value = 25.5
    device1.unit = "°C"
    device1._observers = []
    device1.read_value = MagicMock(return_value=25.5)
    device1.attach = MagicMock()
    device1.detach = MagicMock()
    device1.notify = MagicMock()
    
    # Dispositivo 2
    device2 = MagicMock(spec=AIDevicePublisher)
    device2.tag = "A1-AI-TIT02"
    device2.value = 26.7
    device2.unit = "°C"
    device2._observers = []
    device2.read_value = MagicMock(return_value=26.7)
    device2.attach = MagicMock()
    device2.detach = MagicMock()
    device2.notify = MagicMock()
    
    devices.append(device1)
    devices.append(device2)
    
    return devices

@pytest.fixture
def mock_subscriber():
    """Cria um subscriber mock para testes."""
    subscriber = GenericSubscriber("TestSubscriber")
    return subscriber

@pytest.fixture
def mock_event():
    """Cria um evento mock para parar threads."""
    class MockEvent:
        def __init__(self):
            self.is_set_calls = 0
            self.set_called = False
        
        def is_set(self):
            # Retorna False na primeira chamada, True nas seguintes
            # Isso permite que loops executem exatamente uma vez
            if self.is_set_calls == 0:
                self.is_set_calls += 1
                return False
            return True
        
        def set(self):
            self.set_called = True
    
    return MockEvent()

@pytest.fixture
def streamlit_mock():
    """Cria um mock para o Streamlit para testes de interface."""
    class StreamlitMock:
        def __init__(self):
            self.session_state = {}
            self.items = []
            self.markdown_calls = []
            self.button_calls = []
            self.selectbox_calls = []
            self.columns_calls = []
            self.errors = []
            self.warnings = []
            self.infos = []
            self.success_msgs = []
        
        def title(self, text):
            self.items.append(('title', text))
        
        def header(self, text):
            self.items.append(('header', text))
        
        def subheader(self, text):
            self.items.append(('subheader', text))
        
        def markdown(self, text, **kwargs):
            self.markdown_calls.append((text, kwargs))
            self.items.append(('markdown', text, kwargs))
        
        def button(self, label, **kwargs):
            self.button_calls.append((label, kwargs))
            self.items.append(('button', label, kwargs))
            return kwargs.get('on_click', False)
        
        def selectbox(self, label, options, **kwargs):
            self.selectbox_calls.append((label, options, kwargs))
            self.items.append(('selectbox', label, options, kwargs))
            return options[0] if options else None
        
        def columns(self, widths):
            cols = []
            for _ in range(len(widths)):
                col_mock = StreamlitColumnMock()
                cols.append(col_mock)
            self.columns_calls.append(widths)
            self.items.append(('columns', widths, cols))
            return cols
        
        def error(self, msg):
            self.errors.append(msg)
            self.items.append(('error', msg))
        
        def warning(self, msg):
            self.warnings.append(msg)
            self.items.append(('warning', msg))
        
        def info(self, msg):
            self.infos.append(msg)
            self.items.append(('info', msg))
        
        def success(self, msg):
            self.success_msgs.append(msg)
            self.items.append(('success', msg))
        
        def text_input(self, label, **kwargs):
            self.items.append(('text_input', label, kwargs))
            return "Test Input"
        
        def write(self, *args):
            self.items.append(('write', args))
        
        def experimental_rerun(self):
            self.items.append(('experimental_rerun',))
        
        def stop(self):
            self.items.append(('stop',))
            
        def set_page_config(self, **kwargs):
            self.items.append(('set_page_config', kwargs))
    
    class StreamlitColumnMock:
        def __init__(self):
            self.items = []
        
        def markdown(self, text, **kwargs):
            self.items.append(('markdown', text, kwargs))
            return None
        
        def button(self, label, **kwargs):
            self.items.append(('button', label, kwargs))
            return False
        
        def write(self, text):
            self.items.append(('write', text))
            return None
    
    return StreamlitMock()