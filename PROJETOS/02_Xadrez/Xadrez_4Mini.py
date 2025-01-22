import os
import sys

class Piece:
    def __init__(self, color, symbol):
        self.color = color  # 'white' or 'black'
        self.symbol = symbol

    def valid_moves(self, board, position):
        """To be implemented in subclasses"""
        return []

class Pawn(Piece):
    def __init__(self, color):
        symbol = '♙' if color == 'white' else '♟'
        super().__init__(color, symbol)

    # Implement specific movement logic for pawns
    def valid_moves(self, board, position):
        # Placeholder logic for pawns
        return []

class Board:
    def __init__(self):
        self.board = self.initialize_board()

    def initialize_board(self):
        board = [[' ' for _ in range(8)] for _ in range(8)]
        # Place pawns
        for col in range(8):
            board[1][col] = Pawn('black')
            board[6][col] = Pawn('white')
        return board

    def display(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print("  a b c d e f g h")
        for i, row in enumerate(self.board):
            print(f"{8 - i} " + ' '.join(
                piece.symbol if isinstance(piece, Piece) else '.'
                for piece in row
            ) + f" {8 - i}")
        print("  a b c d e f g h")

    def move_piece(self, start, end):
        # Placeholder for movement logic
        pass

class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = 'white'

    def play(self):
        while True:
            self.board.display()
            print(f"{self.current_turn.capitalize()}'s turn.")
            move = input("Enter your move (e.g., e2 e4): ").strip()
            if move.lower() == 'exit':
                print("Game exited.")
                sys.exit()
            # Parse and validate move (to be implemented)
            # Update the board and switch turns

if __name__ == "__main__":
    game = Game()
    game.play()
