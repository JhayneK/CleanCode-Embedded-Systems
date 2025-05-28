 #**************************************************/

 #Project: Design-Patterns-for-IoT-Embedded-Systems
 #Data: 01/11/2024
 #Version: 1.0
 #Description: This code implements the platform based on Design Patterns, where the devices (Raspberry Pi and Esp8266) are integrated for read the 
 # temperature and disponilized in the platform to method observers and create objects with the Factory Method and Builder Pattern.
 #The create objects are based on read the I/O list in excel file.
 #License: MIT

 #**************************************************/

##################### INICIO DE PROGRAMA ###################################################################################

import os
import serial
import time
from threading import Thread

from .read_excel import ler_dados_excel
from .observer import GenericSubscriber
from .devices import AIDevicePublisher
from .factories import DODeviceFactory
from .builders import AIDeviceBuilder

base_path = os.path.dirname(os.path.abspath(__file__))

##################### INICIALIZA PORTA SERIAL E COMUNICAÇÃO COM NODEMCU ####################################################

ser = serial.Serial('COM5', 115200)
time.sleep(2)

##################### CLASSE CRIA OBJETO CONFORME ENTRADA ##################################################################


def criar_dispositivo(tipo, *args):
    if tipo == "DO":
        factory = DODeviceFactory()
        return factory.criar_device(*args[:3])  # tag, area, descricao
    elif tipo == "AI":
        builder = AIDeviceBuilder()
        dispositivo = (builder
                       .set_tag(args[0])
                       .set_area(args[1])
                       .set_descricao(args[2])
                       .set_range_min(args[3])
                       .set_range_max(args[4])
                       .set_unit(args[5])
                       .build())
        print(dispositivo)
        return dispositivo
        
    else:
        raise ValueError(f"Tipo de dispositivo {tipo} desconhecido")
    

##################### LEITURA DO SENSOR DE TEMPERATURA A1-AI-TIT01 VIA PORTA SERIAL ##########################################

import time

def ler_sensor(dispositivos_criados, stop_event):  # stop_event é um evento que será usado para parar a thread
    while not stop_event.is_set():
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()  # Use strip() para remover espaços em branco e quebras de linha extras
            print(f"Leitura do sensor: {line}")
            
            # Verifica se a linha contém apenas caracteres numéricos e ponto decimal e tem um formato válido
            if line.replace('.', '', 1).isdigit() and line.count('.') <= 1:
                try:
                    temperatura = float(line)
                    # Verifica se a temperatura está em um intervalo esperado para evitar leituras absurdas
                    if 15.0 <= temperatura <= 50.0:  # Faixa de temperatura aceitável
                        for dispositivo in dispositivos_criados:
                            if isinstance(dispositivo, AIDevicePublisher) and dispositivo.tag == "A1-AI-TIT01":
                                dispositivo.update_value(temperatura)
                    else:
                        print(f"Leitura fora da faixa esperada: {temperatura} °C")
                except ValueError:
                    print(f"Erro ao processar a linha: {line}")
            else:
                print(f"Formato inválido de leitura: {line}")
        
        time.sleep(1.0)



##################### LEITURA DO ARQUIVO DE DADOS E CRIAÇÃO DOS DISPOSITIVOS ##################################################


def processar_e_criar_dispositivos():
    file_path = os.path.join(base_path, '..', 'data', 'Ambiente_Controlado.xlsx')

    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo de dados não encontrado {file_path}")
        return []

    # Lê os dados do Excel
    devices_data = ler_dados_excel(file_path)

    # Cria dispositivos com base nos dados
    dispositivos_criados = [criar_dispositivo(*device_info) for device_info in devices_data]
    return dispositivos_criados
