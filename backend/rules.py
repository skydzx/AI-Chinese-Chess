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
        from_r, from_c = move.from_row, move.from_col
        to_r, to_c = move.to_row, move.to_col
        dr, dc = to_r - from_r, to_c - from_c

        if piece_type == Piece.KING:
            return RuleEngine._is_legal_king_move(from_r, from_c, to_r, to_c, piece[1])
        elif piece_type == Piece.ADVISOR:
            return RuleEngine._is_legal_advisor_move(from_r, from_c, to_r, to_c, piece[1])
        elif piece_type == Piece.ELEPHANT:
            return RuleEngine._is_legal_elephant_move(board, from_r, from_c, to_r, to_c, piece[1])
        elif piece_type == Piece.HORSE:
            return RuleEngine._is_legal_horse_move(from_r, from_c, to_r, to_c)
        elif piece_type == Piece.CHARIOT:
            return RuleEngine._is_legal_chariot_move(board, from_r, from_c, to_r, to_c)
        elif piece_type == Piece.CANNON:
            return RuleEngine._is_legal_cannon_move(board, from_r, from_c, to_r, to_c)
        elif piece_type == Piece.PAWN:
            return RuleEngine._is_legal_pawn_move(from_r, from_c, to_r, to_c, piece[1])

        return True

    @staticmethod
    def _is_legal_king_move(from_r, from_c, to_r, to_c, color) -> bool:
        """将帅走法"""
        if color == Piece.RED:
            # 红方九宫: 7-9行, 3-5列
            if not (7 <= to_r <= 9 and 3 <= to_c <= 5):
                return False
        else:
            # 黑方九宫: 0-2行, 3-5列
            if not (0 <= to_r <= 2 and 3 <= to_c <= 5):
                return False
        # 只能走一格
        return abs(dr) + abs(dc) == 1

    @staticmethod
    def _is_legal_advisor_move(from_r, from_c, to_r, to_c, color) -> bool:
        """士走法"""
        if color == Piece.RED:
            if not (7 <= to_r <= 9 and 3 <= to_c <= 5):
                return False
        else:
            if not (0 <= to_r <= 2 and 3 <= to_c <= 5):
                return False
        # 斜走一格
        return abs(dr) == 1 and abs(dc) == 1

    @staticmethod
    def _is_legal_elephant_move(board, from_r, from_c, to_r, to_c, color) -> bool:
        """象走法"""
        # 象不能过河
        if color == Piece.RED and to_r > 4:
            return False
        if color == Piece.BLACK and to_r < 5:
            return False

        # 田字走法
        if not (abs(dr) == 2 and abs(dc) == 2):
            return False

        # 检查象眼
        mid_r, mid_c = from_r + dr // 2, from_c + dc // 2
        return board.get_piece(mid_r, mid_c) is None

    @staticmethod
    def _is_legal_horse_move(from_r, from_c, to_r, to_c) -> bool:
        """马走法"""
        dr, dc = to_r - from_r, to_c - from_c
        # 马走日
        if (abs(dr), abs(dc)) == (2, 1):
            # 蹩马腿
            mid_r = from_r + dr // 2
            return board.get_piece(mid_r, from_c) is None
        elif (abs(dr), abs(dc)) == (1, 2):
            mid_c = from_c + dc // 2
            return board.get_piece(from_r, mid_c) is None
        return False

    @staticmethod
    def _is_legal_chariot_move(board, from_r, from_c, to_r, to_c) -> bool:
        """车走法"""
        if from_r != to_r and from_c != to_c:
            return False  # 必须直线

        if from_r == to_r:
            # 水平
            c1, c2 = min(from_c, to_c), max(from_c, to_c)
            for c in range(c1 + 1, c2):
                if board.get_piece(from_r, c) is not None:
                    return False
        else:
            # 垂直
            r1, r2 = min(from_r, to_r), max(from_r, to_r)
            for r in range(r1 + 1, r2):
                if board.get_piece(r, from_c) is not None:
                    return False
        return True

    @staticmethod
    def _is_legal_cannon_move(board, from_r, from_c, to_r, to_c) -> bool:
        """炮走法"""
        if from_r != to_r and from_c != to_c:
            return False

        if from_r == to_r:
            # 水平
            c1, c2 = min(from_c, to_c), max(from_c, to_c)
            count = 0
            for c in range(c1 + 1, c2):
                if board.get_piece(from_r, c) is not None:
                    count += 1
            # 不吃子时不能有遮挡,吃子时正好一个遮挡
            dest = board.get_piece(to_r, to_c)
            if dest is None:
                return count == 0
            else:
                return count == 1
        else:
            # 垂直
            r1, r2 = min(from_r, to_r), max(from_r, to_r)
            count = 0
            for r in range(r1 + 1, r2):
                if board.get_piece(r, from_c) is not None:
                    count += 1
            dest = board.get_piece(to_r, to_c)
            if dest is None:
                return count == 0
            else:
                return count == 1

    @staticmethod
    def _is_legal_pawn_move(from_r, from_c, to_r, to_c, color) -> bool:
        """兵/卒走法"""
        dr, dc = to_r - from_r, to_c - from_c

        if color == Piece.RED:
            # 红兵只能前进(行号减小)
            if from_r > 4:
                # 未过河
                return dr == -1 and dc == 0
            else:
                # 过河
                if dc == 0:
                    return dr == -1
                else:
                    return dr == 0 and abs(dc) == 1
        else:
            # 黑卒只能前进(行号增大)
            if from_r < 5:
                return dr == 1 and dc == 0
            else:
                if dc == 0:
                    return dr == 1
                else:
                    return dr == 0 and abs(dc) == 1

    @staticmethod
    def _would_be_in_check(board: Board, move: Move, color: int) -> bool:
        """走棋后是否被将军"""
        # 模拟走棋
        from_piece = board.get_piece(move.from_row, move.from_col)
        to_piece = board.get_piece(move.to_row, move.to_col)

        board.set_piece(move.to_row, move.to_col, from_piece)
        board.set_piece(move.from_row, move.from_col, None)

        is_check = board.is_check(color)

        # 恢复
        board.set_piece(move.from_row, move.from_col, from_piece)
        board.set_piece(move.to_row, move.to_col, to_piece)

        return is_check
