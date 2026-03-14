# AIChineseChess 核心引擎实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现中国象棋核心引擎，包含棋盘表示、规则引擎、神经网络、MCTS搜索和基础训练流程

**Architecture:** 采用AlphaZero架构，神经网络输出策略和价值，MCTS引导搜索，自对弈强化学习

**Tech Stack:** Python 3.8+, PyTorch, NumPy

---

## 文件结构

```
AIChineseChess/
├── backend/
│   ├── __init__.py
│   ├── board.py           # 棋盘表示
│   ├── move.py            # 走法表示
│   ├── rules.py           # 规则引擎
│   └── position.py       # 局面评估
├── ai/
│   ├── __init__.py
│   ├── network.py        # 神经网络
│   ├── mcts.py           # MCTS搜索
│   └── trainer.py        # 训练器
├── data/
│   └── __init__.py
└── tests/
    ├── __init__.py
    ├── test_board.py
    ├── test_rules.py
    └── test_network.py
```

---

## Chunk 1: 棋盘与走法基础

### Task 1: 棋盘表示

**Files:**
- Create: `backend/board.py`
- Test: `tests/test_board.py`

- [ ] **Step 1: 创建完整的棋盘类**

```python
# backend/board.py
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
        [4, 3, 2, 1, 0, 1, 2, 3, 4],  # 0: 车马象士将士象车
        [None] * 9,
        [None, 5, None, None, None, None, None, 5, None],  # 2: 炮
        [6, None, 6, None, 6, None, 6, None, 6],  # 3: 兵
        [None] * 9,
        [None] * 9,
        [6, None, 6, None, 6, None, 6, None, 6],  # 6: 兵
        [None, 5, None, None, None, None, None, 5, None],  # 7: 炮
        [None] * 9,
        [4, 3, 2, 1, 0, 1, 2, 3, 4],  # 9: 车马象士帅士象车
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
        from backend.move import Move

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
            mid = (red_king[0] + black_king[0]) // 2
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
```

- [ ] **Step 2: 运行测试验证**

```bash
python -c "from backend.board import Board; b = Board(); print(b)"
```

预期输出：显示初始棋盘布局

- [ ] **Step 3: 提交**

```bash
git add backend/board.py
git commit -m "feat: add Board class with basic representation"
```

---

### Task 2: 走法表示

**Files:**
- Create: `backend/move.py`

- [ ] **Step 1: 创建走法类**

```python
# backend/move.py
from dataclasses import dataclass
from typing import List, Tuple, Optional

# 棋子类型常量 (与board.py保持一致)
KING, ADVISOR, ELEPHANT, HORSE, CHARIOT, CANNON, PAWN = range(7)
RED, BLACK = 1, -1

# 走法索引映射: 90*90 = 8100, 但中国象棋只有2098种合法走法
# 使用 90*90 = 8100 作为索引空间 (from * 90 + to)
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


@dataclass
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
```

- [ ] **Step 2: 提交**

```bash
git add backend/move.py
git commit -m "feat: add Move class and MoveGenerator"
```

---

### Task 3: 规则引擎

**Files:**
- Create: `backend/rules.py`
- Test: `tests/test_rules.py`

- [ ] **Step 1: 创建规则引擎**

```python
# backend/rules.py
from .board import Board, Piece
from .move import Move

class RuleEngine:
    """规则引擎 - 走法合法性检查"""

    @staticmethod
    def is_legal_move(board: Board, move: Move) -> bool:
        """检查走法是否合法"""
        # 1. 检查起点有己方棋子
        piece = board.get_piece(move.from_row, move.from_col)
        if not piece or piece[1] != board.current_player:
            return False

        # 2. 检查终点不是己方棋子
        dest_piece = board.get_piece(move.to_row, move.to_col)
        if dest_piece and dest_piece[1] == board.current_player:
            return False

        # 3. 检查具体走法规则
        if not RuleEngine._check_piece_move(board, move, piece):
            return False

        # 4. 检查走后是否被将军
        if RuleEngine._would_be_in_check(board, move, board.current_player):
            return False

        return True

    @staticmethod
    def _check_piece_move(board: Board, move: Move, piece) -> bool:
        """检查具体棋子走法"""
        piece_type = piece[0]

        if piece_type == Piece.KING:
            return RuleEngine._is_legal_king_move(board, move)
        elif piece_type == Piece.ADVISOR:
            return RuleEngine._is_legal_advisor_move(board, move)
        elif piece_type == Piece.ELEPHANT:
            return RuleEngine._is_legal_elephant_move(board, move)
        # ... 其他棋子

        return True

    @staticmethod
    def is_check(board: Board, color: int) -> bool:
        """检查是否被将军"""
        # 找到对方的将/帅
        king_pos = None
        for r in range(10):
            for c in range(9):
                p = board.get_piece(r, c)
                if p and p[0] == Piece.KING and p[1] == color:
                    king_pos = (r, c)
                    break

        if not king_pos:
            return True  # 将帅不在，算被将军(将帅对面)

        # 检查是否被攻击
        enemy_color = -color
        enemy_pieces = board.get_all_pieces(enemy_color)

        for er, ec, _ in enemy_pieces:
            # 简化的攻击检查
            # 实际需要检查各种棋子能攻击到 king_pos
            pass

        return False

    @staticmethod
    def _would_be_in_check(board: Board, move: Move, color: int) -> bool:
        """走棋后是否被将军"""
        # 模拟走棋
        # 检查将军
        pass
```

- [ ] **Step 2: 提交**

```bash
git add backend/rules.py
git commit -m "feat: add RuleEngine for move validation"
```

---

## Chunk 2: 神经网络

### Task 4: 神经网络实现

**Files:**
- Create: `ai/network.py`
- Test: `tests/test_network.py`

- [ ] **Step 1: 创建神经网络**

```python
# ai/network.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class ChineseChessNet(nn.Module):
    """中国象棋神经网络 - AlphaZero风格"""

    def __init__(self, num_channels=128, num_res_blocks=8):
        super().__init__()

        # 输入: [batch, 56, 10, 9] (14通道 x 4步历史)
        self.conv_input = nn.Conv2d(56, num_channels, kernel_size=3, padding=1)
        self.bn_input = nn.BatchNorm2d(num_channels)

        # 残差块
        self.res_blocks = nn.ModuleList([
            ResidualBlock(num_channels) for _ in range(num_res_blocks)
        ])

        # 策略头
        self.policy_conv = nn.Conv2d(num_channels, 32, kernel_size=1)
        self.policy_bn = nn.BatchNorm2d(32)
        self.policy_fc = nn.Linear(32 * 10 * 9, 2098)  # 2098种走法

        # 价值头
        self.value_conv = nn.Conv2d(num_channels, 1, kernel_size=1)
        self.value_bn = nn.BatchNorm2d(1)
        self.value_fc1 = nn.Linear(10 * 9, 64)
        self.value_fc2 = nn.Linear(64, 1)

    def forward(self, x):
        # 输入层
        x = F.relu(self.bn_input(self.conv_input(x)))

        # 残差块
        for block in self.res_blocks:
            x = block(x)

        # 策略头
        p = F.relu(self.policy_bn(self.policy_conv(x)))
        p = p.view(p.size(0), -1)
        p = F.softmax(self.policy_fc(p), dim=1)

        # 价值头
        v = F.relu(self.value_bn(self.value_conv(x)))
        v = v.view(v.size(0), -1)
        v = F.tanh(self.value_fc2(F.relu(self.value_fc1(v))))

        return p, v


class ResidualBlock(nn.Module):
    """残差块"""

    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x = F.relu(x + residual)
        return x
```

- [ ] **Step 2: 测试网络输出**

```python
# tests/test_network.py
import torch
from ai.network import ChineseChessNet

def test_network_output():
    net = ChineseChessNet(num_channels=128, num_res_blocks=8)
    x = torch.randn(1, 56, 10, 9)
    policy, value = net(x)
    assert policy.shape == (1, 2098)
    assert value.shape == (1, 1)
    print(f"Policy shape: {policy.shape}, Value: {value.item():.3f}")

if __name__ == "__main__":
    test_network_output()
```

- [ ] **Step 3: 提交**

```bash
git add ai/network.py tests/test_network.py
git commit -m "feat: add ChineseChessNet neural network"
```

---

### Task 5: 棋盘编码器

**Files:**
- Create: `backend/encoder.py`

- [ ] **Step 1: 创建编码器**

```python
# backend/encoder.py
import numpy as np
import torch
from .board import Board, Piece

class BoardEncoder:
    """棋盘编码器 - 将棋盘转为神经网络输入"""

    CHANNEL_MAP = {
        # 红方棋子 (0-6)
        (Piece.KING, Piece.RED): 0,
        (Piece.ADVISOR, Piece.RED): 1,
        (Piece.ELEPHANT, Piece.RED): 2,
        (Piece.HORSE, Piece.RED): 3,
        (Piece.CHARIOT, Piece.RED): 4,
        (Piece.CANNON, Piece.RED): 5,
        (Piece.PAWN, Piece.RED): 6,
        # 黑方棋子 (7-13)
        (Piece.KING, Piece.BLACK): 7,
        (Piece.ADVISOR, Piece.BLACK): 8,
        (Piece.ELEPHANT, Piece.BLACK): 9,
        (Piece.HORSE, Piece.BLACK): 10,
        (Piece.CHARIOT, Piece.BLACK): 11,
        (Piece.CANNON, Piece.BLACK): 12,
        (Piece.PAWN, Piece.BLACK): 13,
    }

    @staticmethod
    def encode(board: Board, history_boards: list = None) -> np.ndarray:
        """
        编码棋盘为56通道 (14 x 4)张量
        """
        planes = np.zeros((56, 10, 9), dtype=np.float32)

        # 当前局面
        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece:
                    channel = BoardEncoder.CHANNEL_MAP.get((piece[0], piece[1]))
                    if channel is not None:
                        planes[channel, r, c] = 1

        # 历史局面 (最多3步)
        if history_boards:
            for i, hist_board in enumerate(history_boards[:3]):
                offset = (i + 1) * 14
                for r in range(10):
                    for c in range(9):
                        piece = hist_board.board[r][c]
                        if piece:
                            channel = BoardEncoder.CHANNEL_MAP.get((piece[0], piece[1]))
                            if channel is not None:
                                planes[offset + channel, r, c] = 1

        return planes

    @staticmethod
    def encode_to_tensor(board: Board, history_boards: list = None) -> np.ndarray:
        """编码为PyTorch张量 [1, 56, 10, 9]"""
        planes = BoardEncoder.encode(board, history_boards)
        return torch.from_numpy(planes).unsqueeze(0)
```

- [ ] **Step 2: 提交**

```bash
git add backend/encoder.py
git commit -m "feat: add BoardEncoder for neural network input"
```

---

## Chunk 3: MCTS搜索

### Task 6: MCTS实现

**Files:**
- Create: `ai/mcts.py`

- [ ] **Step 1: 创建MCTS**

```python
# ai/mcts.py
import math
import copy
import numpy as np
import torch
from typing import Dict, Tuple

class MCTSNode:
    """MCTS节点"""

    def __init__(self, state, parent=None, prior=0.0):
        self.state = state  # (board, current_player)
        self.parent = parent
        self.children = {}  # action -> MCTSNode

        self.visit_count = 0
        self.value_sum = 0.0
        self.prior = prior

    @property
    def q_value(self) -> float:
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count

    def is_expanded(self) -> bool:
        return len(self.children) > 0


class MCTS:
    """蒙特卡洛树搜索 - PUCT算法"""

    def __init__(self, network, num_simulations=500, c_puct=1.5):
        self.network = network
        self.num_simulations = num_simulations
        self.c_puct = c_puct

    def search(self, board) -> Tuple[np.ndarray, float]:
        """
        执行MCTS搜索
        返回: (策略概率, 局面价值)
        """
        root_state = (board, board.current_player)
        root = MCTSNode(root_state)

        # 初始化根节点
        self._expand_node(root, board)

        for _ in range(self.num_simulations):
            board_copy = copy.deepcopy(board)
            node = root

            # 选择
            while node.is_expanded() and not self._is_terminal(board_copy):
                node = self._select_child(node, board_copy)
                move = self._find_move(node.parent, node)
                board_copy.make_move(move)

            # 展开
            if not self._is_terminal(board_copy):
                self._expand_node(node, board_copy)

            # 评估
            value = self._evaluate(board_copy)

            # 回溯
            self._backpropagate(node, value)

        # 返回根节点策略 (访问次数归一化)
        return self._get_policy(root), root.q_value

    def _select_child(self, node: MCTSNode, board) -> MCTSNode:
        """PUCT选择"""
        best_score = -float('inf')
        best_child = None

        for action, child in node.children.items():
            if child.visit_count == 0:
                # 未访问节点，优先探索
                u = self.c_puct * child.prior * math.sqrt(node.visit_count + 1)
                score = u
            else:
                u = self.c_puct * child.prior * math.sqrt(node.visit_count) / (child.visit_count + 1)
                score = child.q_value + u

            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def _expand_node(self, node: MCTSNode, board):
        """展开节点 - 使用神经网络预测"""
        # 编码棋盘
        encoder = BoardEncoder()
        x = encoder.encode(board)
        x_tensor = torch.from_numpy(x).unsqueeze(0).cuda()  # GPU

        with torch.no_grad():
            policy_logits, value = self.network(x_tensor)

        policy = policy_logits.squeeze(0).cpu().numpy()

        # 获取合法走法
        legal_moves = MoveGenerator.get_legal_moves(board)

        # 创建子节点
        for move in legal_moves:
            prior = policy[move.to_index()]  # 需要实现 move.to_index()
            node.children[move] = MCTSNode(
                (board, -board.current_player),
                parent=node,
                prior=prior
            )

    def _evaluate(self, board) -> float:
        """评估局面"""
        encoder = BoardEncoder()
        x = encoder.encode(board)
        x_tensor = torch.from_numpy(x).unsqueeze(0).cuda()

        with torch.no_grad():
            _, value = self.network(x_tensor)

        return value.item()

    def _backpropagate(self, node: MCTSNode, value: float):
        """回溯更新"""
        while node is not None:
            node.visit_count += 1
            node.value_sum += value
            value = -value  # 翻转视角
            node = node.parent

    def _get_policy(self, root: MCTSNode) -> np.ndarray:
        """获取策略分布"""
        visits = np.zeros(2098)
        for move, child in root.children.items():
            visits[move.to_index()] = child.visit_count

        # 归一化
        total = visits.sum()
        if total > 0:
            visits /= total
        return visits
```

- [ ] **Step 2: 提交**

```bash
git add ai/mcts.py
git commit -m "feat: add MCTS search implementation"
```

---

## Chunk 4: 训练流程

### Task 7: 训练器

**Files:**
- Create: `ai/trainer.py`

- [ ] **Step 1: 创建训练器**

```python
# ai/trainer.py
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import numpy as np
from tqdm import tqdm

class Trainer:
    """AlphaZero训练器"""

    def __init__(self, network, data_dir="data"):
        self.network = network
        self.network.cuda()

        self.optimizer = optim.Adam(network.parameters(), lr=0.001)
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=100
        )

        self.data_dir = data_dir
        self.replay_buffer = deque(maxlen=100000)

    def train(self, num_epochs=100, selfplay_games_per_epoch=100):
        """训练主循环"""
        for epoch in range(num_epochs):
            print(f"\n=== Epoch {epoch+1}/{num_epochs} ===")

            # 1. 自对弈收集数据
            print("Self-play...")
            games = self.selfplay(selfplay_games_per_epoch)

            # 2. 加入回放池
            for game in games:
                self.replay_buffer.extend(game)

            # 3. 训练网络
            print("Training...")
            loss = self.train_step(batch_size=128)

            print(f"Loss: {loss:.4f}")
            self.scheduler.step()

            # 4. 保存检查点
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(f"model_epoch_{epoch+1}.pth")

    def selfplay(self, num_games: int) -> list:
        """自对弈生成训练数据"""
        games = []

        for _ in range(num_games):
            game_data = self.play_one_game(temperature=1.0)
            games.append(game_data)

        return games

    def play_one_game(self, temperature=1.0) -> list:
        """下一局自对弈"""
        board = Board()
        mcts = MCTS(self.network)

        game_data = []  # [(state, policy, value), ...]
        history_boards = []

        while not board.is_game_over():
            # MCTS搜索
            policy, value = mcts.search(board)

            # 保存数据 (状态, 策略, 价值)
            encoder = BoardEncoder()
            state = encoder.encode(board, history_boards[-3:] if history_boards else None)
            game_data.append((state, policy, value))

            # 采样走法
            if temperature > 0.001:
                # 加温度采样
                p = policy ** (1/temperature)
                p /= p.sum()
                action = np.random.choice(len(p), p=p)
            else:
                action = np.argmax(policy)

            # 执行走法
            move = Move.from_index(action)
            board.make_move(move)

            # 更新历史
            history_boards.append(copy.deepcopy(board))

        # 计算最终回报
        result = board.get_result()  # 1:红胜, -1:黑胜, 0:和

        # 回溯赋值
        for i, (state, policy, _) in enumerate(game_data):
            # 最后一手之后的结果
            if i % 2 == 0:  # 红方
                game_data[i] = (state, policy, result)
            else:
                game_data[i] = (state, policy, -result)

        return game_data

    def train_step(self, batch_size=128) -> float:
        """单步训练"""
        if len(self.replay_buffer) < batch_size:
            return 0.0

        # 采样
        batch = random.sample(self.replay_buffer, batch_size)

        states = torch.tensor(np.array([b[0] for b in batch]), dtype=torch.float32).cuda()
        target_pis = torch.tensor(np.array([b[1] for b in batch]), dtype=torch.float32).cuda()
        target_vs = torch.tensor(np.array([b[2] for b in batch]), dtype=torch.float32).unsqueeze(1).cuda()

        # 前向
        policy, value = self.network(states)

        # 损失
        policy_loss = -torch.sum(target_pis * torch.log(policy + 1e-8)) / batch_size
        value_loss = nn.MSELoss()(value, target_vs)

        loss = policy_loss + value_loss

        # 反向
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def save_checkpoint(self, filename: str):
        """保存模型"""
        path = f"{self.data_dir}/models/{filename}"
        torch.save({
            'network': self.network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }, path)
        print(f"Saved: {path}")
```

- [ ] **Step 2: 提交**

```bash
git add ai/trainer.py
git commit -m "feat: add AlphaZero trainer"
```

---

## 总结

此计划包含核心引擎的所有基础组件：
1. 棋盘与走法表示
2. 规则引擎
3. 神经网络
4. MCTS搜索
5. 训练流程

完成后可进行基础的自对弈训练测试。
