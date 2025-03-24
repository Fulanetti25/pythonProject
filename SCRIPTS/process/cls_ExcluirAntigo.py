import os
import datetime


def listar_maiores_arquivos(drive='G:\\', top_n=100):
    arquivos = []

    for root, _, files in os.walk(drive):
        for file in files:
            caminho_completo = os.path.join(root, file)
            try:
                tamanho = os.path.getsize(caminho_completo)
                data_modificacao = os.path.getmtime(caminho_completo)
                arquivos.append((caminho_completo, tamanho, data_modificacao))
            except Exception as e:
                print(f"Erro ao processar {caminho_completo}: {e}")

    # Ordena os arquivos pelo tamanho (maior para menor)
    arquivos.sort(key=lambda x: x[1], reverse=True)

    # Exibe os top_n arquivos
    print(f"Top {top_n} maiores arquivos no drive {drive}:\n")
    for i, (caminho, tamanho, data_modificacao) in enumerate(arquivos[:top_n], 1):
        data_formatada = datetime.datetime.fromtimestamp(data_modificacao).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {caminho}\n   Tamanho: {tamanho / (1024 ** 2):.2f} MB\n   Última modificação: {data_formatada}\n")


if __name__ == "__main__":
    listar_maiores_arquivos()
