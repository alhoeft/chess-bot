import copy

import numpy as np

from pieces import Bishop, King, Knight, Pawn, Queen, Rook


class Chess:
    BOARD_SIZE = 8
    FILES = "abcdefgh"

    def __init__(self):
        self.board = np.full((self.BOARD_SIZE, self.BOARD_SIZE), None, dtype=object)
        self.en_passant_target = None
        self.turn = "white"

        back_row = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for x in range(self.BOARD_SIZE):
            self.board[0, x] = back_row[x]("white", x, 0)
            self.board[1, x] = Pawn("white", x, 1)
            self.board[6, x] = Pawn("black", x, 6)
            self.board[7, x] = back_row[x]("black", x, 7)

    def is_square_attacked(self, x, y, by_color):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row, col]
                if piece is None or piece.color != by_color:
                    continue
                if isinstance(piece, Pawn):
                    direction = 1 if piece.color == "white" else -1
                    if y == piece.y_pos + direction and abs(x - piece.x_pos) == 1:
                        return True
                else:
                    if (x, y) in piece.get_moves(self.board):
                        return True
        return False

    def castling_moves(self, color):
        moves = []
        row = 0 if color == "white" else 7
        enemy = "black" if color == "white" else "white"
        king = self.board[row, 4]

        if not isinstance(king, King) or king.has_moved:
            return moves

        if self.is_square_attacked(4, row, enemy):
            return moves

        sides = [
            (7, [5, 6], [5, 6], 6),
            (0, [1, 2, 3], [3, 2], 2),
        ]

        for rook_x, must_be_empty, king_path, king_landing in sides:
            rook = self.board[row, rook_x]
            if not isinstance(rook, Rook) or rook.has_moved or rook.color != color:
                continue
            if any(self.board[row, x] is not None for x in must_be_empty):
                continue
            if any(self.is_square_attacked(x, row, enemy) for x in king_path):
                continue
            moves.append((king_landing, row))

        return moves

    def find_king(self, color):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row, col]
                if isinstance(piece, King) and piece.color == color:
                    return col, row
        return None

    def parse_square(self, text):
        if len(text) != 2:
            return None
        file, rank = text[0].lower(), text[1]
        if file not in self.FILES or rank not in "12345678":
            return None
        return self.FILES.index(file), int(rank) - 1

    def display_board(self):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row, col]
                if piece is None:
                    print("empty", end=" ")
                else:
                    piece.display_name(end=" ")
            print()

    def move(self, old_x, old_y, new_x, new_y, promote_to=None):
        piece = self.board[old_y, old_x]
        target = self.board[new_y, new_x]
        captured = target

        if isinstance(piece, Pawn) and new_x != old_x and target is None:
            captured = self.board[old_y, new_x]
            self.board[old_y, new_x] = None

        if isinstance(piece, King) and abs(new_x - old_x) == 2:
            if new_x == 6:
                rook_from, rook_to = 7, 5
            else:
                rook_from, rook_to = 0, 3
            rook = self.board[old_y, rook_from]
            self.board[old_y, rook_to] = rook
            self.board[old_y, rook_from] = None
            rook.move(rook_to, old_y)

        self.board[new_y, new_x] = piece
        self.board[old_y, old_x] = None
        piece.move(new_x, new_y)

        last_row = 7 if piece.color == "white" else 0
        if isinstance(piece, Pawn) and new_y == last_row:
            if promote_to is None:
                promote_to = Queen
            new_piece = promote_to(piece.color, new_x, new_y)
            new_piece.has_moved = True
            self.board[new_y, new_x] = new_piece

        if isinstance(piece, Pawn) and abs(new_y - old_y) == 2:
            self.en_passant_target = (new_x, (old_y + new_y) // 2)
        else:
            self.en_passant_target = None

        return captured

    def play(self):
        promotion_choices = {"q": Queen, "r": Rook, "b": Bishop, "n": Knight}

        while True:
            self.display_board()
            print(f"{self.turn} to move")
            text = input("Enter move (e.g. e2 e4), or 'quit': ").strip()

            if text.lower() == "quit":
                break

            parts = text.split()
            if len(parts) != 2:
                print("Please enter two squares, like: e2 e4")
                continue

            start = self.parse_square(parts[0])
            end = self.parse_square(parts[1])
            if start is None or end is None:
                print("Squares must be a-h followed by 1-8, like: e2")
                continue

            old_x, old_y = start
            new_x, new_y = end

            if not self.valid_move(old_x, old_y, new_x, new_y):
                print("Illegal move, try again.")
                continue

            piece = self.board[old_y, old_x]
            last_row = 7 if piece.color == "white" else 0
            promote_to = None
            if isinstance(piece, Pawn) and new_y == last_row:
                choice = input("Promote to (q, r, b, n): ").strip().lower()
                promote_to = promotion_choices.get(choice, Queen)

            self.move(old_x, old_y, new_x, new_y, promote_to)
            self.turn = "black" if self.turn == "white" else "white"

            result = self.winning_eval()
            if result is not None:
                self.display_board()
                print(result)
                break

            enemy = "black" if self.turn == "white" else "white"
            king_x, king_y = self.find_king(self.turn)
            if king_x is not None and self.is_square_attacked(king_x, king_y, enemy):
                print("Check!")

    def legal_moves(self, x, y):
        piece = self.board[y, x]
        if piece is None:
            return []

        enemy = "black" if piece.color == "white" else "white"
        candidates = piece.get_moves(self.board, self.en_passant_target)
        if isinstance(piece, King):
            candidates += self.castling_moves(piece.color)

        legal = []
        for new_x, new_y in candidates:
            test_game = copy.deepcopy(self)
            test_game.move(x, y, new_x, new_y)
            king_x, king_y = test_game.find_king(piece.color)
            if king_x is not None and not test_game.is_square_attacked(king_x, king_y, enemy):
                legal.append((new_x, new_y))

        return legal

    def valid_move(self, old_x, old_y, new_x, new_y):
        piece = self.board[old_y, old_x]
        if piece is None or piece.color != self.turn:
            return False
        return (new_x, new_y) in self.legal_moves(old_x, old_y)

    def winning_eval(self):
        color = self.turn
        enemy = "black" if color == "white" else "white"

        if self.has_legal_moves(color):
            return None

        king_x, king_y = self.find_king(color)
        if king_x is not None and self.is_square_attacked(king_x, king_y, enemy):
            return f"{enemy} wins by checkmate"
        return "draw by stalemate"

    def has_legal_moves(self, color):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board[row, col]
                if piece is not None and piece.color == color:
                    if self.legal_moves(col, row):
                        return True
        return False


if __name__ == "__main__":
    game = Chess()
    game.play()
