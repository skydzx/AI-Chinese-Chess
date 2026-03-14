from dataclasses import dataclass
from typing import List, Tuple, Optional

# 棋子类型常量 (与board.py保持一致)
KING, ADVISOR, ELEPHANT, HORSE, CHARIOT, CANNON, PAWN = range(7)
RED, BLACK = 1, -1


# 走法索引映射: 10*9*10*9 = 8100
# 使用 from_row * 810 + from_col * 90 + to_row * 9 + to_col
def move_to_index(from_row, from_col, to_row, to_col) -> int:
    """走法转索引"""
    return from_row * 810 + from_col * 90 + to_row * 9 + to_col


def index_to_move(index: int) -> Tuple[int, int, int, int]:
    """索引转走法"""
    to_col = index % 9
    index //= 9
    to_row = index % 10
    index //= 10
    from_col = index % 9
    index //= 9
    from_row = index % 10
    return from_row, from_col, to_row, to_col


# 预计算所有合法走法的索引映射
LEGAL_MOVE_INDICES = {}
MOVE_INDEX_TO_ACTION = {}

_index_counter = 0


def register_legal_move(from_r, from_c, to_r, to_c):
    """注册合法走法"""
    global _index_counter
    idx = move_to_index(from_r, from_c, to_r, to_c)
    LEGAL_MOVE_INDICES[idx] = _index_counter
    MOVE_INDEX_TO_ACTION[_index_counter] = (from_r, from_c, to_r, to_c)
    _index_counter += 1
    return _index_counter - 1


# 注册所有合法走法位置
for r1 in range(10):
    for c1 in range(9):
        for r2 in range(10):
            for c2 in range(9):
                if r1 != r2 or c1 != c2:
                    register_legal_move(r1, c1, r2, c2)

NUM_ACTIONS = _index_counter  # 应该是 8091


@dataclass(frozen=True)
class Move:
    """走法表示"""
    from_row: int
    from_col: int
    to_row: int
    to_col: int

    def to_index(self) -> int:
        """转换为策略网络索引"""
        idx = move_to_index(self.from_row, self.from_col, self.to_row, self.to_col)
        return LEGAL_MOVE_INDICES.get(idx, -1)

    @classmethod
    def from_index(cls, index: int) -> 'Move':
        """从索引创建走法"""
        if index not in MOVE_INDEX_TO_ACTION:
            raise ValueError(f"Invalid move index: {index}")
        from_r, from_c, to_r, to_c = MOVE_INDEX_TO_ACTION[index]
        return cls(from_r, from_c, to_r, to_c)

    def __str__(self):
        return f"{self.from_col}{9-self.from_row}-{self.to_col}{9-self.to_row}"

    def __repr__(self):
        return f"Move({self.from_row},{self.from_col}->{self.to_row},{self.to_col})"


class MoveGenerator:
    """走法生成器"""

    @staticmethod
    def get_legal_moves(board) -> List[Move]:
        """获取所有合法走法"""
        moves = []
        color = board.current_player
        pieces = board.get_all_pieces(color)

        for row, col, piece in pieces:
            piece_type = piece[0]
            if piece_type == KING:
                moves.extend(MoveGenerator._generate_king_moves(board, row, col))
            elif piece_type == ADVISOR:
                moves.extend(MoveGenerator._generate_advisor_moves(board, row, col))
            elif piece_type == ELEPHANT:
                moves.extend(MoveGenerator._generate_elephant_moves(board, row, col))
            elif piece_type == HORSE:
                moves.extend(MoveGenerator._generate_horse_moves(board, row, col))
            elif piece_type == CHARIOT:
                moves.extend(MoveGenerator._generate_chariot_moves(board, row, col))
            elif piece_type == CANNON:
                moves.extend(MoveGenerator._generate_cannon_moves(board, row, col))
            elif piece_type == PAWN:
                moves.extend(MoveGenerator._generate_pawn_moves(board, row, col))

        # 过滤会导致自己被将军的走法
        legal_moves = []
        for move in moves:
            if MoveGenerator._is_safe_move(board, move, color):
                legal_moves.append(move)

        return legal_moves

    @staticmethod
    def _is_safe_move(board, move, color) -> bool:
        """检查走棋后是否被将军"""
        # 模拟走棋
        from_piece = board.get_piece(move.from_row, move.from_col)
        to_piece = board.get_piece(move.to_row, move.to_col)

        board.set_piece(move.to_row, move.to_col, from_piece)
        board.set_piece(move.from_row, move.from_col, None)

        is_check = board.is_check(color)

        # 恢复
        board.set_piece(move.from_row, move.from_col, from_piece)
        board.set_piece(move.to_row, move.to_col, to_piece)

        return not is_check

    @staticmethod
    def _generate_king_moves(board, row, col) -> List[Move]:
        """将帅走法"""
        moves = []
        piece = board.get_piece(row, col)
        color = piece[1]

        palace = [(r, c) for r in range(7, 10) for c in range(3, 6)] if color == RED \
            else [(r, c) for r in range(0, 3) for c in range(3, 6)]

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = row + dr, col + dc
            if (nr, nc) in palace:
                target = board.get_piece(nr, nc)
                if target is None or target[1] != color:
                    moves.append(Move(row, col, nr, nc))
        return moves

    @staticmethod
    def _generate_advisor_moves(board, row, col) -> List[Move]:
        """士走法"""
        moves = []
        piece = board.get_piece(row, col)
        color = piece[1]

        palace = [(r, c) for r in range(7, 10) for c in range(3, 6)] if color == RED \
            else [(r, c) for r in range(0, 3) for c in range(3, 6)]

        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr, nc = row + dr, col + dc
            if (nr, nc) in palace:
                target = board.get_piece(nr, nc)
                if target is None or target[1] != color:
                    moves.append(Move(row, col, nr, nc))
        return moves

    @staticmethod
    def _generate_elephant_moves(board, row, col) -> List[Move]:
        """象/相走法"""
        moves = []
        piece = board.get_piece(row, col)
        color = piece[1]

        for dr, dc in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 10 and 0 <= nc < 9:
                # 不过河
                if color == RED and nr < 5:
                    continue
                if color == BLACK and nr >= 5:
                    continue
                # 象眼
                mr, mc = row + dr // 2, col + dc // 2
                if board.get_piece(mr, mc) is None:
                    target = board.get_piece(nr, nc)
                    if target is None or target[1] != color:
                        moves.append(Move(row, col, nr, nc))
        return moves

    @staticmethod
    def _generate_horse_moves(board, row, col) -> List[Move]:
        """马走法"""
        moves = []
        piece = board.get_piece(row, col)
        color = piece[1]

        legs = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        jumps = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]

        for (lr, lc), (jr, jc) in zip(legs, jumps):
            if 0 <= jr < 10 and 0 <= jc < 9:
                if board.get_piece(lr, lc) is None:
                    target = board.get_piece(jr, jc)
                    if target is None or target[1] != color:
                        moves.append(Move(row, col, jr, jc))
        return moves

    @staticmethod
    def _generate_chariot_moves(board, row, col) -> List[Move]:
        """车走法"""
        moves = []
        piece = board.get_piece(row, col)
        color = piece[1]

        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = row + dr, col + dc
            while 0 <= nr < 10 and 0 <= nc < 9:
                target = board.get_piece(nr, nc)
                if target is None:
                    moves.append(Move(row, col, nr, nc))
                else:
                    if target[1] != color:
                        moves.append(Move(row, col, nr, nc))
                    break
                nr, nc = nr + dr, nc + dc
        return moves

    @staticmethod
    def _generate_cannon_moves(board, row, col) -> List[Move]:
        """炮走法"""
        moves = []
        piece = board.get_piece(row, col)
        color = piece[1]

        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = row + dr, col + dc
            screen = False
            while 0 <= nr < 10 and 0 <= nc < 9:
                target = board.get_piece(nr, nc)
                if not screen:
                    if target:
                        screen = True
                    else:
                        moves.append(Move(row, col, nr, nc))
                else:
                    if target:
                        if target[1] != color:
                            moves.append(Move(row, col, nr, nc))
                        break
                nr, nc = nr + dr, nc + dc
        return moves

    @staticmethod
    def _generate_pawn_moves(board, row, col) -> List[Move]:
        """兵/卒走法"""
        moves = []
        piece = board.get_piece(row, col)
        color = piece[1]

        if color == RED:
            # 未过河
            if row > 4:
                moves.append(Move(row, col, row - 1, col))
            else:
                # 过河
                moves.append(Move(row, col, row - 1, col))
                moves.append(Move(row, col, row, col - 1))
                moves.append(Move(row, col, row, col + 1))
        else:
            if row < 5:
                moves.append(Move(row, col, row + 1, col))
            else:
                moves.append(Move(row, col, row + 1, col))
                moves.append(Move(row, col, row, col - 1))
                moves.append(Move(row, col, row, col + 1))

        # 过滤越界
        moves = [m for m in moves if 0 <= m.to_row < 10 and 0 <= m.to_col < 9]
        # 过滤吃己方子
        moves = [m for m in moves
                 if board.get_piece(m.to_row, m.to_col) is None
                 or board.get_piece(m.to_row, m.to_col)[1] != color]
        return moves
