import json
from datetime import datetime

def json_caminho(nome = 'Json_Caminhos'):
     try:
        with open(r"C:\Users\paulo\OneDrive\Documentos\github\pythonProject\SCRIPTS\config\caminhos.json", "r", encoding="utf-8") as arquivo_json:
            dados = json.load(arquivo_json)
            caminhos = dados.get("caminhos", [])
            resultado = next((item for item in caminhos if item.get('Nome') == nome), None)
            return resultado if resultado else {}
     except FileNotFoundError:
        print("Arquivo não encontrado.")
        return []
     except json.JSONDecodeError:
        print("Erro ao ler o arquivo JSON.")
        return []


def json_dados(arquivo):
    try:
        with open(arquivo, "r", encoding="utf-8") as arquivo_json:
            dados = json.load(arquivo_json)
            return dados if dados else {}
    except FileNotFoundError:
        print("Arquivo não encontrado.")
        return []
    except json.JSONDecodeError as e:
        print("Erro ao ler o arquivo JSON.")
        print(f"Erro ao ler o arquivo JSON: {e}")
        return []


def json_registra(dados, arquivo):
    try:
        with open(arquivo, "w", encoding="utf-8") as arquivo_json:
            json.dump(dados, arquivo_json, indent=4, ensure_ascii=False)
        print(f"Arquivo salvo com sucesso em: {arquivo}")
    except IOError as e:
        print(f"Erro ao escrever no arquivo JSON: {e}")


def json_limpa(arquivo, filtro_server):
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados_filtrados = [item for item in dados if item.get("server") != filtro_server]
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados_filtrados, f, indent=4, ensure_ascii=False)
        print(f"Arquivo JSON limpo com filtro: {filtro_server} => {arquivo}")
    except Exception as e:
        print(f"Erro ao limpar com filtro o arquivo JSON: {e}")


def json_atualiza(arquivo, grupo, nome, campo, atualizacao):
    try:
        with open(arquivo, "r", encoding="utf-8") as arquivo_json:
            dados = json.load(arquivo_json)
            dados_grupo = dados.get(grupo, [])
            registro = next((item for item in dados_grupo if item.get('Nome') == nome), None)

        if registro:
            if atualizacao:
                registro[campo] = atualizacao
            else:
                print(f"A chave '{campo}' não foi encontrada no registro.")

            with open(arquivo, "w", encoding="utf-8") as arquivo_json:
                json.dump(dados, arquivo_json, indent=4, ensure_ascii=False)
            print(f"Registro '{nome}' atualizado com sucesso.")
        else:
            print(f"Registro com o nome '{nome}' não encontrado.")
    except FileNotFoundError:
        print("Arquivo não encontrado.")
    except json.JSONDecodeError as e:
        print(f"Erro ao ler o arquivo JSON: {e}")
    except IOError as e:
        print(f"Erro ao acessar o arquivo JSON: {e}")


def main():
    print(json_caminho())


if __name__ == "__main__":
    main()