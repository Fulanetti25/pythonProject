import os
import inspect
import traceback
import time
from blessed import Terminal
from datetime import datetime, timedelta
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_BarraProgresso import barra_Criar, barra_CriarTempo, barra_Atualizar, barra_Finalizar
from SCRIPTS.process.cls_ContaPJ import fnc_saldos_por_periodo
from SCRIPTS.process.cls_ProjetosPSM import fnc_projetos_por_periodo

COLUNA_ESQ = 0
COLUNA_DIR = 100
LINHA_CABECALHO = 0
LINHA_DADOS = 3
LINHA_TEMPORIZADOR = 59
LINHA_KPI = 40


def fn_validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def fnc_LogRecupera(processo=None, data=None):
    log_info = "F1"
    varl_detail = None

    caminhos = json_caminho('Json_Caminhos')
    info_caminhos = json_dados(os.path.join(caminhos['Diretorio'], caminhos['Arquivo']))
    caminho = next((item for item in info_caminhos['caminhos'] if item['Nome'] == 'Log_Acompanhamento'), None)

    dados_log = os.path.join(caminho['Diretorio'], caminho['Arquivo'])
    with open(dados_log, 'r') as arquivo:
        linhas = arquivo.readlines()

    data_limite = datetime.now() - timedelta(days=7) if not data else datetime.strptime(data, '%Y-%m-%d')

    log_info = "F2"
    registros_com_data = []
    for i, linha in enumerate(linhas):
        if len(linha) >= 10 and fn_validate_date(linha[:10]):
            data_log = datetime.strptime(linha.split(',')[0], '%Y-%m-%d %H:%M:%S')
            if data_log >= data_limite and (not data or data_log.date() == data_limite.date()):
                registros_com_data.append(linha)

    log_info = "F3"
    registros_final = []
    if processo:
        for registro in registros_com_data:
            if processo in registro:
                registros_final.append(registro)
    else:
        registros_final = registros_com_data

    registros_final.sort(reverse=True, key=lambda x: datetime.strptime(x.split(',')[0], '%Y-%m-%d %H:%M:%S'))

    log_info = "F0"
    return registros_final


def fnc_UltimoLog(nome_classe):
    registros = fnc_LogRecupera(nome_classe)

    if registros:
        registros_sucesso = [registro for registro in registros if "Sucesso" in registro]
        if registros_sucesso:
            ultima_execucao_str = registros_sucesso[0].split(',')[0]
            ultima_execucao = datetime.strptime(ultima_execucao_str, '%Y-%m-%d %H:%M:%S')
            return ultima_execucao

    return datetime.now() - timedelta(days=1)


def tela_limpar():
    os.system('cls' if os.name == 'nt' else 'clear')


def exibir_texto(term, x, y, texto, estilo=None):
    with term.location(x, y):
        if estilo:
            print(estilo + texto + term.normal)
        else:
            print(texto)


def barra_fake(term, x, y, total, incremento):
    with term.location(x, y):
        fake = barra_Criar(total=total, cor_barra="green", cor_fonte="white")
        for i in range(total):
            barra_Atualizar(fake, incremento=incremento)
            time.sleep(0.1)
        barra_Finalizar(fake)


def barra_tempo(term, x, y, total, incremento):
    with term.location(x, y):
        tempo = barra_CriarTempo(total=total)
        for i in range(total):
            barra_Atualizar(tempo, incremento=incremento)
            time.sleep(1)
        barra_Finalizar(tempo)


def tela_superior_esq(term):
    exibir_texto(term, COLUNA_ESQ, LINHA_CABECALHO, "Gerenciador de Processos Pytão", estilo=term.underline + term.cyan)
    exibir_texto(term, COLUNA_ESQ + 70, LINHA_CABECALHO, str(datetime.now()), estilo=term.bold_blue)
    exibir_texto(term, COLUNA_ESQ, LINHA_DADOS, "Últimos Logs:", estilo=term.underline + term.bold_red)
    registros = fnc_LogRecupera()
    linha_y = LINHA_DADOS + 1
    for registro in registros:
        if linha_y >= LINHA_DADOS + 54:
            break
        if 'Falha' in registro:
            exibir_texto(term, COLUNA_ESQ, linha_y, registro[:99].rstrip('\n'),estilo=term.red)
        elif 'WARNING' in registro:
            exibir_texto(term, COLUNA_ESQ, linha_y, registro[:99].rstrip('\n'),estilo=term.yellow)
        else:
            exibir_texto(term, COLUNA_ESQ, linha_y, registro[:99].rstrip('\n'))
        linha_y += 1

def tela_tag_proximo(term, proxima_execucao='testetagproxima'):
    exibir_texto(term, COLUNA_DIR, LINHA_CABECALHO, f"Próxima Execução:", estilo=term.underline + term.bold_yellow)
    exibir_texto(term, COLUNA_DIR + 18, LINHA_CABECALHO, f" {proxima_execucao}", estilo=term.bold_white)


def tela_superior_dir(term, processos):
    exibir_texto(term, COLUNA_DIR, LINHA_DADOS, "Agendas:", estilo=term.underline + term.bold_yellow)
    freq_dict = {}
    for processo in processos:
        freq = processo['Frequencia']
        freq_dict.setdefault(freq, []).append(processo)

    line = LINHA_DADOS + 1
    for frequencia, procs in freq_dict.items():
        exibir_texto(term, COLUNA_DIR, line, f"- {frequencia.upper()}", estilo=term.bold)
        line += 1
        for proc in procs:
            nome_formatado = proc['Nome']
            ultimo_log = fnc_UltimoLog(proc['Processo'])
            ultimo_log = "" if not ultimo_log else ultimo_log.date()
            exibir_texto(term, COLUNA_DIR, line, f"{nome_formatado:<35} | Classe: {proc['Classe']:<24} | Horário: {proc['Horario']:<5} " f"| Dia: {proc['Dia']:<10} | Intervalo: {proc['Intervalo'][-3:]} |: {ultimo_log}")
            line += 1


def tela_inferior_esq(term):
    exibir_texto(term, COLUNA_ESQ, LINHA_TEMPORIZADOR, "Temporizador:", estilo=term.underline + term.bold_green)


def tela_inferior_sub_dir(term):
    exibir_texto(term, COLUNA_DIR, LINHA_TEMPORIZADOR, "Demandas em Fila:", estilo=term.underline + term.bold_green)

    caminhos = json_caminho('Json_Fila_WA')
    FILA_WA = len(json_dados(os.path.join(caminhos['Diretorio'], caminhos['Arquivo'])))
    caminhos = json_caminho('Json_Falhas_SQL')
    FILA_ERROS = len(json_dados(os.path.join(caminhos['Diretorio'], caminhos['Arquivo'])))
    PROSPECTS = 0
    PROJETOS = 0

    colunas_kpi = ["FILA_WA", "FILA_ERROS", "PROSPECTS", "PROJETOS"]
    valores_kpi = [FILA_WA, FILA_ERROS, PROSPECTS, PROJETOS]

    largura_coluna = 13  # espaçamento entre colunas
    linha_base = LINHA_TEMPORIZADOR + 1  # abaixo do cabeçalho
    for i, nome in enumerate(colunas_kpi):
        coluna = COLUNA_DIR + i * largura_coluna
        exibir_texto(term, coluna, linha_base, nome, estilo=term.bold + term.bold_yellow)
    for i, valor in enumerate(valores_kpi):
        coluna = COLUNA_DIR + i * largura_coluna
        if valor > 0:
            exibir_texto(term, coluna, linha_base + 1, str(valor), estilo=term.bold_red)
        else:
            exibir_texto(term, coluna, linha_base + 1, str(valor), estilo=term.bold_white_on_black)


def tela_inferior_dir(term):
    # Configuração do cabeçalho dos KPIs
    col_base = COLUNA_DIR
    linha_base = LINHA_KPI
    colunas_kpi = ["ATUAL", "YTD", "MTD", "M-1", "M-2", "M-3", "M-4", "M-5", "M-6"]

    resultado_pj = fnc_saldos_por_periodo()
    saldos_pj = resultado_pj["Resultado"]["saldo"]
    notas_pj = resultado_pj["Resultado"]["notas"]

    # resultado_psm = fnc_projetos_por_periodo()
    # saldos_psm = resultado_psm["Resultado"]

    # Título da seção
    exibir_texto(term, col_base, linha_base, "KPIs Operacionais:", estilo=term.underline + term.bold_red)

    # Cabeçalho das colunas
    largura_coluna = 13
    offset_nome_kpi = 20  # espaço reservado para os nomes
    linha_base += 1
    for i, col in enumerate(colunas_kpi):
        exibir_texto(term, col_base + offset_nome_kpi + i * largura_coluna, linha_base, col, estilo=term.bold_yellow)

    # Definição dos KPIs e seus valores
    kpis = [
        {"nome": "NU_DAN_PJ", "valores": [saldos_pj["NU_DAN_PJ"].get(col, 0.0) for col in colunas_kpi]},
        {"nome": "PB_DAN_PJ", "valores": [saldos_pj["PB_DAN_PJ"].get(col, 0.0) for col in colunas_kpi]},
        {"nome": "NU_FULA_PJ", "valores": [saldos_pj["NU_FULA_PJ"].get(col, 0.0) for col in colunas_kpi]},
        {"nome": "PB_FULA_PJ", "valores": [saldos_pj["PB_FULA_PJ"].get(col, 0.0) for col in colunas_kpi]},
        {"nome": "SALDO CONTA TOTAL", "valores": [saldos_pj["SALDO CONTA TOTAL"].get(col, 0.0) for col in colunas_kpi]},
        {"nome": "NF_DAN", "valores": [notas_pj["NF_DAN"].get(col, 0.0) for col in colunas_kpi]},
        {"nome": "NF_FULA EMT", "valores": [notas_pj["NF_FULA EMT"].get(col, 0.0) for col in colunas_kpi]},
        {"nome": "NF_FULA RCB", "valores": [notas_pj["NF_FULA RCB"].get(col, 0.0) for col in colunas_kpi]}
        # {"nome": "total Leads", "valores": [int(saldos_psm.loc[saldos_psm['PERIODO'] == col, 'total Leads'].values[0]) if col in saldos_psm['PERIODO'].values else 0 for col in colunas_kpi]},
        # {"nome": "Leads Válidos", "valores": [int(saldos_psm.loc[saldos_psm['PERIODO'] == col, 'Leads Válidos'].values[0]) if col in saldos_psm['PERIODO'].values else 0 for col in colunas_kpi]},
        # {"nome": "% Sucesso COM", "valores": [round(saldos_psm.loc[saldos_psm['PERIODO'] == col, '% Sucesso COM'].values[0], 2) if col in saldos_psm['PERIODO'].values else 0.0 for col in colunas_kpi]}
    ]

    for kpi_idx, kpi in enumerate(kpis):
        linha_base += 1
        if kpi_idx == 5:
            linha_base += 1  # insere linha em branco antes do 6º KPI
        exibir_texto(term, col_base, linha_base, kpi["nome"], estilo=term.bold_cyan)
        for i, valor in enumerate(kpi["valores"]):
            exibir_texto(term, col_base + offset_nome_kpi + i * largura_coluna, linha_base, str(valor), estilo=term.bold_white)


def desenhar_tela(term, proxima_execucao, processos_filtrados, fake, tempo, executando):
    tela_limpar()
    if executando == True:
        tela_inferior_esq(term)
        tela_tag_proximo(term, proxima_execucao)
        with term.location(0, 59):
            print("Executando Processo " + proxima_execucao + "! Aguarde...")
    else:
        tela_inferior_esq(term)
        tela_tag_proximo(term, proxima_execucao)
        tela_superior_dir(term, processos_filtrados)
        tela_superior_esq(term)
        tela_inferior_dir(term)
        tela_inferior_sub_dir(term)
    if tempo:
        barra_tempo(term, COLUNA_ESQ, LINHA_TEMPORIZADOR+1, 30, 1)
    elif fake:
        barra_fake(term, COLUNA_ESQ, LINHA_TEMPORIZADOR+2, 10, 1)


def main():
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = False
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        # resultado = fnc_LogRecupera('prc_teste_dmb')
        # print(resultado)
        resultado = fnc_UltimoLog('prc_teste_dmb')
        print(resultado)

    except Exception as e:
        exec_info += "\t\t\tM99\n"
        exec_info += f"Traceback: {traceback.format_exc()}"
        varg_erro = True
        raise

    finally:
        exec_info += "LF\n"


if __name__ == "__main__":
    main()