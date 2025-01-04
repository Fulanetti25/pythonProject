import tst_curses
import time

# Configuração inicial
TAMANHO_SUP_ESQUERDA = 5  # Linhas da parte superior esquerda
TAMANHO_SUP_DIREITA = 5  # Linhas da parte superior direita

def iniciar_tela(stdscr):
    curses.curs_set(0)  # Ocultar o cursor
    stdscr.clear()

    # Calcula os tamanhos dos quadrantes
    altura, largura = stdscr.getmaxyx()
    metade_largura = largura // 2

    # Janela 1: Superior Esquerda
    janela_superior_esquerda = stdscr.subwin(TAMANHO_SUP_ESQUERDA, metade_largura, 0, 0)
    janela_superior_esquerda.box()
    janela_superior_esquerda.addstr(0, 2, " Tempo e Progresso ")

    # Janela 2: Superior Direita
    janela_superior_direita = stdscr.subwin(TAMANHO_SUP_DIREITA, largura - metade_largura, 0, metade_largura)
    janela_superior_direita.box()
    janela_superior_direita.addstr(0, 2, " Agenda ")

    # Janela 3: Inferior Esquerda
    altura_inferior = altura - TAMANHO_SUP_ESQUERDA
    janela_inferior = stdscr.subwin(altura_inferior, largura, TAMANHO_SUP_ESQUERDA, 0)
    janela_inferior.box()
    janela_inferior.addstr(0, 2, " Logs ")

    # Atualiza as janelas
    while True:
        # Simula uma barra de progresso no setor superior esquerdo
        janela_superior_esquerda.addstr(1, 2, "Aguardando próximo agendamento...")
        for i in range(1, metade_largura - 2):
            time.sleep(0.1)
            janela_superior_esquerda.addch(2, i, '=')
            janela_superior_esquerda.refresh()

        # Exemplo de escrita na janela superior direita
        janela_superior_direita.addstr(1, 2, "Processo 1: 06:00")
        janela_superior_direita.addstr(2, 2, "Processo 2: 12:00")
        janela_superior_direita.refresh()

        # Exemplo de log na janela inferior
        janela_inferior.addstr(1, 2, "Log Iniciado.")
        janela_inferior.addstr(2, 2, "Processo executado com sucesso.")
        janela_inferior.refresh()

        time.sleep(5)  # Simula uma espera antes de reiniciar o ciclo
        break

# Executa a interface
curses.wrapper(iniciar_tela)
