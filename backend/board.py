import copy
from typing import List, Tuple, Optional


class Piece:
    """棋子定义"""
    RED = 1
    BLACK = -1

    # 棋子类型
    KING = 0    # 帅/将
    ADVISOR = 1 # 仕/士
    ELEPHANT = 2 # 相/象
    HORSE = 3   # 马
    CHARIOT = 4 # 车
    CANNON = 5  # 炮
    PAWN = 6    # 兵/卒

    @staticmethod
    def to_char(piece_type: int, color: int) -> str:
        """棋子字符表示"""
        chars = {
            (0, 1): '帅', (0, -1): '将',
            (1, 1): '仕', (1, -1): '士',
            (2, 1): '相', (2, -1): '象',
            (3, 1): '马', (3, -1): '马',
            (4, 1): '车', (4, -1): '车',
            (5, 1): '炮', (5, -1): '炮',
            (6, 1): '兵', (6, -1): '卒',
        }
        return chars.get((piece_type, color), ' ')


class Board:
    """棋盘表示 - 10行9列 (红方在0-4行, 黑方在5-9行)"""

    INITIAL_BOARD = [
        [4, 3, 2, 1, 0, 1, 2, 3, 4],  # 9: 黑方车马象士将士象车
        [None] * 9,
        [None, 5, None, None, None, None, None, 5, None],  # 7: 黑炮
        [6, None, 6, None, 6, None, 6, None, 6],  # 6: 黑卒
        [None] * 9,
        [None] * 9,
        [6, None, 6, None, 6, None, 6, None, 6],  # 3: 红兵
        [None, 5, None, None, None, None, None, 5, None],  # 2: 红炮
        [None] * 9,
        [4, 3, 2, 1, 0, 1, 2, 3, 4],  # 0: 红车马象士帅士象车
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        """重置到初始局面"""
        self.board = [[None for _ in range(9)] for _ in range(10)]
        self.current_player = Piece.RED

        for r in range(10):
            for c in range(9):
                piece_type = self.INITIAL_BOARD[r][c]
                if piece_type is not None:
                    color = Piece.RED if r < 5 else Piece.BLACK
                    self.board[r][c] = (piece_type, color)

        self.move_history = []

    def get_piece(self, row: int, col: int) -> Optional[Tuple[int, int]]:
        """获取指定位置棋子 (row, col)"""
        if 0 <= row < 10 and 0 <= col < 9:
            return self.board[row][col]
        return None

    def set_piece(self, row: int, col: int, piece: Optional[Tuple[int, int]]):
        """设置棋子"""
        if 0 <= row < 10 and 0 <= col < 9:
            self.board[row][col] = piece

    def get_all_pieces(self, color: int) -> List[Tuple[int, int, Tuple[int, int]]]:
        """获取所有指定颜色的棋子"""
        pieces = []
        for r in range(10):
            for c in range(9):
                piece = self.board[r][c]
                if piece and piece[1] == color:
                    pieces.append((r, c, piece))
        return pieces

    def make_move(self, move) -> bool:
        """执行走法,返回是否成功"""
        # 获取起点棋子
        piece = self.get_piece(move.from_row, move.from_col)
        if not piece:
            return False

        # 设置终点
        self.set_piece(move.to_row, move.to_col, piece)
        self.set_piece(move.from_row, move.from_col, None)

        # 记录历史
        self.move_history.append(move)

        # 切换玩家
        self.current_player = -self.current_player
        return True

    def undo_move(self):
        """撤销最后一步"""
        if not self.move_history:
            return False

        move = self.move_history.pop()
        self.current_player = -self.current_player

        # 恢复起点
        piece = self.get_piece(move.to_row, move.to_col)
        self.set_piece(move.from_row, move.from_col, piece)
        self.set_piece(move.to_row, move.to_col, None)
        return True

    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        red_king = self._find_king(Piece.RED)
        black_king = self._find_king(Piece.BLACK)

        if not red_king or not black_king:
            return True

        # 将帅对面
        if red_king[1] == black_king[1]:  # 同列
            # 检查中间是否有遮挡
            for r in range(min(red_king[0], black_king[0]) + 1,
                          max(red_king[0], black_king[0])):
                if self.board[r][red_king[1]]:
                    break
            else:
                return True

        # 无合法走法
        from backend.move import MoveGenerator
        moves = MoveGenerator.get_legal_moves(self)
        return len(moves) == 0

    def get_result(self) -> int:
        """返回结果: 1=红胜, -1=黑胜, 0=和"""
        if self.is_game_over():
            # 简单判断: 当前被将军方输
            if self.is_check(self.current_player):
                return -self.current_player  # 当前玩家输了
        return 0

    def _find_king(self, color: int) -> Optional[Tuple[int, int]]:
        """找到指定颜色的将/帅"""
        for r in range(10):
            for c in range(9):
                p = self.board[r][c]
                if p and p[0] == Piece.KING and p[1] == color:
                    return (r, c)
        return None

    def is_check(self, color: int) -> bool:
        """检查是否被将军"""
        king_pos = self._find_king(color)
        if not king_pos:
            return True

        enemy_color = -color
        enemy_pieces = self.get_all_pieces(enemy_color)

        for er, ec, piece in enemy_pieces:
            moves = self._get_attacking_moves(er, ec, piece)
            for mr, mc in moves:
                if (mr, mc) == king_pos:
                    return True
        return False

    def _get_attacking_moves(self, row: int, col: int, piece) -> List[Tuple[int, int]]:
        """获取棋子能攻击到的位置"""
        piece_type = piece[0]
        color = piece[1]

        if piece_type == Piece.KING:
            return self._king_attacks(row, col, color)
        elif piece_type == Piece.ADVISOR:
            return self._advisor_attacks(row, col, color)
        elif piece_type == Piece.ELEPHANT:
            return self._elephant_attacks(row, col, color)
        elif piece_type == Piece.HORSE:
            return self._horse_attacks(row, col, color)
        elif piece_type == Piece.CHARIOT:
            return self._chariot_attacks(row, col, color)
        elif piece_type == Piece.CANNON:
            return self._cannon_attacks(row, col, color)
        elif piece_type == Piece.PAWN:
            return self._pawn_attacks(row, col, color)
        return []

    def _king_attacks(self, row: int, col: int, color: int) -> List[Tuple[int, int]]:
        """将帅的攻击位置"""
        attacks = []
        if color == Piece.RED:
            palace = [(r, c) for r in range(7, 10) for c in range(3, 6)]
        else:
            palace = [(r, c) for r in range(0, 3) for c in range(3, 6)]

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = row + dr, col + dc
            if (nr, nc) in palace:
                attacks.append((nr, nc))
        return attacks

    def _advisor_attacks(self, row: int, col: int, color: int) -> List[Tuple[int, int]]:
        """士的攻击位置"""
        attacks = []
        if color == Piece.RED:
            palace = [(r, c) for r in range(7, 10) for c in range(3, 6)]
        else:
            palace = [(r, c) for r in range(0, 3) for c in range(3, 6)]

        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr, nc = row + dr, col + dc
            if (nr, nc) in palace:
                attacks.append((nr, nc))
        return attacks

    def _elephant_attacks(self, row: int, col: int, color: int) -> List[Tuple[int, int]]:
        """象的攻击位置"""
        attacks = []
        for dr, dc in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 10 and 0 <= nc < 9:
                # 限制不过河
                if color == Piece.RED and nr < 5:
                    continue
                if color == Piece.BLACK and nr >= 5:
                    continue
                # 检查象眼
                mr, mc = row + dr // 2, col + dc // 2
                if not self.get_piece(mr, mc):
                    attacks.append((nr, nc))
        return attacks

    def _horse_attacks(self, row: int, col: int, color: int) -> List[Tuple[int, int]]:
        """马的攻击位置"""
        attacks = []
        legs = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        jumps = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]
        for (lr, lc), (jr, jc) in zip(legs, jumps):
            if 0 <= jr < 10 and 0 <= jc < 9:
                if self.get_piece(lr, lc) is None:
                    attacks.append((jr, jc))
        return attacks

    def _chariot_attacks(self, row: int, col: int, color: int) -> List[Tuple[int, int]]:
        """车的攻击位置"""
        attacks = []
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = row + dr, col + dc
            while 0 <= nr < 10 and 0 <= nc < 9:
                piece = self.get_piece(nr, nc)
                if piece:
                    if piece[1] != color:
                        attacks.append((nr, nc))
                    break
                attacks.append((nr, nc))
                nr, nc = nr + dr, nc + dc
        return attacks

    def _cannon_attacks(self, row: int, col: int, color: int) -> List[Tuple[int, int]]:
        """炮的攻击位置"""
        attacks = []
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = row + dr, col + dc
            screen = False
            while 0 <= nr < 10 and 0 <= nc < 9:
                piece = self.get_piece(nr, nc)
                if not screen:
                    if piece:
                        screen = True
                else:
                    if piece:
                        if piece[1] != color:
                            attacks.append((nr, nc))
                        break
                nr, nc = nr + dr, nc + dc
        return attacks

    def _pawn_attacks(self, row: int, col: int, color: int) -> List[Tuple[int, int]]:
        """兵/卒的攻击位置"""
        attacks = []
        if color == Piece.RED:
            forward = -1
            if row <= 4:
                attacks.append((row - 1, col))
            attacks.append((row + forward, col))
            if row < 5:
                attacks.extend([(row, col - 1), (row, col + 1)])
        else:
            forward = 1
            if row >= 6:
                attacks.append((row + 1, col))
            attacks.append((row + forward, col))
            if row > 4:
                attacks.extend([(row, col - 1), (row, col + 1)])

        return [(r, c) for r, c in attacks if 0 <= r < 10 and 0 <= c < 9]

    def __repr__(self):
        lines = []
        for r in range(9, -1, -1):
            line = f"{r}|"
            for c in range(9):
                piece = self.board[r][c]
                if piece:
                    line += Piece.to_char(piece[0], piece[1])
                else:
                    line += '·'
                line += ' '
            lines.append(line)
        lines.append("  0 1 2 3 4 5 6 7 8")
        return "\n".join(lines)
