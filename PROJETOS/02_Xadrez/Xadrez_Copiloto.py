import pygame
import numpy as np
import chess
import chess.svg

# Configurações do tabuleiro
board_size = 8
square_size = 60
board = chess.Board()

# Inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode((board_size * square_size, board_size * square_size))
pygame.display.set_caption('Jogo de Xadrez')

# Cores
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
dark_red = (139, 0, 0)

# Função para desenhar o tabuleiro
def draw_board():
    for row in range(board_size):
        for col in range(board_size):
            color = white if (row + col) % 2 == 0 else black
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))

# Função para desenhar peças
def draw_pieces():
    pieces = {
        'P': 'pawn_white.png',
        'p': 'pawn_black.png',
        'N': 'knight_white.png',
        'n': 'knight_black.png',
        'B': 'bishop_white.png',
        'b': 'bishop_black.png',
        'R': 'rook_white.png',
        'r': 'rook_black.png',
        'Q': 'queen_white.png',
        'q': 'queen_black.png',
        'K': 'king_white.png',
        'k': 'king_black.png',
    }
    for i in range(64):
        piece = str(board.piece_at(i))
        if piece != 'None':
            row, col = divmod(i, 8)
            screen.blit(pygame.image.load(pieces[piece]), (col * square_size, row * square_size))

# Função principal do jogo
def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_board()
        draw_pieces()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
