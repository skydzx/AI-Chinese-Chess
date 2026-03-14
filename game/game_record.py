# game/game_record.py
import json
from backend.board import Piece


class GameRecord:
    """棋谱记录"""

    def __init__(self):
        self.moves = []  # [(from_row, from_col, to_row, to_col), ...]
        self.red_player = "Player"
        self.black_player = "AI" if False else "Player"

    def add_move(self, fr, fc, tr, tc):
        self.moves.append((fr, fc, tr, tc))

    def save(self, filename):
        data = {
            "red": self.red_player,
            "black": self.black_player,
            "moves": self.moves
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.red_player = data.get("red", "Player")
        self.black_player = data.get("black", "Player")
        self.moves = data.get("moves", [])
