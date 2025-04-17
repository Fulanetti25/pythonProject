import os
import logging
import traceback
import inspect
from blessed import Terminal
from datetime import datetime, timedelta
from SCRIPTS.functions.cls_TelaLog import desenhar_tela, fn_ultimo_log
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_CarregaJson import json_caminho, json_dados
from SCRIPTS.functions.cls_DiasUteis import df_DiasUteis
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse
from SCRIPTS.process.cls_Exporta import main as exporta_main
from SCRIPTS.process.cls_GooglePalavras import main as google_main
from SCRIPTS.process.cls_VerificaMail import main as leads_main
from SCRIPTS.process.cls_GanttProjetos import main as gantt_main
from SCRIPTS.process.cls_LimpaLogs import main as limpeza_logs
from SCRIPTS.process.cls_AtualizaFonteLocal import main as fontes_local
from SCRIPTS.process.cls_AtualizaFonteOnline import main as fontes_online
from SCRIPTS.process.cls_LimpaGoogleDrive import main as limpeza_drive
from SCRIPTS.process.cls_FFMPEG_Video import main as processa_videos
from SCRIPTS.process.cls_FFMPEG_Video import main as processa_tbt


def etl_VerificaAgendamento(processo, horario_atual):
    return processo['Horario'] == horario_atual.strftime("%H:%M")

def etl_ExecutaProcesso(processo,proxima_execucao):
    log_info = "F1"
    varl_detail = None

    try:
        if processo != "N/A":
            log_info = "F2"

            nome_processo = processo['Processo']
            desenhar_tela(term, proxima_execucao:= nome_processo,None,fake:=True, tempo:=False, executando:=True)

            func = globals().get(nome_processo)
            if func:
                resultado = func()
            else:
                ValueError(f"Função {nome_processo} não encontrada.")

        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    finally:
        pass

    return {"Resultado": str(nome_processo), 'Status_log': log_info, 'Detail_log': varl_detail}

def main():
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    global term
    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None

    term = Terminal()
    proxima_execucao = None
    processos_futuros = None

    df_data = df_DiasUteis(datetime.now(), datetime.now())
    dia_semana = df_data['Resultado'].iloc[0]['dia_semana']
    dia_util = df_data['Resultado'].iloc[0]['util']

    horarios = json_caminho('Json_Horarios')
    info_horarios = json_dados(os.path.join(horarios['Diretorio'], horarios['Arquivo']))
    lista_horarios = info_horarios["horarios"]
    horarios_filtrados = [horario for horario in lista_horarios if horario["Dia"] == dia_semana]
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            while True:
                horario_atual = datetime.now()
                processos = json_caminho('Json_Processos')
                info_processos = json_dados(os.path.join(processos['Diretorio'], processos['Arquivo']))
                lista_processos = info_processos["processos"]
                processos_filtrados = [processo for processo in lista_processos
                                       if processo["Dia"] == dia_semana
                                       or processo["Dia"] == "All"
                                       or (processo["Dia"] == "Util" and dia_util)]

                # Inicia Execucao
                if horarios_filtrados[0]["HorarioMinimo"] <= horario_atual.strftime("%H:%M") <= horarios_filtrados[0]["HorarioMaximo"]:
                    if processos_futuros:
                        for processo in processos_futuros:
                            if etl_VerificaAgendamento(processo, horario_atual):
                                resultado = etl_ExecutaProcesso(processo, proxima_execucao)
                                exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
                                exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
                                exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
                    desenhar_tela(term, proxima_execucao, processos_filtrados, False, True, False)
                    varg_erro = False
                else:
                    print(f"Fora do horário permitido ({dia_semana}, das {horarios_filtrados[0]["HorarioMinimo"]} as {horarios_filtrados[0]["HorarioMaximo"]}). \nAguardando próximo intervalo.")
                    if horario_atual.strftime("%H:%M") >= horarios_filtrados[0]["HorarioMaximo"]:
                        break

                # Inicia Agendamento
                for processo in processos_filtrados:
                    ultimo = fn_ultimo_log(processo['Classe'])
                    horario_processo = datetime.strptime(processo['Horario'], "%H:%M")
                    if processo['Classe'] != "N/A":
                        if processo["Frequencia"] == "Diario":
                            if processo['Predecessor'] != 'N/A':
                                ultimo_predecessor = fn_ultimo_log(processo['Predecessor'])
                                if ultimo_predecessor.date() == horario_atual.date():
                                    if ultimo.date() != horario_atual.date():
                                        while horario_processo <= horario_atual:
                                            horario_processo = horario_processo + timedelta(hours=int(1), minutes=int(0))
                                        processo['Horario'] = horario_processo.strftime("%H:%M")
                            else:
                                if ultimo:
                                    if horario_atual.date() != ultimo.date() and horario_processo < horario_atual:
                                        while horario_processo <= horario_atual:
                                            horario_processo = horario_processo + timedelta(hours=int(1), minutes=int(0))
                                        processo['Horario'] = horario_processo.strftime("%H:%M")
                                else:
                                    processo['Horario'] = horario_processo.strftime("%H:%M")
                        if processo["Frequencia"] == "Intervalo":
                            if processo["Intervalo"] != "N/A":
                                intervalo = timedelta(hours=int(processo['Intervalo'].split(":")[0]), minutes=int(processo['Intervalo'].split(":")[1]))
                                while horario_processo <= horario_atual:
                                    horario_processo += intervalo
                                processo['Horario'] = horario_processo.strftime("%H:%M")
                processos_futuros = [horario for horario in processos_filtrados if
                                     horario["Horario"] >= datetime.now().strftime('%H:%M')]
                if processos_futuros:
                    proximo_horario = min(processos_futuros, key=lambda x: x["Horario"])
                    proxima_execucao = f"{proximo_horario['Nome']}, {proximo_horario['Horario']}"
                else:
                    proxima_execucao = "Nenhuma execução programada."
                #exec_info += "\t\tMF\n"

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
    print(f"Horario de Execução Diario Encerrado!")