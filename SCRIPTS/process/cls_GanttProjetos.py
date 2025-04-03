import os
import logging
import traceback
import inspect
import locale
import pandas as pd
import plotly.express as px
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_OutWhatsapp import prc_executa_whats


def processar_base():
	log_info = "F1"
	varl_detail = None
	caminhos = json_caminho('Base_Projetos_Excel')
	file_dir = caminhos['Diretorio']
	file_name = os.path.join(file_dir, caminhos['Arquivo'])
	caminhos = json_caminho('Base_Projetos_Gantt')
	out_dir = caminhos['Diretorio']
	out_name = os.path.join(file_dir, caminhos['Arquivo'])
	pd.set_option('mode.chained_assignment', None)

	try:
		log_info = "F2"
		df = pd.read_csv(file_name)

		log_info = "F3"
		df.columns = df.iloc[0]
		df = df[1:]
		df_selecionado = df[
			['CLI_NOME', 'PROJ_STATUS', 'DEV_NOME', 'PROJ_DATA', 'PROJ_PRAZO', 'PROJ_ENTREGA', 'PROJ_GARANTIA',
			 'PROJ_VALOR', 'FIN_PAGO']]
		df_filtrado = df_selecionado[
			(df_selecionado['PROJ_STATUS'] == '2-DEV_ANDAMENTO') | (df_selecionado['PROJ_STATUS'] == '4-CLI_GARANTIA')]
		df_filtrado['DEV_NOME'] = df_filtrado['DEV_NOME'].fillna('').apply(lambda x: ' '.join(x.split()[:2]))
		df_filtrado['PROJ_VALOR'] = pd.to_numeric(df_filtrado['PROJ_VALOR'], errors='coerce')
		df_filtrado['FIN_PAGO'] = pd.to_numeric(df_filtrado['FIN_PAGO'], errors='coerce')
		df_filtrado['PROJ_PRAZO'] = pd.to_numeric(df_filtrado['PROJ_PRAZO'], errors='coerce')
		df_filtrado['PROJ_DATA'] = pd.to_datetime(df_filtrado['PROJ_DATA'], errors='coerce')
		df_filtrado['DATA_HOJE'] = pd.to_datetime(pd.Timestamp.today().normalize(), errors='coerce').tz_localize('UTC')
		df_filtrado['DATA_MAXIMA'] = df_filtrado['DATA_HOJE'] + pd.Timedelta(days=31)
		df_filtrado['DATA_ESTIMADA'] = df_filtrado.apply(
			lambda row: row['PROJ_ENTREGA'] if pd.notna(row['PROJ_ENTREGA']) else row['PROJ_DATA'] + pd.to_timedelta(
				row['PROJ_PRAZO'], unit='D'),
			axis=1
		)
		df_filtrado['DATA_ESTIMADA_FINAL'] = df_filtrado.apply(
			lambda row: row['PROJ_GARANTIA'] if pd.notna(row['PROJ_ENTREGA']) else row[
																					   'DATA_ESTIMADA'] + pd.to_timedelta(
				7, unit='D'),
			axis=1
		)
		df_filtrado['VALOR_PENDENTE'] = df_filtrado['PROJ_VALOR'] - df_filtrado['FIN_PAGO']
		df_filtrado['DATA_ESTIMADA_FINAL'] = pd.to_datetime(df_filtrado['DATA_ESTIMADA_FINAL'], errors='coerce')
		df_filtrado['DATA_HOJE'] = pd.to_datetime(df_filtrado['DATA_HOJE'], errors='coerce')

		df_filtrado['PROJ_STATUS'] = df_filtrado.apply(
			lambda row: "ATRASO" if row['DATA_ESTIMADA_FINAL'] < row['DATA_HOJE'] else row['PROJ_STATUS'],
			axis=1
		)
		df_ordenado = df_filtrado.sort_values(by=['PROJ_DATA', 'CLI_NOME'], ascending=[True, True])

		log_info = "F4"
		df_ordenado.to_csv(out_name)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass

	return {"Resultado": str(df_ordenado.shape), 'Status_log': log_info, 'Detail_log': varl_detail}


def gerar_grafico_gantt():
	locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
	log_info = "F1"
	varl_detail = None
	caminhos = json_caminho('Base_Projetos_Gantt')
	file_dir = caminhos['Diretorio']
	file_name = os.path.join(file_dir, caminhos['Arquivo'])
	caminhos = json_caminho('Imagem_Projetos_Gantt')
	out_dir = caminhos['Diretorio']
	out_name = os.path.join(file_dir, caminhos['Arquivo'])

	try:
		log_info = "F2"
		df = pd.read_csv(file_name)

		log_info = "F3"
		df['EIXO'] = df.index.astype(str) + " | " + df['DEV_NOME'] + "/ " + df['CLI_NOME'] + " / " + df['PROJ_STATUS']
		df['EIXO'] = df['EIXO'].fillna('').astype(str).apply(lambda x: x.replace("ATRASO", "<b>ATRASO</b>"))
		df['ROTULO'] = pd.to_datetime(df['DATA_ESTIMADA_FINAL'], errors='coerce').dt.strftime('%d/%b').str.lower() + " - R$ " + df['VALOR_PENDENTE'].round(2).astype(str)

		df_blue = df.copy()
		df_blue['x_start'] = df_blue['DATA_HOJE']
		df_blue['x_end'] = df_blue['DATA_ESTIMADA']
		df_blue['color'] = 'blue'
		df_orange = df.copy()
		df_orange['x_start'] = df_orange['DATA_ESTIMADA']
		df_orange['x_end'] = df_orange['DATA_ESTIMADA_FINAL']
		df_orange['color'] = 'orange'
		df_combined = pd.concat([
			df_blue[
				['EIXO', 'ROTULO', 'PROJ_STATUS', 'CLI_NOME', 'DEV_NOME', 'DATA_HOJE', 'DATA_ESTIMADA', 'DATA_MAXIMA', 'x_start', 'x_end', 'color']],
			df_orange[
				['EIXO', 'ROTULO', 'PROJ_STATUS', 'CLI_NOME', 'DEV_NOME', 'DATA_HOJE', 'DATA_ESTIMADA', 'DATA_MAXIMA', 'x_start', 'x_end', 'color']]
		])

		fig = px.timeline(
			df_combined,
			x_start="x_start",
			x_end="x_end",
			y='EIXO',
			color="color",
			text='ROTULO',
			title="Projetos PSM em Andamento"
		)
		fig.update_layout(
			height=1000,
			width=2000,
			margin=dict(l=50, r=50, t=50, b=50),
			xaxis=dict(title=None, showgrid=True, gridcolor='black', gridwidth=0.5, tickfont=dict(size=20), tickformat="%d/%m/%y", range=[df['DATA_HOJE'].min(), df['DATA_MAXIMA'].max()]),
			yaxis=dict(title=None, tickfont=dict(size=20), tickmode='linear'),
			showlegend=False
		)
		fig.update_yaxes(tickmode="array", tickvals=df_combined['EIXO'], ticktext=df_combined['EIXO'])
		fig.update_traces(textfont=dict(size=20, color="black"), textposition="outside",insidetextanchor="end")

		log_info = "F4"
		fig.write_image(out_name)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		os.remove(file_name)

	return {"Resultado": str(out_name), 'Status_log': log_info, 'Detail_log': varl_detail}


def enviar_grafico_gantt():
	log_info = "F1"
	varl_detail = None
	caminhos = json_caminho('Imagem_Projetos_Gantt')
	file_dir = caminhos['Diretorio']
	file_name = os.path.join(file_dir, caminhos['Arquivo'])
	numero = "PSM - DESENVOLVIMENTO"
	mensagem = ("*Bom dia Time DEV!* Esta é uma mensagem automática visando acompanharmos nossas entregas. "
				"Qualquer alteração dos fatos ou regras, dar-se-á no dia seguinte.")
	try:
		log_info = "F2"
		resultado = prc_executa_whats(numero, mensagem, file_name)

		log_info = "F0"

	except Exception as e:
		varl_detail = f"Erro na etapa {log_info}, {e}"
		log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
		log_info = "F99"
		raise

	finally:
		pass
		os.remove(file_name)

	return {"Resultado": str(resultado), 'Status_log': log_info, 'Detail_log': varl_detail}

def main():
	varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))

	global exec_info
	exec_info = "\nLI\n"

	exec_info += "\tGI\n"
	varg_erro = None
	exec_info += "\tGF\n"

	exec_info += "\t\tMI\n"
	try:
		resultado1 = processar_base()
		exec_info += f"\t\t\t\tResultado: {resultado1['Resultado']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado1['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado1['Detail_log']}\n"
		resultado2 = gerar_grafico_gantt()
		exec_info += f"\t\t\t\tResultado: {resultado2['Resultado']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado2['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado2['Detail_log']}\n"
		resultado3 = enviar_grafico_gantt()
		exec_info += f"\t\t\t\tResultado: {resultado3['Resultado']}\n"
		exec_info += f"\t\t\t\tStatus: {resultado3['Status_log']}\n"
		exec_info += f"\t\t\t\tDetail: {resultado3['Detail_log']}\n"
		exec_info += "\t\tMF\n"
		varg_erro = False

	except Exception as e:
		exec_info += "\t\t\tM99\n"
		exec_info += f"Traceback: {traceback.format_exc()}"
		varg_erro = True
		raise

	finally:
		exec_info += "LF\n"
		log_registra(var_modulo=varg_modulo, var_funcao=inspect.currentframe().f_code.co_name, var_detalhe=exec_info, var_erro=varg_erro)
		logging.shutdown()


if __name__ == "__main__":
	main()
	print(exec_info)