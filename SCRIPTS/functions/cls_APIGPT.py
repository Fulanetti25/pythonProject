import logging
import traceback
import inspect
import requests
import json
import os
import re
import tiktoken
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


def fnc_estimar_tokens(modelo, texto):
    try:
        encoding = tiktoken.encoding_for_model(modelo)
    except:
        encoding = tiktoken.get_encoding("cl100k_base")  # fallback genérico
    tokens = encoding.encode(texto)
    return len(tokens)


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


def fnc_pergunta_gpt_com_temperature(modelo = None, key = None, texto = None, temperature = None):
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
            "model": gpt_modelo,
            "max_tokens": 1000,
            "temperature": temperature,
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


def prc_traduzir_lrc_musica(caminho_arquivo_lrc, artista, estilo, idioma_origem="en", idioma_destino="pt", modelo="gpt-4o-mini", temperature=None):
    log_info = "F1"
    varl_detail = None

    try:
        log_info = "F2"
        with open(caminho_arquivo_lrc, 'r', encoding='utf-8') as file:
            linhas = file.readlines()

        padrao_linha_com_tempo = re.compile(r"^\[(\d{2}:\d{2}\.\d{2})\](.*)")
        linhas_para_traduzir = []
        estrutura_lrc = []

        for linha in linhas:
            linha = linha.rstrip('\n')
            match = padrao_linha_com_tempo.match(linha)
            if match:
                tempo, texto = match.groups()
                linhas_para_traduzir.append((tempo, texto.strip()))
                estrutura_lrc.append(("tradução", tempo))  # marcador de posição
            else:
                estrutura_lrc.append(("fixo", linha))  # manter linha como está
        trecho_para_gpt = "\n".join([f"[{tempo}]{texto}" for tempo, texto in linhas_para_traduzir])

        log_info = "F3"
        prompt = f"""
    Você é um tradutor especializado em letras de música. Sua função é traduzir do {idioma_origem.upper()} para o {idioma_destino.upper()} mantendo:
    
    - O estilo e musicalidade do artista ({estilo}).
    - O sentido emocional original do artista ({artista}).
    - Adaptação de expressões idiomáticas quando necessário.
    - Gramática correta, mas sem remover a "voz" artística.
    
    Abaixo está a letra com marcações de tempo. Traduza **apenas os trechos da letra**, mantendo os tempos **exatamente como estão**:
    {trecho_para_gpt}
    
    Importante:
    - Não altere os tempos entre colchetes.
    - Não explique nada, apenas devolva as linhas traduzidas.
    - Mantenha uma linha por tempo, sem adicionar quebras extras.
    """
        log_info = "F4"
        tokens_entrada = fnc_estimar_tokens(modelo, prompt)
        tokens_saida = tokens_entrada
        custo_por_token_entrada = custos.get(modelo, {}).get("Entrada", 0)
        custo_por_token_saida = custos.get(modelo, {}).get("Saida", 0)
        custo_estimado = (tokens_entrada * custo_por_token_entrada) + (tokens_saida * custo_por_token_saida)
        print(f"Custo estimado: R$ {custo_estimado}:.6f no modelo {modelo} para {tokens_entrada} + {tokens_saida} tokens.")
        confirmacao = input("Deseja continuar com a tradução? [s/n]: ").lower()
        if confirmacao != 's':
            print("Tradução cancelada pelo usuário.")
            return {"Resultado": None, 'Status_log': 'F_CANCELADA', 'Detail_log': 'Usuário cancelou após estimativa de custo.'}

        resposta = fnc_pergunta_gpt_com_temperature(modelo, api_key, prompt, temperature=temperature)
        linhas_traduzidas = resposta["Resultado"].splitlines()

        log_info = "F5"
        resultado_final = []
        idx_trad = 0
        for tipo, conteudo in estrutura_lrc:
            if tipo == "fixo":
                resultado_final.append(conteudo)
            else:
                if idx_trad < len(linhas_traduzidas):
                    resultado_final.append(linhas_traduzidas[idx_trad])
                    idx_trad += 1
                else:
                    resultado_final.append("[ERRO: Tradução ausente]")

        log_info = "F6"
        caminho_saida = caminho_arquivo_lrc.replace("LEGENDA", "TRADUCAO")
        with open(caminho_saida, 'w', encoding='utf-8') as file:
            file.write("\n".join(resultado_final))

        log_info = "F0"

    except Exception as e:
        varl_detail = f"Erro na etapa {log_info}, {e}"
        log_registra(__name__, inspect.currentframe().f_code.co_name, var_detalhe=varl_detail, var_erro=True)
        log_info = "F99"
        raise

    finally:
        pass

    return {"Resultado": caminho_saida, 'Status_log': log_info, 'Detail_log': varl_detail}


def main(caminho=r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\FILA', arquivo =  r'LEGENDA - Dua Lipa - Dance The Night.lrc'):
    varg_modulo = fnc_NomeClasse(str(inspect.stack()[0].filename))
    global exec_info
    exec_info = "\nLI\n"

    exec_info += "\tGI\n"
    varg_erro = None
    exec_info += "\tGF\n"

    exec_info += "\t\tMI\n"
    try:
        caminho_arquivo_lrc = os.path.join(caminho,arquivo)
        partes = caminho_arquivo_lrc.split(" - ")
        artista = partes[1].strip()
        estilo = "rock moderno"
        confirmacao = input(f"Deseja traduzir '{artista}', estilo '{estilo}'? [s/n]: ").strip().lower()
        if confirmacao == "n":
            novo_estilo = input(
                f"Digite um novo estilo para '{artista}' ou pressione Enter para manter '{estilo}': ").strip()
            if novo_estilo:
                estilo = novo_estilo

        confirmacao_final = input(f"Confirma traduzir '{artista}' no estilo '{estilo}'? [s/n]: ").strip().lower()
        if confirmacao_final == "s":
            print(f"Traduzindo '{artista}' no estilo '{estilo}'...")
            resultado = prc_traduzir_lrc_musica(caminho_arquivo_lrc, artista, estilo, idioma_origem="en", idioma_destino="pt", modelo="gpt-4o-mini", temperature=0.7)
            exec_info += f"\t\t\t\tResultado: {resultado['Resultado']}\n"
            exec_info += f"\t\t\t\tStatus: {resultado['Status_log']}\n"
            exec_info += f"\t\t\t\tDetail: {resultado['Detail_log']}\n"
            ler_sumarizar_gpt_log()
        else:
            print("Tradução cancelada.")

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