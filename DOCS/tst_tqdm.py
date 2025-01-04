from tst_tqdm import tqdm
import time

# EXEMPLO 1: Função para aplicar cor ao texto (usando códigos ANSI)
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


# Função para barra de progresso personalizada
def barra_progresso_corrigida(total=100, delay=0.05, cor_barra="green", cor_fonte="cyan", cor_percentual="yellow",
                              cor_contador="blue"):
    # Personaliza os textos coloridos
    desc = colorir_texto("Processando:", cor_fonte)  # Descrição colorida
    bar_format = (
        f"{desc} "  # Adiciona a descrição diretamente
        f"{colorir_texto('{percentage:3.0f}%', cor_percentual)}| "  # Percentual colorido
        f"{colorir_texto('{bar}', cor_barra)} "  # Barra de progresso colorida
        f"{colorir_texto('{n_fmt}/{total_fmt}', cor_contador)}"  # Contador colorido
    )

    for _ in tqdm(
            range(total),
            ncols=70,
            bar_format=bar_format,
            colour=cor_barra
    ):
        time.sleep(delay)


# Exemplo de uso
barra_progresso_corrigida(
    cor_barra="#FF5733",
    cor_fonte="white",
    cor_percentual="cyan",
    cor_contador="white"
)

# EXEMPLO 2: Função para usar um contador numérico
def barra_progresso_numerico(total=100):
    contador = 0
    for _ in tqdm(range(total), desc="Processando", ncols=70):
        contador += 1  # Simula uma operação ou trabalho
        # Aqui você poderia colocar algum processamento real se necessário
    print(f"Contador final: {contador}")

# Exemplo de uso
barra_progresso_numerico()

# EXEMPLO 3: Função para usar um contador pesado
def barra_progresso_calculo(total=100):
    resultado = 0
    for i in tqdm(range(total), desc="Calculando", ncols=70):
        resultado += i ** 2  # Simula um trabalho de cálculo
    print(f"Resultado final: {resultado}")

barra_progresso_calculo()


# EXEMPLO 3: Função para simular um processo com múltiplos passos e barra de progresso
from tst_tqdm import tqdm
import time
def barra_progresso_em_fases(total=100, fases=5):
    # Cria a barra de progresso inicial
    progresso = tqdm(total=total, desc="Iniciando processo", ncols=70)

    for fase in range(1, fases + 1):
        # Simula um processamento para cada fase
        for _ in range(total // fases):  # Divide o total em partes
            time.sleep(0.1)  # Simula algum trabalho
            progresso.update(1)  # Atualiza a barra
        progresso.set_postfix(f"Fase {fase}/{fases}")  # Exibe o status da fase
    progresso.close()  # Fecha a barra de progresso no final


# Exemplo de uso
barra_progresso_em_fases(total=100, fases=5)

# EXEMPLO 4: Barra Regressiva
from tst_tqdm import tqdm
import time

# Função de barra regressiva corrigida
def criar_tempo_regressivo(total=60):
    return tqdm(total=total, ncols=70, desc="Regressivo")

def atualizar_tempo_regressivo(tempo, incremento=1):
    tempo.update(incremento)  # A barra só aceita incrementos, então trabalhamos com o total invertido

def finalizar_tempo_regressivo(tempo):
    tempo.close()

# Teste funcional
total_tempo = 60
tempo = criar_tempo_regressivo(total=total_tempo)

for i in range(total_tempo, 0, -1):  # Contagem regressiva
    print(i)  # Mostra o número regressivo
    atualizar_tempo_regressivo(tempo, incremento=1)  # Incrementa para a barra atingir o total
    time.sleep(1)  # Intervalo

finalizar_tempo_regressivo(tempo)
