import os
import logging
import traceback
import inspect
import pandas as pd
from datetime import datetime
from serpapi import GoogleSearch
from decouple import config
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados, json_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


SERP_API = config('FULA_SERP_API')


def fnc_verifica_anuncio(file_name, out_name) -> dict:
	log_info = "F1"
	varl_detail = None
	resultados_gerais = []

	try:
		log_info = "F2"
		dados = json_dados(file_name)
		palavras = dados['palavras']

		for palavra_chave in palavras:
			params = {
				"engine": "google",
				"q": palavra_chave,
				"location": "Brazil",
				"hl": "pt-br",
				"gl": "br",
				"api_key": SERP_API,
			}
			search = GoogleSearch(params)
			results = search.get_dict()
			resultados_gerais.append(results)

		os.makedirs(os.path.dirname(out_name), exist_ok=True)
		json_registra(resultados_gerais, out_name)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": resultados_gerais, 'Status_log': log_info, 'Detail_log': varl_detail}


def fnc_formatar_palavras(dados_raw: dict, palavra: str) -> pd.DataFrame:
	log_info = "F1"
	varl_detail = None
	resultados = []
	rank = 1
	agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	try:
		log_info = "F2"
		for ad in dados_raw.get("ads", []):
			resultados.append({
				"DATA_HORA": agora,
				"RANK": rank,
				"Palavra": palavra,
				"Tipo": "patrocinado",
				"Anuncio": ad.get("title", ""),
				"Nome Empresa": ad.get("displayed_link", ""),
				"Site Empresa": ad.get("link", ""),
				"Detalhe Anuncio": ad.get("snippet", "")
			})
			rank += 1

		log_info = "F3"
		for item in dados_raw.get("organic_results", []):
			resultados.append({
				"DATA_HORA": agora,
				"RANK": rank,
				"Palavra": palavra,
				"Tipo": "organico",
				"Anuncio": item.get("title", ""),
				"Nome Empresa": item.get("displayed_link", ""),
				"Site Empresa": item.get("link", ""),
				"Detalhe Anuncio": item.get("snippet", "")
			})
			rank += 1

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": pd.DataFrame(resultados), 'Status_log': log_info, 'Detail_log': varl_detail}


def prc_ProcessarPalavras():
	import csv
	log_info = "F1"
	varl_detail = None
	df_concatenado = pd.DataFrame()
	caminhos = json_caminho('Raw_Pesquisas_Google')
	raw_file = os.path.join(caminhos['Diretorio'], caminhos['Arquivo'])
	caminhos = json_caminho('Base_Pesquisas_Google')
	out_file = os.path.join(caminhos['Diretorio'], caminhos['Arquivo'])
	caminhos = json_caminho('Json_Palavras')
	word_file = os.path.join(caminhos['Diretorio'], caminhos['Arquivo'])

	try:
		log_info = "F2"
		fnc_verifica_anuncio(word_file, raw_file)
		raw_data = json_dados(raw_file)

		log_info = "F3"
		palavras_dict = json_dados(word_file)
		lista_palavras = palavras_dict.get("palavras", [])

		for i, dados_raw in enumerate(raw_data):
			if i >= len(lista_palavras):
				continue
			palavra = lista_palavras[i]
			res_formatado = fnc_formatar_palavras(dados_raw, palavra)
			df_formatado = res_formatado['Resultado']
			df_concatenado = pd.concat([df_concatenado, df_formatado], ignore_index=True)

		log_info = "F4"
		modo = 'a' if os.path.exists(out_file) else 'w'
		cabecalho = not os.path.exists(out_file)
		df_concatenado.to_csv(out_file,	mode=modo, header=cabecalho, index=False, sep=';', encoding='utf-8', quotechar='"',	quoting=csv.QUOTE_ALL)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	return {"Resultado": "Dados atualizados com sucesso", 'Status_log': log_info, 'Detail_log': varl_detail}


def exe_GooglePalavras():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado = prc_ProcessarPalavras()
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