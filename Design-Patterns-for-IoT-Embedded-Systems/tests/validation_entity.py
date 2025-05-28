import re
import os
import sys
import pytest

# Adicionando os caminhos necessários para importação
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

if src_dir not in sys.path:
    sys.path.append(src_dir)

# Tentativa de importar as classes reais, com fallback para mocks
try:
    from src.devices import AIDevicePublisher
except ImportError:
    AIDevicePublisher = None

# Validadores para tags
def validar_formato_tag(tag):
    """
    Valida o formato das tags dos dispositivos.
    
    Formato esperado: [A-Z]\d+-[A-Z]+-[A-Z]+\d+
    Exemplos válidos: A1-AI-TIT01, B2-DI-PIT03
    """
    pattern = r'^[A-Z]\d+-[A-Z]+-[A-Z]+\d+$'
    return bool(re.match(pattern, tag))

# Validadores para valores
def validar_temperatura(valor):
    """
    Valida se um valor de temperatura está dentro dos limites razoáveis.
    
    Para este projeto, consideramos temperaturas válidas entre -50°C e 150°C.
    """
    return -50 <= valor <= 150

def validar_unidade_temperatura(unidade):
    """
    Valida se a unidade de temperatura está em um formato válido.
    
    Formatos aceitos: "°C", "°F", "K"
    """
    return unidade in ["°C", "°F", "K"]

# Validadores para estrutura dos dispositivos
def validar_estrutura_dispositivo(dispositivo):
    """
    Valida se um dispositivo tem todos os atributos e métodos necessários.
    
    Retorna um dicionário com o resultado da validação.
    """
    resultado = {
        "valido": True,
        "erros": []
    }
    
    # Verificar atributos obrigatórios
    atributos_obrigatorios = ["tag", "value", "unit"]
    for attr in atributos_obrigatorios:
        if not hasattr(dispositivo, attr):
            resultado["valido"] = False
            resultado["erros"].append(f"Dispositivo não possui o atributo '{attr}'")
    
    # Verificar métodos obrigatórios
    metodos_obrigatorios = ["attach", "detach", "notify", "read_value"]
    for metodo in metodos_obrigatorios:
        if not hasattr(dispositivo, metodo) or not callable(getattr(dispositivo, metodo)):
            resultado["valido"] = False
            resultado["erros"].append(f"Dispositivo não possui o método '{metodo}'")
    
    # Verificar valores dos atributos
    if hasattr(dispositivo, "tag") and not validar_formato_tag(dispositivo.tag):
        resultado["valido"] = False
        resultado["erros"].append(f"Tag '{dispositivo.tag}' não está no formato correto")
    
    if hasattr(dispositivo, "value") and not validar_temperatura(dispositivo.value):
        resultado["valido"] = False
        resultado["erros"].append(f"Valor de temperatura {dispositivo.value} está fora dos limites aceitáveis")
    
    if hasattr(dispositivo, "unit") and not validar_unidade_temperatura(dispositivo.unit):
        resultado["valido"] = False
        resultado["erros"].append(f"Unidade '{dispositivo.unit}' não é válida para temperatura")
    
    return resultado

# Validadores para o Observer
def validar_subscriber(subscriber):
    """
    Valida se um subscriber tem todos os atributos e métodos necessários.
    
    Retorna um dicionário com o resultado da validação.
    """
    resultado = {
        "valido": True,
        "erros": []
    }
    
    # Verificar atributos obrigatórios
    atributos_obrigatorios = ["name", "notifications"]
    for attr in atributos_obrigatorios:
        if not hasattr(subscriber, attr):
            resultado["valido"] = False
            resultado["erros"].append(f"Subscriber não possui o atributo '{attr}'")
    
    # Verificar métodos obrigatórios
    if not hasattr(subscriber, "update") or not callable(getattr(subscriber, "update")):
        resultado["valido"] = False
        resultado["erros"].append("Subscriber não possui o método 'update'")
    
    # Verificar tipo das notificações
    if hasattr(subscriber, "notifications") and not isinstance(subscriber.notifications, list):
        resultado["valido"] = False
        resultado["erros"].append("O atributo 'notifications' não é uma lista")
    
    return resultado

# Validadores para dados de Excel
def validar_dados_excel(df):
    """
    Valida se o DataFrame do Excel possui as colunas necessárias e formatos corretos.
    
    Retorna um dicionário com o resultado da validação.
    """
    resultado = {
        "valido": True,
        "erros": []
    }
    
    # Verificar colunas obrigatórias
    colunas_obrigatorias = ["Tipo", "Tag", "Descrição", "Unidade", "Dispositivo"]
    for coluna in colunas_obrigatorias:
        if coluna not in df.columns:
            resultado["valido"] = False
            resultado["erros"].append(f"DataFrame não possui a coluna '{coluna}'")
    
    # Se não tiver as colunas básicas, não adianta continuar a validação
    if not resultado["valido"]:
        return resultado
    
    # Verificar tipos
    tipos_validos = ["AI"]  # Podemos expandir conforme necessário
    tipos_invalidos = df[~df["Tipo"].isin(tipos_validos)]["Tipo"].unique()
    if len(tipos_invalidos) > 0:
        resultado["valido"] = False
        resultado["erros"].append(f"Tipos inválidos encontrados: {list(tipos_invalidos)}")
    
    # Verificar tags
    for i, tag in enumerate(df["Tag"]):
        if not validar_formato_tag(tag):
            resultado["valido"] = False
            resultado["erros"].append(f"Tag inválida na linha {i+1}: '{tag}'")
    
    # Verificar unidades
    for i, unidade in enumerate(df["Unidade"]):
        if not validar_unidade_temperatura(unidade):
            resultado["valido"] = False
            resultado["erros"].append(f"Unidade inválida na linha {i+1}: '{unidade}'")
    
    # Verificar dispositivos
    dispositivos_validos = ["ESP8266", "RaspberryPi"]
    dispositivos_invalidos = df[~df["Dispositivo"].isin(dispositivos_validos)]["Dispositivo"].unique()
    if len(dispositivos_invalidos) > 0:
        resultado["valido"] = False
        resultado["erros"].append(f"Dispositivos inválidos encontrados: {list(dispositivos_invalidos)}")
    
    return resultado

# Validadores para associações
def validar_associacao(associacao, dispositivos):
    """
    Valida se uma associação entre dispositivo e subscriber está correta.
    
    Retorna um dicionário com o resultado da validação.
    """
    resultado = {
        "valido": True,
        "erros": []
    }
    
    # Verificar campos obrigatórios
    campos_obrigatorios = ["dispositivo", "subscriber", "observer"]
    for campo in campos_obrigatorios:
        if campo not in associacao:
            resultado["valido"] = False
            resultado["erros"].append(f"Associação não possui o campo '{campo}'")
    
    # Se não tiver os campos básicos, não adianta continuar a validação
    if not resultado["valido"]:
        return resultado
    
    # Verificar se o dispositivo existe na lista de dispositivos
    if not any(d.tag == associacao["dispositivo"] for d in dispositivos):
        resultado["valido"] = False
        resultado["erros"].append(f"Dispositivo '{associacao['dispositivo']}' não existe na lista de dispositivos")
    
    # Verificar se o observer é válido
    if "observer" in associacao:
        observer_validacao = validar_subscriber(associacao["observer"])
        if not observer_validacao["valido"]:
            resultado["valido"] = False
            resultado["erros"].extend(observer_validacao["erros"])
    
    return resultado

# Testes para os validadores
def test_validar_formato_tag():
    """Testa o validador de formato de tag."""
    # Tags válidas
    assert validar_formato_tag("A1-AI-TIT01") == True
    assert validar_formato_tag("B2-DI-PIT03") == True
    
    # Tags inválidas
    assert validar_formato_tag("AI-TIT01") == False  # Falta o prefixo de área
    assert validar_formato_tag("A1-AI-") == False  # Incompleta
    assert validar_formato_tag("a1-ai-tit01") == False  # Case sensitive
    assert validar_formato_tag("A1_AI_TIT01") == False  # Separadores incorretos

def test_validar_temperatura():
    """Testa o validador de temperatura."""
    # Temperaturas válidas
    assert validar_temperatura(25.5) == True
    assert validar_temperatura(-30) == True
    assert validar_temperatura(100) == True
    
    # Temperaturas inválidas
    assert validar_temperatura(-100) == False  # Muito baixa
    assert validar_temperatura(200) == False  # Muito alta

def test_validar_unidade_temperatura():
    """Testa o validador de unidade de temperatura."""
    # Unidades válidas
    assert validar_unidade_temperatura("°C") == True
    assert validar_unidade_temperatura("°F") == True
    assert validar_unidade_temperatura("K") == True
    
    # Unidades inválidas
    assert validar_unidade_temperatura("C") == False
    assert validar_unidade_temperatura("Celsius") == False
    assert validar_unidade_temperatura("Graus") == False

if __name__ == "__main__":
    # Executa os testes
    pytest.main(["-v", __file__])