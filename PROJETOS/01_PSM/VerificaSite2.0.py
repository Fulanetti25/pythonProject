import requests
import os
import logging
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(filename='G:\\Meu Drive\\PSM\\01 - OPERACIONAL\\00_FONTES\\app.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Configuração inicial
url = {}
url[0] = "https://www.google.com/search?q=planilha+personalizada"
url[1] = "https://www.google.com/search?q=criação+planilha"
url[2] = "https://www.google.com/search?q=planilha"
url[3] = "https://www.google.com/search?q=planilha+excel"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'
}

df_temp = pd.DataFrame()

for k in range(0, len(url), 1):
    print('Iniciando processo: ', k + 1, ' de ', len(url), ' - ', url[k])
    session = requests.Session()
    session.headers.update(headers)
    response = requests.get(url[k], headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    session.cookies.clear()

    # Extrair todo o texto da página, preservando a estrutura
    texto_pagina = soup.get_text(separator='\n')
    linhas = texto_pagina.split('\n')

    # Cria um DataFrame a partir das linhas
    df = pd.DataFrame(linhas, columns=['Texto'])
    if not df.empty:
        df.index += 1  # Ajustar índice para começar em 1

        # Configurações do pandas para exibir a tabela completa
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)

        # Identificar linhas a ignorar
        try:
            ignore_until = df[df['Texto'].str.contains(r'.* segundos\)', regex=True)].index[0]
            ignore_after = df[df['Texto'].str.contains('Resultados da pesquisa', regex=True)].index[0]
            ignore_ending = df[df['Texto'].str.contains('Navegação nas páginas', regex=True)].index[0]
            df_add_filtered = df.loc[ignore_until + 1: ignore_after]
            df_add_filtered = df_add_filtered.Texto.copy()
        except IndexError as e:
            logging.error("IndexError: %s", e)

        # Lógica para "Anúncios"
        patrocinado_indices = df_add_filtered[df_add_filtered.str.contains('Patrocinado')].index

        # Extrair dados de "Patrocinado"
        anuncios = []
        for i in patrocinado_indices:
            bloco = {}
            bloco['Palavra'] = url[k]
            bloco['Tipo'] = df_add_filtered.loc[i]
            bloco['Anuncio'] = df_add_filtered.loc[i + 1]
            bloco['Nome Empresa'] = df_add_filtered.loc[i + 2]
            bloco['Site Empresa'] = df_add_filtered.loc[i + 3]
            # Concatena detalhes do anúncio até a próxima quebra
            detalhes = []
            for j in range(i + 4, max(list(df_add_filtered.index))):
                if df_add_filtered.loc[j] == 'Patrocinado':
                    break
                detalhes.append(df_add_filtered.loc[j])
            bloco['Detalhe Anuncio'] = ' '.join(detalhes)
            anuncios.append(bloco)

        # Criar dataframe com anúncios
        df_anuncios = pd.DataFrame(anuncios)

        # Lógica para "Resultados"
        df_res_filtered = df.loc[ignore_after:ignore_ending + 2]
        df_res_filtered = df_res_filtered.Texto.copy()
        sites_indices = df_res_filtered[df_res_filtered.str.contains('http')].drop_duplicates().index

        organico = []
        for i in sites_indices:
            bloco = {}
            bloco['Palavra'] = url[k]
            bloco['Tipo'] = 'Organico'
            bloco['Anuncio'] = df_res_filtered.loc[i - 2]
            bloco['Nome Empresa'] = df_res_filtered.loc[i - 1]
            bloco['Site Empresa'] = df_res_filtered.loc[i]
            # Concatena detalhes do resultado até a próxima quebra
            detalhes = []
            if (sites_indices > i).any():
                proximo_indice = sites_indices[sites_indices > i].min()
            else:
                proximo_indice = max(list(df_res_filtered.index))
            for j in range(i + 1, proximo_indice - 2):
                detalhes.append(df_res_filtered.loc[j])
            bloco['Detalhe Anuncio'] = ' '.join(detalhes)
            organico.append(bloco)

        # Criar dataframe com organicos
        df_organico = pd.DataFrame(organico)

        # Unir dataframes
        df_final = pd.concat([df_anuncios, df_organico], ignore_index=True)
        df_final['DATA_HORA'] = datetime.now()
        df_final['RANK'] = range(1, len(df_final) + 1)
        df_temp = pd.concat([df_temp, df_final], ignore_index=True)

# PARTE FINAL - GERAR ARQUIVOS
# Gerar arquivo Excel
if os.path.exists('G:\\Meu Drive\\PSM\\01 - OPERACIONAL\\00_FONTES\\pesquisas_google.csv'):
    df_existente = pd.read_csv('G:\\Meu Drive\\PSM\\01 - OPERACIONAL\\00_FONTES\\pesquisas_google.csv')
    df_concatenado = pd.concat([df_existente, df_temp], ignore_index=True)
    print('Arquivo empilhado')
else:
    df_concatenado = df_temp
    print('Arquivo criado')

df_concatenado.to_csv('G:\\Meu Drive\\PSM\\01 - OPERACIONAL\\00_FONTES\\pesquisas_google.csv', index=False)
print("Arquivo Excel 'pesquisas_google.xlsx' gerado com sucesso!")