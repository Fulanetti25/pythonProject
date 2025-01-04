import requests
import os
import logging
import traceback
import inspect
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


def ExtrairPalavras(palavra = 'planilha+personalizada'):
	log_info = "F1"
	varl_detail = None

	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'}

	session = requests.Session()
	session.headers.update(headers)
	response = requests.get('https://www.google.com/search?q=' + palavra, headers=headers)
	soup = BeautifulSoup(response.content, 'html.parser')
	#session.cookies.clear()

	texto_pagina = soup.get_text(separator='\n')
	linhas = texto_pagina.split('\n')

	df_temp = pd.DataFrame()
	df = pd.DataFrame(linhas, columns=['Texto'])
	df = df.map(lambda x: str(x).replace(';', ',') if isinstance(x, str) else x)
	df = df.map(lambda x: str(x).replace('\n', '') if isinstance(x, str) else x)
	df = df.map(lambda x: str(x).replace('\r', '') if isinstance(x, str) else x)
	if not df.empty: df.index += 1
	pd.set_option('display.max_columns', None)
	pd.set_option('display.max_rows', None)

	caminhos = json_caminho('Base_Pesquisas_Google')
	file_dir = caminhos['Diretorio']
	file_name = os.path.join(file_dir, caminhos['Arquivo'])

	try:
		log_info = "F2"
		filtro = df[df['Texto'].str.contains(r'.* segundos\)', regex=True)]
		if not filtro.empty:
			ignore_until = filtro.index[0]
			ignore_after = df[df['Texto'].str.contains('Resultados da pesquisa', regex=True)].index[0]
			ignore_ending = df[df['Texto'].str.contains('Navegação nas páginas', regex=True)].index[0]
			df_add_filtered = df.loc[ignore_until + 1: ignore_after]
			df_add_filtered = df_add_filtered.Texto.copy()
			patrocinado_indices = df_add_filtered[df_add_filtered.str.contains('Patrocinado')].index

			anuncios = []
			for i in patrocinado_indices:
				bloco = {}
				bloco['Palavra'] = palavra
				bloco['Tipo'] = df_add_filtered.loc[i]
				bloco['Anuncio'] = df_add_filtered.loc[i + 1]
				bloco['Nome Empresa'] = df_add_filtered.loc[i + 2]
				bloco['Site Empresa'] = df_add_filtered.loc[i + 3]
				detalhes = []
				for j in range(i + 4, max(list(df_add_filtered.index))):
					if df_add_filtered.loc[j] == 'Patrocinado':
						break
					detalhes.append(df_add_filtered.loc[j])
				bloco['Detalhe Anuncio'] = ' '.join(detalhes)
				anuncios.append(bloco)
			df_anuncios = pd.DataFrame(anuncios)

			df_res_filtered = df.loc[ignore_after:ignore_ending + 2]
			df_res_filtered = df_res_filtered.Texto.copy()
			sites_indices = df_res_filtered[df_res_filtered.str.contains('http')].drop_duplicates().index

			organico = []
			for i in sites_indices:
				bloco = {}
				bloco['Palavra'] = palavra
				bloco['Tipo'] = 'Organico'
				bloco['Anuncio'] = df_res_filtered.loc[i - 2]
				bloco['Nome Empresa'] = df_res_filtered.loc[i - 1]
				bloco['Site Empresa'] = df_res_filtered.loc[i]
				detalhes = []
				if (sites_indices > i).any():
					proximo_indice = sites_indices[sites_indices > i].min()
				else:
					proximo_indice = max(list(df_res_filtered.index))
				for j in range(i + 1, proximo_indice - 2):
					detalhes.append(df_res_filtered.loc[j])
				bloco['Detalhe Anuncio'] = ' '.join(detalhes)
				organico.append(bloco)
			df_organico = pd.DataFrame(organico)

		else:
			pass

		log_info = "F3"
		if 'df_anuncios' not in locals():
			df_anuncios = pd.DataFrame()
		if 'df_organico' not in locals():
			df_organico = pd.DataFrame()
		if df_anuncios.empty and df_organico.empty:
			ValueError("Ambos os DataFrames, df_anuncios e df_organico, estão vazios ou não foram gerados.")

		df_final = pd.concat([df_anuncios, df_organico], ignore_index=True)
		df_final = pd.concat([df_anuncios, df_organico], ignore_index=True)
		df_final['DATA_HORA'] = datetime.now()
		df_final['RANK'] = range(1, len(df_final) + 1)
		df_temp = pd.concat([df_temp, df_final], ignore_index=True)

		log_info = "F4"
		if os.path.exists(file_name):
			df_existente = pd.read_csv(file_name)
			df_concatenado = pd.concat([df_existente, df_temp], ignore_index=True)
		else:
			df_concatenado = df_temp
		df_concatenado.to_csv(file_name, index=False)

		log_info = "F0"

	except IndexError as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	except ValueError as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": str(palavra), 'Status_log': log_info, 'Detail_log': varl_detail}


def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	palavras = json_caminho('Json_Palavras')
	file_dir = palavras['Diretorio']
	file_name = os.path.join(file_dir, palavras['Arquivo'])
	info_palavras = json_dados(os.path.join(palavras['Diretorio'], palavras['Arquivo']))
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		for index, palavra in enumerate(info_palavras['palavras']):
			resultado = ExtrairPalavras(palavra)
			exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
			exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
			exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
		exec_info += "\t\tMF\n"
		varg_erro = False

	except Exception as e:
		exec_info += "\t\t\tM99\n"
		exec_info += f"Traceback: {traceback.format_exc()}"
		varg_erro = True
		raise

	finally:
		exec_info += "LF\n"
		log_registra(varg_modulo, inspect.currentframe().f_code.co_name, var_detalhe=exec_info, var_erro=varg_erro)
		logging.shutdown()


if __name__ == "__main__":
	main()
	print(exec_info)