# game/game_controller.py
from enum import Enum
from backend.board import Board, Piece
from backend.move import Move, MoveGenerator


class GameMode(Enum):
    PVP = 0
    PVE = 1
    AI_WATCH = 2


class GameController:
    def __init__(self):
        self.board = None
        self.mode = None
        self.player_color = Piece.RED
        self.move_history = []
        self.redo_stack = []

    def start_game(self, mode: GameMode, player_color=Piece.RED):
        self.mode = mode
        self.player_color = player_color
        self.board = Board()
        self.move_history = []
        self.redo_stack = []

    def make_move(self, from_row, from_col, to_row, to_col) -> bool:
        move = Move(from_row, from_col, to_row, to_col)
        legal_moves = MoveGenerator.get_legal_moves(self.board)
        if move not in legal_moves:
            return False
        self.board.make_move(move)
        self.move_history.append(move)
        self.redo_stack.clear()
        return True

    def undo_move(self) -> bool:
        if not self.move_history:
            return False
        move = self.move_history.pop()
        self.board.undo_move()
        self.redo_stack.append(move)
        return True

    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    def get_result(self) -> int:
        return self.board.get_result()

    def get_current_player(self):
        return self.board.current_player
