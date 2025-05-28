<h1 align="center"> Clean Code - Design Patterns </h1>

<p align="center">
   <a href="#-tecnologias">Visão Geral</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
   <a href="#-projeto">Funcionalidades</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
   <a href="#-tecnologias">Problemas Detectados</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
   <a href="#-projeto">Refatoração</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
   <a href="#-projeto">Estrutura</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
   <a href="#-projeto">Instalação</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
   <a href="#-projeto">Testes</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
   <a href="#-projeto">Interface</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
   <a href="#-projeto">CHANGELOG</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</p>

## 📌 Visão Geral do Projeto
Este projeto demonstra a aplicação de padrões de projeto (Design Patterns) em sistemas embarcados de IoT. Utilizando dispositivos como Raspberry Pi e ESP8266, a plataforma realiza a leitura de temperatura via comunicação serial e exibe os dados em tempo real por meio de uma interface desenvolvida em Streamlit.

O código foi estruturado com foco em reutilização, escalabilidade e legibilidade, fazendo uso de padrões como Factory Method, Builder e Observer.


## 🧠 Funcionalidades Principais

✅ Criação de dispositivos IoT via Factory e Builder Patterns;

✅ Leitura de dados em tempo real via serial (ESP8266);

✅ Interface interativa com Streamlit;

✅ Sistema Observer para notificação de mudanças;

✅ Estilização customizada com CSS.


## 🛠️ Problemas Detectados (Pré-refatoração)

Código altamente acoplado entre camadas de leitura, interface e lógica de negócios;

Nomes de variáveis e funções pouco descritivos;

Falta de testes automatizados;

Ausência de linter e formatação inconsistente;

Presença de code smells como variáveis globais desnecessárias e responsabilidades duplicadas;

Uso ineficiente de session_state no Streamlit.


## 🔧 Estratégia de Refatoração

Modularização do projeto com separação de responsabilidades;

Padronização de nomes e estrutura de arquivos;

Redesenho parcial de componentes com base em Clean Code;

Aplicação de Interface Fluente para configuração de dispositivos;

Implementação de suíte de testes com cobertura parcial (~50%);

Integração de linter com flake8 e black;

Criação de documentação e ChangeLog organizados.

## 📁 Estrutura do Projeto

project-root/
├── src/
│   ├── main.py
│   ├── observer.py
│   ├── devices.py
│   ├── factories.py
│   ├── builders.py
├── app/
│   └── broker.py
├── data/
│   └── Ambiente_Controlado.xlsx
├── styles/
│   └── styles.css
├── tests/
│   ├── test_devices.py
│   └── test_factories.py
├── assets/
│   └── image.png
├── README.md
├── CHANGELOG.md
└── .flake8

## 🚀 Instalação e Execução

1.Clone o repositório:

git clone https://github.com/RenatoRibas/Design-Patterns-for-IoT-Embedded-Systems.git
cd Design-Patterns-for-IoT-Embedded-Systems

2.Instale as dependências:
pip install -r requirements.txt

3.Execute a aplicação:
streamlit run app/broker.py

4.Acesse no navegador: http://localhost:8501

## 🧪 Testes Automatizados

Implementado com pytest.

Localizados em tests/, com cobertura parcial (~50%).

Para rodar os testes:
pytest tests/

## 🧼 Linter e Formatação

Ferramentas: flake8, black

Para rodar manualmente:
flake8 src/
black src/

## 🧩 Interface Fluente

Foi aplicada uma interface fluente no padrão Builder para construção dos dispositivos, permitindo chamadas encadeadas como:
device = (
    DeviceBuilder()
    .with_tag("Sensor01")
    .with_type("Temperature")
    .with_location("Sala 1")
    .build()
)

## 🔄 CHANGELOG

O histórico de mudanças encontra-se no arquivo CHANGELOG.md, com as versões documentadas da seguinte forma:
## [1.1.0] - 2025-05-13
### Adicionado
- Suíte de testes com cobertura parcial
- Interface fluente no DeviceBuilder
- Aplicação de linter com Flake8 e Black

### Modificado
- Modularização da lógica principal
- Padronização de nomes e estrutura

### Removido
- Código duplicado e variáveis globais desnecessárias

### 👤 Autores
Renato Ribas
Jhayne Henemam
📅 Data da última refatoração: 13/05/2025

