import logging
import traceback
import inspect
import requests
import json
import os
from datetime import datetime
from decouple import config
from SCRIPTS.functions.cls_Logging import main as log_registra
from SCRIPTS.functions.cls_NomeClasse import fnc_NomeClasse


gpt_modelo = "gpt-4o-mini"
gpt_pergunta = """Há três interruptores em uma sala e três lâmpadas incandescentes em outra sala. As lâmpadas estão apagadas e as duas salas estão isoladas uma da outra, nada do que acontece em uma delas pode ser percebido da outra. Cada um dos interruptores acende ou apaga uma das três lâmpadas.  Como descobrir a correspondência entre interruptores e lâmpadas indo uma única vez da sala dos interruptores à sala das
lâmpadas?"""
api_key = config('DANILO_GPT_API')
headers = {"Authorization": f"Bearer {api_key}",
           "Content-Type": "application/json",
           "OpenAI-Client-Options": json.dumps({"user_provided_data": False})}
LOG_FILE = "G:\\Meu Drive\\PSM\\01 - OPERACIONAL\\00_FONTES\\logs\\gpt.json"

# #Modelo get para recuperar os modelos de chatGPT disponíveis.
# link = "https://api.openai.com/v1/models"
# requisicao = requests.get(link,headers=headers)
# print(requisicao)
# print(requisicao.text)

custos = {
    "gpt-3.5-turbo": {"Entrada": 0, "Saida": 0},
    "gpt-4o": {"Entrada": 0, "Saida": 0},
    "gpt-4o-mini": {"Entrada": 0.15/1_000_000, "Saida": 0.6/1_000_000},
    "gpt-4o-mini-audio-preview": {"Entrada": 0.15/1_000_000, "Saida": 0.6/1_000_000}
}


def ler_sumarizar_gpt_log():
    if not os.path.exists(LOG_FILE):
        print("Arquivo de log não encontrado.")
        return

    mes_atual = datetime.now().strftime("%Y%m")  # Exemplo: "202504"
    resumo_tokens = {}
    resumo_custos = {}

    with open(LOG_FILE, "r") as f:
        for linha in f:
            try:
                log = json.loads(linha.strip())
                data_hora = datetime.strptime(log["data_hora"], "%Y-%m-%d %H:%M:%S")
                mes_registro = data_hora.strftime("%Y%m")

                if mes_registro == mes_atual:
                    modelo = log["modelo"]
                    entrada = log.get("prompt", 0)
                    saida = log.get("completion", 0)

                    # Inicializa contadores se necessário
                    if modelo not in resumo_tokens:
                        resumo_tokens[modelo] = {"Entrada": 0, "Saida": 0}
                        resumo_custos[modelo] = 0.0

                    resumo_tokens[modelo]["Entrada"] += entrada
                    resumo_tokens[modelo]["Saida"] += saida

                    if modelo in custos:
                        custo_entrada = entrada * custos[modelo]["Entrada"]
                        custo_saida = saida * custos[modelo]["Saida"]
                        resumo_custos[modelo] += custo_entrada + custo_saida

            except json.JSONDecodeError:
                print(f"Erro ao processar linha: {linha.strip()}")

    print(f"\nResumo do consumo de tokens competencia {mes_atual}")
    print("=" * 80)
    print(f"{'Modelo':<20} {'Entrada':>10} {'Saída':>10} {'Total':>10} {'Custo (USD)':>20}")
    print("-" * 80)

    for modelo, tokens in resumo_tokens.items():
        total = tokens["Entrada"] + tokens["Saida"]
        custo = resumo_custos.get(modelo, 0.0)
        print(f"{modelo:<20} {tokens['Entrada']:>10} {tokens['Saida']:>10} {total:>10} {custo:>20.6f}")

    print("=" * 80)
    return resumo_tokens, resumo_custos


def prc_gpt_registra(modulo, funcao, modelo, key, tokens_usados, prompt, completion, other):
    if not tokens_usados:
        return

    key_masked = f"****{key[-4:]}" if key else "N/A"

    log_entry = {
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modulo": modulo,
        "funcao": funcao,
        "modelo": modelo,
        "key": key_masked,
        "tokens": tokens_usados,
        "prompt": prompt,
        "completion": completion,
        "other": other
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


def fnc_pergunta_gpt(modelo, key, texto):
    log_info = "F1"
    varl_detail = None
    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    other_tokens = 0

    try:
        log_info = "F2"
        link = "https://api.openai.com/v1/chat/completions"
        body = {
            "model": modelo,
            "messages": [{"role": "user", "content": texto}]
        }
        body = json.dumps(body)
        requisicao = requests.post(link, headers=headers, data=body)

        resposta = requisicao.json()

        # Captura a mensagem de retorno
        mensagem = resposta["choices"][0]["message"]["content"]

        # Captura o consumo de tokens
        if "usage" in resposta:
            total_tokens = resposta["usage"]["total_tokens"]
            prompt_tokens = resposta["usage"]["prompt_tokens"]
            completion_tokens = resposta["usage"]["completion_tokens"]

            prompt_tokens_details = resposta["usage"].get("prompt_tokens_details", {})
            completion_tokens_details = resposta["usage"].get("completion_tokens_details", {})
            cached_tokens = prompt_tokens_details.get("cached_tokens", 0)
            audio_tokens = prompt_tokens_details.get("audio_tokens", 0)
            reasoning_tokens = completion_tokens_details.get("reasoning_tokens", 0)
            accepted_prediction_tokens = completion_tokens_details.get("accepted_prediction_tokens", 0)
            rejected_prediction_tokens = completion_tokens_details.get("rejected_prediction_tokens", 0)

            # Soma dos tokens "extras"
            other_tokens = cached_tokens + audio_tokens + reasoning_tokens + accepted_prediction_tokens + rejected_prediction_tokens

        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    finally:
        prc_gpt_registra(__name__, inspect.currentframe().f_code.co_name, modelo, key, total_tokens, prompt_tokens, completion_tokens, other_tokens)

    return {"Resultado": mensagem, "Status_log": log_info, "Detail_log": varl_detail}


def main():
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:

        resultado = fnc_pergunta_gpt(gpt_modelo, api_key, gpt_pergunta)
        exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
        exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
        exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
        ler_sumarizar_gpt_log()

        exec_info += "\t\tMF\n"

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