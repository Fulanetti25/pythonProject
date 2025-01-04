import pygame
import os
import numpy as np

# Inicialização do Pygame
pygame.init()

# Configurações da janela e tabuleiro
TILE_SIZE = 80
BOARD_SIZE = 8
WINDOW_SIZE = TILE_SIZE * BOARD_SIZE
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Xadrez Profissional")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (173, 216, 230)
THREAT_COLOR = (255, 100, 100)

# Recursos de mídia (caminho para imagens e sons)
ASSETS_PATH = "assets/"
PIECES = {}
SOUNDS = {}

def load_assets():
    """Carrega as imagens e sons necessários."""
    piece_names = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
    for color in ['white', 'black']:
        for piece in piece_names:
            PIECES[f"{color}_{piece}"] = pygame.image.load(
                os.path.join(ASSETS_PATH, f"{color}_{piece}.png")
            )
            PIECES[f"{color}_{piece}"] = pygame.transform.scale(
                PIECES[f"{color}_{piece}"], (TILE_SIZE, TILE_SIZE)
            )
    SOUNDS['move'] = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "move.wav"))
    SOUNDS['capture'] = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "capture.wav"))
    SOUNDS['check'] = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "check.wav"))

load_assets()

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
        """Desenha uma peça no tabuleiro."""
        color = "white" if piece.isupper() else "black"
        piece_name = {
            "k": "king", "q": "queen", "r": "rook", "b": "bishop", "n": "knight", "p": "pawn"
        }[piece.lower()]
        screen.blit(PIECES[f"{color}_{piece_name}"], (x * TILE_SIZE, y * TILE_SIZE))

# Classe para gerenciar o jogo
class Game:
    def _init_(self):
        self.board = Board()
        self.selected_piece = None
        self.valid_moves = []

    def handle_click(self, pos):
        """Gerencia cliques do jogador."""
        x, y = pos[0] // TILE_SIZE, pos[1] // TILE_SIZE
        if self.selected_piece:
            start = self.selected_piece
            self.selected_piece = None
            # Movimento básico sem validação completa
            self.board.grid[y][x] = self.board.grid[start[1]][start[0]]
            self.board.grid[start[1]][start[0]] = " "
            pygame.mixer.Sound.play(SOUNDS['move'])
        else:
            self.selected_piece = (x, y)

    def draw_highlights(self):
        """Destaca movimentos válidos e a peça selecionada."""
        if self.selected_piece:
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (
                self.selected_piece[0] * TILE_SIZE, self.selected_piece[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)

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
        game.draw_highlights()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if _name_ == "_main_":
    main()