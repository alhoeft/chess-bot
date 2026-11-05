class Piece:
    STRAIGHT = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    DIAGONAL = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    KNIGHT_OFFSETS = [
        (1, 2), (2, 1), (-1, 2), (-2, 1),
        (1, -2), (2, -1), (-1, -2), (-2, -1),
    ]

    def __init__(self, color, x_pos, y_pos):
        self.color = color
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.has_moved = False

    def move(self, new_x, new_y):
        self.x_pos = new_x
        self.y_pos = new_y
        self.has_moved = True

    def get_moves(self, board, en_passant_target=None):
        raise NotImplementedError

    def display_name(self, end="\n"):
        print(f"{self.color} {type(self).__name__}", end=end)

    def _slide(self, board, directions):
        moves = []
        for x_change, y_change in directions:
            x, y = self.x_pos + x_change, self.y_pos + y_change
            while 0 <= x < 8 and 0 <= y < 8:
                target = board[y, x]
                if target is None:
                    moves.append((x, y))
                elif target.color != self.color:
                    moves.append((x, y))
                    break
                else:
                    break
                x += x_change
                y += y_change
        return moves

    def _jump(self, board, offsets):
        moves = []
        for x_change, y_change in offsets:
            x, y = self.x_pos + x_change, self.y_pos + y_change
            if 0 <= x < 8 and 0 <= y < 8:
                target = board[y, x]
                if target is None or target.color != self.color:
                    moves.append((x, y))
        return moves


class Rook(Piece):
    def get_moves(self, board, en_passant_target=None):
        return self._slide(board, self.STRAIGHT)


class Bishop(Piece):
    def get_moves(self, board, en_passant_target=None):
        return self._slide(board, self.DIAGONAL)


class Queen(Piece):
    def get_moves(self, board, en_passant_target=None):
        return self._slide(board, self.STRAIGHT + self.DIAGONAL)


class Knight(Piece):
    def get_moves(self, board, en_passant_target=None):
        return self._jump(board, self.KNIGHT_OFFSETS)


class King(Piece):
    def get_moves(self, board, en_passant_target=None):
        return self._jump(board, self.STRAIGHT + self.DIAGONAL)


class Pawn(Piece):
    def get_moves(self, board, en_passant_target=None):
        moves = []
        x, y = self.x_pos, self.y_pos
        direction = 1 if self.color == "white" else -1
        start_row = 1 if self.color == "white" else 6

        move_one_square = y + direction
        if 0 <= move_one_square < 8 and board[move_one_square, x] is None:
            moves.append((x, move_one_square))
            move_two_squares = y + 2 * direction
            if y == start_row and board[move_two_squares, x] is None:
                moves.append((x, move_two_squares))

        for x_change in (-1, 1):
            capture_x = x + x_change
            if 0 <= capture_x < 8 and 0 <= move_one_square < 8:
                target = board[move_one_square, capture_x]
                if target is not None and target.color != self.color:
                    moves.append((capture_x, move_one_square))

        if en_passant_target is not None:
            target_x, target_y = en_passant_target
            if target_y == move_one_square and abs(target_x - x) == 1:
                moves.append(en_passant_target)

        return moves
