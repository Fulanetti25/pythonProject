import json
from decouple import config
from datetime import datetime

caminho_default = config('CAMINHOS_DEFAULT')

class JsonHandler:
    """
    Gerencia registros de arquivos .json.
    """
    def __init__(self, base_path_config=None):
        self.base_path_config = base_path_config or caminho_default


    def buscar_caminho(self, nome='Json_Caminhos'):
        try:
            with open(f"{self.base_path_config}/caminhos.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
                caminhos = dados.get("caminhos", [])
                return next((item for item in caminhos if item.get("Nome") == nome), {})
        except FileNotFoundError:
            print(f"{nome} não encontrado.")
            return []
        except json.JSONDecodeError:
            print("Erro ao ler o arquivo JSON.")
            return []


    def carregar(self, arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados if dados else {}
        except FileNotFoundError:
            print(f"{arquivo} não encontrado.")
            return []
        except json.JSONDecodeError as e:
            print(f"Erro ao ler o arquivo JSON: {e}")
            return []


    def salvar(self, dados, arquivo):
        try:
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            print(f"Arquivo salvo com sucesso em: {arquivo}")
        except IOError as e:
            print(f"Erro ao escrever no arquivo JSON: {e}")


def deletar_por_filtro(self, arquivo, filtro_server, filtro_data):
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados_filtrados = [item for item in dados if
                           not (item.get("server") == filtro_server and item.get("data") == filtro_data)]
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados_filtrados, f, indent=4, ensure_ascii=False)
        print(f"Deletado um registro com filtro: {filtro_server}")
    except Exception as e:
        print(f"Erro ao limpar com filtro o arquivo JSON: {e}")


def atualizar(self, arquivo, grupo, nome, campo, novo_valor):
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            dados_grupo = dados.get(grupo, [])
            registro = next((item for item in dados_grupo if item.get("Nome") == nome), None)

        if registro:
            if novo_valor:
                registro[campo] = novo_valor
            else:
                print(f"A chave '{campo}' não foi encontrada no registro.")

            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            print(f"Registro '{nome}' atualizado com sucesso.")
        else:
            print(f"Registro com o nome '{nome}' não encontrado.")
    except FileNotFoundError:
        print(f"{arquivo} não encontrado.")
    except json.JSONDecodeError as e:
        print(f"Erro ao ler o arquivo JSON: {e}")
    except IOError as e:
        print(f"Erro ao acessar o arquivo JSON: {e}")


if __name__ == "__main__":
    j = JsonHandler()
    caminho = j.buscar_caminho("Json_Caminhos")
    print(caminho)