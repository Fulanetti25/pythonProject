from tst_blessed import Terminal
import time

# Instância do terminal
term = Terminal()

# Variáveis de teste
progresso = 0
agenda = [
    {"Nome": "Processo A", "Horario": "08:00"},
    {"Nome": "Processo B", "Horario": "12:00"},
    {"Nome": "Processo C", "Horario": "16:00"},
]
logs = ["Log Iniciado.", "Principal Iniciado.", "Processo A Executado.", "Log Finalizado."]

# Função para exibir a barra de progresso
def desenha_barra_progresso(progresso, total=100, largura=30):
    completado = int((progresso / total) * largura)
    barra = "=" * completado + "-" * (largura - completado)
    return f"[{barra}] {progresso}%"

# Função principal
def main():
    global progresso  # Declara a variável como global
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            # Limpa a tela antes de desenhar a próxima
            print(term.clear())

            with term.location(0, 0):  # Reseta o cursor
                # Cabeçalho
                print(term.bold(term.blue("Gerenciador de Processos - Agenda")))

                # Parte Superior Esquerda: Barra de Progresso e Tempo Restante
                print(term.bold("\n[Parte Superior Esquerda]"))
                print(f"Progresso da tarefa atual: {desenha_barra_progresso(progresso)}")
                print(f"Tempo para próxima execução: {60 - progresso} segundos")

                # Parte Superior Direita: Agenda
                print(term.bold("\n[Parte Superior Direita]"))
                print("Agenda de Execuções:")
                for item in agenda:
                    print(f"- {item['Nome']} às {item['Horario']}")

                # Parte Inferior Esquerda: Logs
                print(term.bold("\n[Parte Inferior Esquerda]"))
                print("Logs:")
                for log in logs[-5:]:  # Mostra os últimos 5 logs
                    print(f"> {log}")

            # Simula progresso (remova isso no código final)
            time.sleep(1)
            progresso += 5
            if progresso > 100:
                progresso = 0
                logs.append("Nova tarefa concluída.")

# Executa o programa
if __name__ == "__main__":
    main()


#interação com a tela
import time
from blessed import Terminal

term = Terminal()

def exibir_texto(term, x, y, texto, estilo=None):
    with term.location(x, y):
        if estilo:
            print(estilo + texto + term.normal)
        else:
            print(texto)

def interagir(term):
    with term.cbreak(), term.hidden_cursor():
        while True:
            exibir_texto(term, 0, 0, "Pressione 'q' para sair ou 'a' para interagir", estilo=term.bold_green)
            tecla = term.inkey(timeout=1)  # Timeout para continuar o loop
            if tecla == 'q':
                break
            elif tecla == 'a':
                exibir_texto(term, 0, 1, "Você pressionou 'a'!", estilo=term.bold_red)

interagir(term)
