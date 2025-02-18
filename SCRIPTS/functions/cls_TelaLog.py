import os
import inspect
import traceback
import time
from blessed import Terminal
from datetime import datetime, timedelta
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_BarraProgresso import barra_Criar, barra_CriarTempo, barra_Atualizar, barra_Finalizar

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


def fn_log_recupera(processo=None, data=None):
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


def fn_ultimo_log(nome_classe):
    registros = fn_log_recupera(nome_classe)

    if registros:
        registros_sucesso = [registro for registro in registros if "Sucesso" in registro]

        if registros_sucesso:
            ultima_execucao_str = registros_sucesso[0].split(',')[0]
            ultima_execucao = datetime.strptime(ultima_execucao_str, '%Y-%m-%d %H:%M:%S')
            return ultima_execucao
    else:
        return None


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
        fake = barra_Criar(total=total, cor_barra="blue", cor_fonte="white")
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
    registros = fn_log_recupera()
    linha_y = LINHA_DADOS + 1
    for registro in registros:
        if linha_y >= LINHA_DADOS + 54:
            break
        if 'Falha' in registro:
            exibir_texto(term, COLUNA_ESQ, linha_y, registro[:99].rstrip('\n'),estilo=term.red)
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
            ultimo_log = fn_ultimo_log(proc['Classe'])
            ultimo_log = "" if not ultimo_log else ultimo_log.date()
            exibir_texto(term, COLUNA_DIR, line, f"{nome_formatado:<40} | Classe: {proc['Classe']:<20} | Horário: {proc['Horario']:<5} " f"| Dia: {proc['Dia']:<10} | Intervalo: {proc['Intervalo'][-3:]} |: {ultimo_log}")
            line += 1


def tela_inferior_esq(term):
    exibir_texto(term, COLUNA_ESQ, LINHA_TEMPORIZADOR, "Temporizador:", estilo=term.underline + term.bold_green)


def tela_inferior_dir(term):
    # Configuração do cabeçalho dos KPIs
    col_base = COLUNA_DIR
    linha_base = LINHA_KPI
    meses = ["ATUAL", "DEZ_24", "NOV_24", "OUT_24", "SET_24"]  # Substituir pelos meses relevantes

    # Título da seção
    exibir_texto(term, col_base, linha_base, "KPIs Operacionais:", estilo=term.underline + term.bold_red)

    # Cabeçalho das colunas
    linha_base += 1
    for i, mes in enumerate(meses):
        exibir_texto(term, col_base + i * 15, linha_base, mes, estilo=term.bold_white)

    # Definição dos KPIs e seus valores
    kpis = [
        {"nome": "Conta PF Saldo", "valores": [15000, 14500, 14000, 13000, 12500]},
        {"nome": "Conta PJ Saldo", "valores": [75000, 74000, 73000, 72000, 71000]},
        {"nome": "Valor Comprometido", "valores": [20000, 19500, 19000, 18000, 17500]},
        {"nome": "Ticket Médio", "valores": [500, 510, 520, 530, 540]},
        {"nome": "Projetos", "valores": [10, 9, 8, 7, 6]},
        {"nome": "% Sucesso Comercial", "valores": [95, 93, 90, 88, 85]},
        {"nome": "% Sucesso Desenvolvimento", "valores": [90, 89, 88, 87, 85]},
    ]

    # Exibição dos KPIs
    for kpi_idx, kpi in enumerate(kpis):
        linha_base += 1
        exibir_texto(term, col_base, linha_base, kpi["nome"], estilo=term.bold_cyan)
        for i, valor in enumerate(kpi["valores"]):
            exibir_texto(term, col_base + i * 15, linha_base, str(valor), estilo=term.bold_white)


def desenhar_tela(term, proxima_execucao, processos_filtrados, fake=False, tempo=True, executando = True):
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
    if tempo:
        barra_tempo(term, COLUNA_ESQ, LINHA_TEMPORIZADOR+1, 30, 1)
    if fake:
        barra_fake(term, COLUNA_ESQ, LINHA_TEMPORIZADOR+2, 10, 1)


def main():
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = False

    term = Terminal()
    proxima_execucao = "Teste Proxima"

    processos = json_caminho('Json_Processos')
    info_processos = json_dados(os.path.join(processos['Diretorio'], processos['Arquivo']))
    lista_processos = info_processos["processos"]
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            while True:
                desenhar_tela(term, proxima_execucao, lista_processos, True)
                time.sleep(3)

    except Exception as e:
        exec_info += "\t\t\tM99\n"
        exec_info += f"Traceback: {traceback.format_exc()}"
        varg_erro = True
        raise

    finally:
        exec_info += "LF\n"


if __name__ == "__main__":
    main()
    print(exec_info)