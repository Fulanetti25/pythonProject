import json
from datetime import datetime

def json_caminho(nome = 'Json_Caminhos'):
     try:
        with open(r"C:\Users\paulo\OneDrive\Documentos\Programação\pythonProject\SCRIPTS\config\caminhos.json", "r", encoding="utf-8") as arquivo_json:
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


def json_dados(arquivo=r'C:\Users\paulo\OneDrive\Documentos\Programação\pythonProject\SCRIPTS\config\caminhos.json'):
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


def json_registra(dados, arquivo=r"G:\Meu Drive\PSM\01 - OPERACIONAL\00_FONTES\logs\falhas_sql.json"):
    try:
        with open(arquivo, "w", encoding="utf-8") as arquivo_json:
            json.dump(dados, arquivo_json, indent=4, ensure_ascii=False)
        print(f"Arquivo salvo com sucesso em: {arquivo}")
    except IOError as e:
        print(f"Erro ao escrever no arquivo JSON: {e}")


def json_limpa(arquivo):
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        print(f"Arquivo JSON limpo com sucesso: {arquivo}")
    except IOError as e:
        print(f"Erro ao limpar o arquivo JSON: {e}")


def main():
    print(json_caminho())
    print(json_dados())
    dados_teste = {"server": "server_teste", "log": "log_teste", "query": "query_teste", "params": "params_teste",	"timestamp": str(datetime.now())}
    print(json_registra(dados_teste))


if __name__ == "__main__":
    main()