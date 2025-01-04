# Revisada em 2024-12-03
from tqdm import tqdm
import time

def colorir_texto(texto, cor="reset"):
    cores = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    return f"{cores.get(cor, cores['reset'])}{texto}{cores['reset']}"

def barra_Criar(total=100, cor_barra="blue", cor_fonte="white", cor_percentual="green", cor_contador="red", leave = False):
    desc = colorir_texto("Processando:", cor_fonte)  # Descrição colorida
    bar_format = (
        f"{desc} "  # Adiciona a descrição diretamente
        f"{colorir_texto('{percentage:3.0f}%', cor_percentual)}| "  # Percentual colorido
        f"{colorir_texto('{bar}', cor_barra)} "  # Barra de progresso colorida
        f"{colorir_texto('{n_fmt}/{total_fmt}', cor_contador)}"  # Contador colorido
    )

    progresso = tqdm(total=total, ncols=70, bar_format=bar_format, colour=cor_barra, leave=leave)
    return progresso

def barra_CriarTempo(total=100, cor_barra="yellow", cor_fonte="yellow", cor_percentual="yellow", cor_contador="yellow", leave = False):
    desc = colorir_texto("Aguardando.:", cor_fonte)  # Descrição colorida
    bar_format = (
        f"{desc} "  # Adiciona a descrição diretamente
        f"{colorir_texto('{percentage:3.0f}%', cor_percentual)}| "  # Percentual colorido
        f"{colorir_texto('{bar}', cor_barra)} "  # Barra de progresso colorida
        f"{colorir_texto('{n_fmt}/{total_fmt}', cor_contador)}"  # Contador colorido
    )

    progresso = tqdm(total=total, ncols=70, bar_format=bar_format, colour=cor_barra, leave=leave)
    return progresso

def barra_Atualizar(progresso, incremento=1):
    progresso.update(incremento)  # Avança a barra conforme o incremento

def barra_Finalizar(progresso):
    progresso.n = progresso.total  # Garante que a barra está no total
    progresso.last_print_n = progresso.total  # Atualiza o estado interno para refletir 100%
    progresso.colour = "white"  # Define a cor verde para indicar sucesso
    progresso.refresh()  # Atualiza visualmente a barra para refletir as mudanças
    progresso.set_postfix({"status": "Completado"})  # Mostra o status final
    progresso.close()  # Fecha a barra

if __name__ == "__main__":
    progresso = barra_Criar(total=100)
    for i in range(1, 101):
        barra_Atualizar(progresso, incremento=1)
        time.sleep(0.1)
    barra_Finalizar(progresso)