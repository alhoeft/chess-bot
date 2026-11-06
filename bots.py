import random


Move = tuple[int, int, int, int]


class RandomBot:
    def choose_move(self, legal_moves: list[Move]) -> Move:
        if not legal_moves:
            raise ValueError("Cannot choose a move from an empty list")
        return random.choice(legal_moves)
