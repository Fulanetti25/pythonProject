import numpy as np

# Tamanho do tabuleiro
BOARD_SIZE = 8

# Representação do tabuleiro
board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]


def print_board():
    """Imprime o tabuleiro no console."""
    print("\n  a b c d e f g h")
    for i, row in enumerate(board):
        print(f"{8 - i} " + " ".join(row) + f" {8 - i}")
    print("  a b c d e f g h\n")


def get_threat_map():
    """Calcula um mapa de ameaças baseado nas peças no tabuleiro."""
    threat_map = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

    def add_threat(row, col):
        """Adiciona uma ameaça ao mapa se estiver dentro do tabuleiro."""
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            threat_map[row][col] += 1

    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece == " ":
                continue

            is_white = piece.isupper()
            piece = piece.lower()

            if piece == "p":  # Peões
                direction = -1 if is_white else 1
                add_threat(i + direction, j - 1)
                add_threat(i + direction, j + 1)

            elif piece == "n":  # Cavalos
                knight_moves = [
                    (i + 2, j + 1), (i + 2, j - 1), (i - 2, j + 1), (i - 2, j - 1),
                    (i + 1, j + 2), (i + 1, j - 2), (i - 1, j + 2), (i - 1, j - 2),
                ]
                for move in knight_moves:
                    add_threat(*move)

            elif piece == "b":  # Bispos
                for k in range(1, BOARD_SIZE):
                    if not (add_threat(i + k, j + k) or add_threat(i + k, j - k) or
                            add_threat(i - k, j + k) or add_threat(i - k, j - k)):
                        break

            elif piece == "r":  # Torres
                for k in range(1, BOARD_SIZE):
                    if not (add_threat(i + k, j) or add_threat(i - k, j) or
                            add_threat(i, j + k) or add_threat(i, j - k)):
                        break

            elif piece == "q":  # Rainha
                for k in range(1, BOARD_SIZE):
                    if not (add_threat(i + k, j + k) or add_threat(i + k, j - k) or
                            add_threat(i - k, j + k) or add_threat(i - k, j - k) or
                            add_threat(i + k, j) or add_threat(i - k, j) or
                            add_threat(i, j + k) or add_threat(i, j - k)):
                        break

            elif piece == "k":  # Rei
                king_moves = [
                    (i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1),
                    (i + 1, j + 1), (i + 1, j - 1), (i - 1, j + 1), (i - 1, j - 1),
                ]
                for move in king_moves:
                    add_threat(*move)

    return threat_map


def is_king_in_check(is_white):
    """Verifica se o rei está em xeque."""
    threat_map = get_threat_map()
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece == ("K" if is_white else "k"):
                return threat_map[i][j] > 0
    return False


def highlight_threats():
    """Exibe casas ameaçadas com níveis de ameaça."""
    threat_map = get_threat_map()
    print("Casas ameaçadas:")
    for row in threat_map:
        print(" ".join(map(str, row)))
    print()


# Loop principal
while True:
    print_board()
    highlight_threats()
    print(f"Rei Branco em Xeque: {is_king_in_check(True)}")
    print(f"Rei Preto em Xeque: {is_king_in_check(False)}")

    move = input("Digite sua jogada (ex: e2e4) ou 'sair' para encerrar: ").strip()
    if move.lower() == "sair":
        break

    try:
        start_col, start_row = ord(move[0]) - ord('a'), 8 - int(move[1])
        end_col, end_row = ord(move[2]) - ord('a'), 8 - int(move[3])
        piece = board[start_row][start_col]
        board[start_row][start_col] = " "
        board[end_row][end_col] = piece
    except (IndexError, ValueError):
        print("Movimento inválido! Tente novamente.")