import tkinter as tk
from tkinter import simpledialog

from bots import RandomBot
from chess import Chess
from pieces import Bishop, King, Knight, Pawn, Queen, Rook


class ChessGUI:
    LIGHT_SQUARE = "#EBEBEB"
    DARK_SQUARE = "#030027"
    SELECTED_SQUARE = "#efef85"
    LEGAL_SQUARE = "#87cfbe"
    PIECE_SYMBOLS = {
        ("white", Pawn): "\u2659",
        ("white", Knight): "\u2658",
        ("white", Bishop): "\u2657",
        ("white", Rook): "\u2656",
        ("white", Queen): "\u2655",
        ("white", King): "\u2654",
        ("black", Pawn): "\u265f",
        ("black", Knight): "\u265e",
        ("black", Bishop): "\u265d",
        ("black", Rook): "\u265c",
        ("black", Queen): "\u265b",
        ("black", King): "\u265a",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Chess")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.square_size = max(
            28,
            min(56, screen_width // 32, screen_height // 18),
        )
        self.root.resizable(False, False)
        self.game = Chess()
        self.player_color = None
        self.bot_color = None
        self.bot = None
        self.selected_square = None
        self.legal_destinations = []
        self.game_over = False
        self.buttons = {}

        self.show_start_screen()
        self.center_window()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def show_start_screen(self):
        self.clear_window()
        tk.Label(self.root, text="Choose your color", font=("Arial", 18)).grid(
            row=0, column=0, columnspan=2, padx=24, pady=(24, 16)
        )
        tk.Button(
            self.root,
            text="Play as White",
            command=lambda: self.start_game("white"),
        ).grid(row=1, column=0, padx=(24, 8), pady=(0, 24))
        tk.Button(
            self.root,
            text="Play as Black",
            command=lambda: self.start_game("black"),
        ).grid(row=1, column=1, padx=(8, 24), pady=(0, 24))
        self.center_window()

    def start_game(self, color):
        self.player_color = color
        self.bot_color = "black" if color == "white" else "white"
        self.bot = RandomBot()
        self.game = Chess()
        self.selected_square = None
        self.legal_destinations = []
        self.game_over = False
        self.buttons = {}
        self.build_game_screen()

    def build_game_screen(self):
        self.clear_window()
        self.status = tk.StringVar()
        tk.Label(self.root, textvariable=self.status, font=("Arial", 14)).grid(
            row=0, column=0, columnspan=9, pady=(10, 8)
        )

        for display_x in range(8):
            x = display_x if self.player_color == "white" else 7 - display_x
            tk.Label(self.root, text=Chess.FILES[x], width=4).grid(
                row=1, column=display_x + 1
            )
        for display_row in range(8):
            y = 7 - display_row if self.player_color == "white" else display_row
            tk.Label(self.root, text=str(y + 1), width=2).grid(
                row=display_row + 2, column=0
            )
            for display_x in range(8):
                x = display_x if self.player_color == "white" else 7 - display_x
                square = tk.Frame(
                    self.root,
                    width=self.square_size,
                    height=self.square_size,
                )
                square.grid_propagate(False)
                square.grid(row=display_row + 2, column=display_x + 1)
                button = tk.Button(
                    square,
                    font=("DejaVu Sans Mono", max(16, self.square_size // 2), "bold"),
                    command=lambda x=x, y=y: self.on_square_click(x, y),
                    relief=tk.FLAT,
                    borderwidth=0,
                    padx=0,
                    pady=0,
                )
                button.place(relwidth=1, relheight=1)
                self.buttons[(x, y)] = button

        tk.Button(self.root, text="New Game", command=self.new_game).grid(
            row=10, column=0, columnspan=9, pady=(8, 10)
        )
        self.update_status()
        self.refresh_board()
        self.center_window()
        if self.game.turn == self.bot_color:
            self.root.after(100, self.play_bot_move)

    def refresh_board(self):
        for (x, y), button in self.buttons.items():
            piece = self.game.board[y, x]
            if piece is None:
                button.configure(text="", fg="black")
            else:
                button.configure(
                    text=self.PIECE_SYMBOLS[(piece.color, type(piece))],
                    fg="#707070",
                )

            background = self.LIGHT_SQUARE if (x + y) % 2 else self.DARK_SQUARE
            if (x, y) in self.legal_destinations:
                background = self.LEGAL_SQUARE
            if (x, y) == self.selected_square:
                background = self.SELECTED_SQUARE
            button.configure(
                bg=background,
                activebackground=background,
                disabledforeground=button.cget("fg"),
            )
            if self.game_over:
                button.configure(state=tk.DISABLED)
            else:
                button.configure(state=tk.NORMAL)

    def update_status(self, message=None):
        if message:
            self.status.set(message)
            return

        king_position = self.game.find_king(self.game.turn)
        enemy = "black" if self.game.turn == "white" else "white"
        turn_label = (
            f"Bot ({self.game.turn.title()})"
            if self.game.turn == self.bot_color
            else self.game.turn.title()
        )
        if king_position and self.game.is_square_attacked(*king_position, enemy):
            self.status.set(f"{turn_label} to move — Check!")
        else:
            self.status.set(f"{turn_label} to move")

    def on_square_click(self, x, y):
        if self.game_over or self.game.turn != self.player_color:
            return

        if self.selected_square and (x, y) in self.legal_destinations:
            self.make_move(*self.selected_square, x, y)
            return

        piece = self.game.board[y, x]
        if piece is not None and piece.color == self.game.turn:
            self.selected_square = (x, y)
            self.legal_destinations = self.game.legal_moves(x, y)
        else:
            self.selected_square = None
            self.legal_destinations = []

        self.refresh_board()

    def make_move(self, old_x, old_y, new_x, new_y):
        piece = self.game.board[old_y, old_x]
        promote_to = None
        last_row = 7 if piece.color == "white" else 0
        if isinstance(piece, Pawn) and new_y == last_row:
            choice = simpledialog.askstring(
                "Pawn promotion",
                "Promote to queen, rook, bishop, or knight (Q/R/B/N):",
                parent=self.root,
            )
            promotion_choices = {
                "q": Queen,
                "r": Rook,
                "b": Bishop,
                "n": Knight,
            }
            promote_to = promotion_choices.get((choice or "q").strip().lower(), Queen)

        self.finish_move(old_x, old_y, new_x, new_y, promote_to)

    def finish_move(self, old_x, old_y, new_x, new_y, promote_to=None):
        self.game.move(old_x, old_y, new_x, new_y, promote_to)
        self.game.turn = "black" if self.game.turn == "white" else "white"
        self.selected_square = None
        self.legal_destinations = []

        result = self.game.winning_eval()
        if result is not None:
            self.game_over = True
            self.update_status(result)
        else:
            self.update_status()
        self.refresh_board()
        if not self.game_over and self.game.turn == self.bot_color:
            self.root.after(100, self.play_bot_move)

    def play_bot_move(self):
        if self.game_over or self.game.turn != self.bot_color:
            return

        legal_moves = []
        for y in range(self.game.BOARD_SIZE):
            for x in range(self.game.BOARD_SIZE):
                piece = self.game.board[y, x]
                if piece is not None and piece.color == self.bot_color:
                    for new_x, new_y in self.game.legal_moves(x, y):
                        legal_moves.append((x, y, new_x, new_y))

        if not legal_moves:
            self.game_over = True
            result = self.game.winning_eval()
            self.update_status(result or "Game over")
            self.refresh_board()
            return

        if self.bot is None:
            raise RuntimeError("The bot has not been initialized")
        old_x, old_y, new_x, new_y = self.bot.choose_move(legal_moves)
        self.finish_move(old_x, old_y, new_x, new_y)

    def new_game(self):
        self.show_start_screen()


def main():
    root = tk.Tk()
    ChessGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
