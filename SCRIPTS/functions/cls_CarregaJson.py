import json

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

def main():
    print(json_caminho())
    print(json_dados())

if __name__ == "__main__":
    main()