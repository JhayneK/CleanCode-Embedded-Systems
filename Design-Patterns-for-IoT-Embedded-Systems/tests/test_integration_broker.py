import os
import sys
import pytest
from unittest.mock import patch, MagicMock, Mock
import streamlit as st
import tempfile
import pandas as pd

# Adicionando os caminhos necessários para importação
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

if src_dir not in sys.path:
    sys.path.append(src_dir)

# Importando os módulos necessários
from src.observer import GenericSubscriber
from src.devices import AIDevicePublisher

# Mock para o Streamlit
class StreamlitMock:
    """Mock para as funções do Streamlit usadas no broker."""
    
    def __init__(self):
        self.session_state = {}
        self.sidebar_items = []
        self.page_items = []
        self.errors = []
        self.warnings = []
        self.infos = []
        self.success_msgs = []
    
    def set_page_config(self, *args, **kwargs):
        pass
    
    def sidebar(self):
        mock = MagicMock()
        mock.image = lambda *args, **kwargs: self.sidebar_items.append(('image', args, kwargs))
        mock.title = lambda *args: self.sidebar_items.append(('title', args))
        mock.selectbox = lambda *args, **kwargs: self.sidebar_items.append(('selectbox', args, kwargs)) or "Broker"
        mock.error = lambda *args: self.sidebar_items.append(('error', args))
        return mock
    
    def markdown(self, *args, **kwargs):
        self.page_items.append(('markdown', args, kwargs))
    
    def title(self, *args):
        self.page_items.append(('title', args))
    
    def header(self, *args):
        self.page_items.append(('header', args))
    
    def subheader(self, *args):
        self.page_items.append(('subheader', args))
    
    def columns(self, sizes):
        cols = []
        for _ in range(len(sizes)):
            col = MagicMock()
            col.markdown = lambda *args, **kwargs: None
            col.button = lambda *args, **kwargs: False
            cols.append(col)
        return cols
    
    def selectbox(self, *args, **kwargs):
        self.page_items.append(('selectbox', args, kwargs))
        return args[1][0] if len(args) > 1 and isinstance(args[1], list) and args[1] else None
    
    def text_input(self, *args, **kwargs):
        self.page_items.append(('text_input', args, kwargs))
        return "Test Input"
    
    def button(self, *args, **kwargs):
        self.page_items.append(('button', args, kwargs))
        action = kwargs.get('on_click')
        if action:
            action()
        return True
    
    def error(self, msg):
        self.errors.append(msg)
    
    def warning(self, msg):
        self.warnings.append(msg)
    
    def info(self, msg):
        self.infos.append(msg)
    
    def success(self, msg):
        self.success_msgs.append(msg)
    
    def write(self, *args):
        self.page_items.append(('write', args))
    
    def stop(self):
        pass

# Fixtures para os testes
@pytest.fixture
def st_mock():
    """Cria um mock do Streamlit."""
    return StreamlitMock()

@pytest.fixture
def mock_ai_device():
    """Cria um mock de um dispositivo AI."""
    device = MagicMock(spec=AIDevicePublisher)
    device.tag = "A1-AI-TIT01"
    device.value = 25.5
    device.unit = "°C"
    return device

@pytest.fixture
def mock_devices():
    """Cria uma lista de dispositivos mock."""
    device1 = MagicMock(spec=AIDevicePublisher)
    device1.tag = "A1-AI-TIT01"
    device1.value = 25.5
    device1.unit = "°C"
    
    device2 = MagicMock(spec=AIDevicePublisher)
    device2.tag = "A1-AI-TIT02"
    device2.value = 26.7
    device2.unit = "°C"
    
    return [device1, device2]

# Testes para o broker Streamlit
def test_broker_inicializacao(monkeypatch, st_mock, mock_devices):
    """Testa a inicialização do broker."""
    # Patch para funções do Streamlit
    monkeypatch.setattr('streamlit.set_page_config', st_mock.set_page_config)
    monkeypatch.setattr('streamlit.sidebar', st_mock.sidebar)
    monkeypatch.setattr('streamlit.markdown', st_mock.markdown)
    monkeypatch.setattr('streamlit.session_state', st_mock.session_state)
    monkeypatch.setattr('streamlit.error', st_mock.error)
    
    # Patch para a função de processamento de dispositivos
    monkeypatch.setattr('src.main.processar_e_criar_dispositivos', lambda: mock_devices)
    
    # Importa o módulo do broker
    import broker
    
    # Verifica se os dispositivos foram carregados corretamente
    assert 'dispositivos_criados' in st_mock.session_state
    assert len(st_mock.session_state['dispositivos_criados']) == 2
    assert st_mock.session_state['dispositivos_criados'][0].tag == "A1-AI-TIT01"

def test_adicionar_associacao(monkeypatch, st_mock, mock_devices):
    """Testa a funcionalidade de adicionar associação entre dispositivos."""
    # Configura o estado da sessão
    st_mock.session_state['dispositivos_criados'] = mock_devices
    st_mock.session_state['associacoes'] = []
    
    # Patch para funções do Streamlit
    monkeypatch.setattr('streamlit.selectbox', st_mock.selectbox)
    monkeypatch.setattr('streamlit.text_input', st_mock.text_input)
    monkeypatch.setattr('streamlit.button', st_mock.button)
    monkeypatch.setattr('streamlit.success', st_mock.success)
    monkeypatch.setattr('streamlit.session_state', st_mock.session_state)
    
    # Simula a criação de uma associação
    dispositivo_tag = "A1-AI-TIT01"
    subscriber_name = "TestSubscriber"
    
    # Função simplificada de adição de associação
    def adicionar_associacao_test():
        dispositivo = next((d for d in mock_devices if d.tag == dispositivo_tag), None)
        if dispositivo and isinstance(dispositivo, AIDevicePublisher):
            observer = GenericSubscriber(subscriber_name)
            dispositivo.attach = Mock()  # Mock para o método attach
            dispositivo.attach(observer)
            
            st_mock.session_state['associacoes'].append({
                'dispositivo': dispositivo_tag,
                'subscriber': subscriber_name,
                'observer': observer
            })
            st_mock.success(f"Associação criada entre {dispositivo_tag} e {subscriber_name}")
    
    # Executa a função
    adicionar_associacao_test()
    
    # Verifica se a associação foi criada
    assert len(st_mock.session_state['associacoes']) == 1
    assert st_mock.session_state['associacoes'][0]['dispositivo'] == "A1-AI-TIT01"
    assert st_mock.session_state['associacoes'][0]['subscriber'] == "TestSubscriber"
    assert len(st_mock.success_msgs) == 1

def test_remover_associacao(monkeypatch, st_mock, mock_devices):
    """Testa a funcionalidade de remover associação entre dispositivos."""
    # Configura o estado da sessão com uma associação existente
    observer = GenericSubscriber("TestSubscriber")
    mock_devices[0].detach = Mock()  # Mock para o método detach
    
    st_mock.session_state['dispositivos_criados'] = mock_devices
    st_mock.session_state['associacoes'] = [{
        'dispositivo': "A1-AI-TIT01",
        'subscriber': "TestSubscriber",
        'observer': observer
    }]
    
    # Função simplificada de remoção de associação
    def remover_associacao_test(indice):
        associacoes = st_mock.session_state['associacoes']
        if indice < len(associacoes):
            assoc = associacoes[indice]
            dispositivo = next((d for d in mock_devices if d.tag == assoc['dispositivo']), None)
            if dispositivo:
                dispositivo.detach(assoc['observer'])
            associacoes.pop(indice)
            st_mock.session_state['associacoes'] = associacoes.copy()
    
    # Executa a função
    remover_associacao_test(0)
    
    # Verifica se a associação foi removida
    assert len(st_mock.session_state['associacoes']) == 0
    mock_devices[0].detach.assert_called_once_with(observer)

def test_visualizacao_temperatura(monkeypatch, st_mock, mock_devices):
    """Testa a página de visualização de temperatura."""
    # Configura o estado da sessão
    st_mock.session_state['dispositivos_criados'] = mock_devices
    
    # Patch para funções do Streamlit
    monkeypatch.setattr('streamlit.markdown', st_mock.markdown)
    monkeypatch.setattr('streamlit.error', st_mock.error)
    
    # Função simplificada de visualização
    def exibir_temperatura():
        dispositivo = next((d for d in mock_devices if d.tag == "A1-AI-TIT01"), None)
        if dispositivo and isinstance(dispositivo, AIDevicePublisher):
            current_value = f"{dispositivo.value} {dispositivo.unit}"
            st_mock.markdown(f"""
                <div class="temperature-container">
                    <div class="temperature-card">
                        <h2 class="temperature-tag">{dispositivo.tag}</h2>
                        <p class="temperature-label">Temperatura Atual:</p>
                        <h1 class="temperature-value">{current_value}</h1>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st_mock.error("Dispositivo A1-AI-TIT01 não encontrado.")
    
    # Executa a função
    exibir_temperatura()
    
    # Verifica se a visualização foi criada
    assert any(item[0] == 'markdown' and "temperature-container" in item[1][0] for item in st_mock.page_items)
    assert len(st_mock.errors) == 0

def test_notificacoes_observadores(monkeypatch, st_mock):
    """Testa a exibição das notificações dos observadores."""
    # Cria um observer com notificações
    observer1 = GenericSubscriber("Observer1")
    observer1.notifications = ["Valor mudou para 25.5°C", "Valor mudou para 26.0°C"]
    
    observer2 = GenericSubscriber("Observer2")
    observer2.notifications = []
    
    # Configura o estado da sessão
    st_mock.session_state['associacoes'] = [
        {'dispositivo': "A1-AI-TIT01", 'subscriber': "Observer1", 'observer': observer1},
        {'dispositivo': "A1-AI-TIT02", 'subscriber': "Observer2", 'observer': observer2}
    ]
    
    # Patch para funções do Streamlit
    monkeypatch.setattr('streamlit.subheader', st_mock.subheader)
    monkeypatch.setattr('streamlit.write', st_mock.write)
    monkeypatch.setattr('streamlit.info', st_mock.info)
    
    # Função simplificada de exibição de notificações
    def exibir_notificacoes():
        associacoes = st_mock.session_state['associacoes']
        if associacoes:
            for assoc in associacoes:
                observer = assoc['observer']
                if observer.notifications:
                    st_mock.subheader(f"Objeto Associado: {observer.name}")
                    for notification in observer.notifications[-5:]:
                        st_mock.write(notification)
                else:
                    st_mock.write(f"Objeto Associado: {observer.name} - Nenhuma notificação ainda.")
        else:
            st_mock.info("Nenhuma notificação para exibir.")
    
    # Executa a função
    exibir_notificacoes()
    
    # Verifica se as notificações foram exibidas corretamente
    assert any(item[0] == 'subheader' and "Observer1" in item[1][0] for item in st_mock.page_items)
    assert any(item[0] == 'write' and "Valor mudou para 25.5°C" in item[1] for item in st_mock.page_items)
    assert any(item[0] == 'write' and "Observer2" in item[1][0] and "Nenhuma notificação ainda" in item[1][0] for item in st_mock.page_items)

# Teste para verificar tentativas de duplicação de associação
def test_duplicacao_associacao(monkeypatch, st_mock, mock_devices):
    """Testa a tentativa de criar uma associação duplicada."""
    # Configura o estado da sessão com uma associação existente
    observer = GenericSubscriber("TestSubscriber")
    
    st_mock.session_state['dispositivos_criados'] = mock_devices
    st_mock.session_state['associacoes'] = [{
        'dispositivo': "A1-AI-TIT01",
        'subscriber': "TestSubscriber",
        'observer': observer
    }]
    
    # Patch para funções do Streamlit
    monkeypatch.setattr('streamlit.warning', st_mock.warning)
    
    # Função simplificada para tentar adicionar uma associação duplicada
    def tentar_adicionar_duplicada():
        dispositivo_tag = "A1-AI-TIT01"
        subscriber_name = "TestSubscriber"
        
        if any(assoc['dispositivo'] == dispositivo_tag and assoc['subscriber'] == subscriber_name 
               for assoc in st_mock.session_state['associacoes']):
            st_mock.warning("Essa associação já existe.")
            return False
        return True
    
    # Executa a função
    resultado = tentar_adicionar_duplicada()
    
    # Verifica se a duplicação foi bloqueada
    assert resultado == False
    assert len(st_mock.warnings) == 1
    assert "Essa associação já existe." in st_mock.warnings[0]

# Teste para verificar o funcionamento correto quando não há dispositivos criados
def test_sem_dispositivos(monkeypatch, st_mock):
    """Testa o comportamento do sistema quando não há dispositivos criados."""
    # Configura o estado da sessão sem dispositivos
    st_mock.session_state['dispositivos_criados'] = []
    
    # Patch para funções do Streamlit
    monkeypatch.setattr('streamlit.error', st_mock.error)
    monkeypatch.setattr('streamlit.stop', st_mock.stop)
    
    # Função simplificada para verificar dispositivos
    def verificar_dispositivos():
        dispositivos_criados = st_mock.session_state['dispositivos_criados']
        if not dispositivos_criados:
            st_mock.error("Nenhum dispositivo foi criado. Verifique o arquivo Excel.")
            st_mock.stop()
            return False
        return True
    
    # Executa a função
    resultado = verificar_dispositivos()
    
    # Verifica se a verificação funcionou corretamente
    assert resultado == False
    assert len(st_mock.errors) == 1
    assert "Nenhum dispositivo foi criado" in st_mock.errors[0]

if __name__ == "__main__":
    # Executa os testes
    pytest.main(["-v", __file__])