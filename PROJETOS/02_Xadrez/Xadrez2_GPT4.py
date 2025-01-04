import pygame
import numpy as np

# Constantes
TILE_SIZE = 80
BOARD_SIZE = 8
WINDOW_SIZE = TILE_SIZE * BOARD_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (173, 216, 230)
THREAT_COLOR = (255, 150, 150)

# Inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Jogo de Xadrez")

# Classe para representar o tabuleiro
class Board:
    def _init_(self):
        self.grid = np.array([
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ])

    def draw(self):
        """Desenha o tabuleiro e as peças."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = WHITE if (row + col) % 2 == 0 else BLACK
                pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                piece = self.grid[row][col]
                if piece != " ":
                    self.draw_piece(piece, col, row)

    def draw_piece(self, piece, x, y):
        """Desenha uma peça específica."""
        font = pygame.font.Font(None, 50)
        text = font.render(piece, True, BLACK if piece.isupper() else WHITE)
        text_rect = text.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
        screen.blit(text, text_rect)

    def move_piece(self, start, end):
        """Move uma peça no tabuleiro."""
        piece = self.grid[start[1]][start[0]]
        self.grid[start[1]][start[0]] = " "
        self.grid[end[1]][end[0]] = piece

# Classe para gerenciar o jogo
class Game:
    def _init_(self):
        self.board = Board()
        self.selected_piece = None
        self.valid_moves = []

    def highlight_moves(self):
        """Destaca os movimentos válidos."""
        for move in self.valid_moves:
            pygame.draw.rect(screen, HIGHLIGHT, (move[0] * TILE_SIZE, move[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def highlight_threats(self):
        """Destaca casas ameaçadas."""
        threat_map = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        # Simulação: calcular ameaças básicas
        for i, row in enumerate(self.board.grid):
            for j, piece in enumerate(row):
                if piece.lower() == "p":  # Simula ameaças de peões
                    direction = -1 if piece.isupper() else 1
                    if 0 <= i + direction < BOARD_SIZE:
                        if 0 <= j - 1 < BOARD_SIZE:
                            threat_map[i + direction][j - 1] += 1
                        if 0 <= j + 1 < BOARD_SIZE:
                            threat_map[i + direction][j + 1] += 1
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if threat_map[row][col] > 0:
                    pygame.draw.rect(screen, THREAT_COLOR, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

    def handle_click(self, pos):
        """Lida com cliques do usuário."""
        x, y = pos[0] // TILE_SIZE, pos[1] // TILE_SIZE
        if self.selected_piece:
            self.board.move_piece(self.selected_piece, (x, y))
            self.selected_piece = None
            self.valid_moves = []
        else:
            self.selected_piece = (x, y)
            self.valid_moves = [(x + 1, y + 1), (x + 2, y + 2)]  # Exemplo de movimentos válidos

# Função principal
def main():
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(pygame.mouse.get_pos())

        screen.fill((0, 0, 0))
        game.board.draw()
        game.highlight_threats()
        game.highlight_moves()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()