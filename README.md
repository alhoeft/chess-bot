# chess-bot
Independent Project

Project structure
- `pieces.py` contains the chess piece classes and movement rules.
- `chess.py` contains the board/game logic and command-line game.
- `bots.py` contains interchangeable bot move-selection strategies.
- `gui.py` contains the simple Tkinter graphical interface.

Run the graphical game from the project folder:

```powershell
python gui.py
```

Or run the command-line game:

```powershell
python chess.py
```

The project requires Python, NumPy (`python -m pip install numpy`), and Tkinter.

Current To-Do
- make chess functional game
    - Implement en passant, check, promotion, check
- random player
- simulations
- dependency injection on board creation

Future
- add opening reference data and use adapter pattern to implement to game
- same for endgame
- do what we're doing for mancala for middle game
