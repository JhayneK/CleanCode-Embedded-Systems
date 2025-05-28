# src/read_excel.py

##################### Leitura do arquivo de dados ###################################################################################

import pandas as pd

def ler_dados_excel(file_path):
    df = pd.read_excel(file_path)

    df_filtered = df.loc[
        ((df['Tag table'] == 'AI') & (df['TAG'].notnull())) |
        (df['Tag table'] == 'DO')
    ]
    
    devices_data = []
    for _, row in df_filtered.iterrows():
        tipo = row['Tag table']
        tag = row['TAG']
        area = row['Area']
        descricao = row['Descrição']
        
        if tipo == 'AI':
            range_min = row['Range Min']
            range_max = row['Range Max']
            unit = row['Unit']
            devices_data.append((tipo, tag, area, descricao, range_min, range_max, unit))
        else:
            devices_data.append((tipo, tag, area, descricao))
    
    return devices_data
