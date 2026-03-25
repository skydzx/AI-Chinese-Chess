# ui/chess_board.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont


class ChessBoard(QWidget):
    """棋盘组件 - 10行9列"""
    piece_clicked = pyqtSignal(int, int)
    square_clicked = pyqtSignal(int, int)

    BOARD_ROWS = 10
    BOARD_COLS = 9
    CELL_SIZE = 60
    PIECE_RADIUS = 26

    BOARD_COLOR = QColor(139, 69, 19)
    LINE_COLOR = QColor(80, 40, 10)
    LEGAL_MOVE_COLOR = QColor(0, 255, 0, 80)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board = None
        self.selected_piece = None
        self.legal_moves = []
        self.last_move = None
        self.flipped = False  # 翻转标志
        self.setMinimumSize(
            self.BOARD_COLS * self.CELL_SIZE + 40,
            self.BOARD_ROWS * self.CELL_SIZE + 40
        )

    def flip_board(self):
        """翻转棋盘"""
        self.flipped = not self.flipped
        self.update()

    def set_board(self, board):
        self.board = board
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_board_background(painter)
        self.draw_grid_lines(painter)
        self.draw_palace_lines(painter)
        self.draw_river_and_border(painter)
        self.draw_highlights(painter)
        if self.board:
            self.draw_pieces(painter)

    def draw_board_background(self, painter):
        painter.fillRect(self.rect(), self.BOARD_COLOR)

    def draw_grid_lines(self, painter):
        painter.setPen(QPen(self.LINE_COLOR, 2))
        for row in range(self.BOARD_ROWS):
            y = self.get_y(row)
            painter.drawLine(self.get_x(0), y, self.get_x(8), y)
        for col in range(1, 8):
            x = self.get_x(col)
            painter.drawLine(x, self.get_y(0), x, self.get_y(4))
            painter.drawLine(x, self.get_y(5), x, self.get_y(9))
        painter.drawLine(self.get_x(0), self.get_y(0), self.get_x(0), self.get_y(9))
        painter.drawLine(self.get_x(8), self.get_y(0), self.get_x(8), self.get_y(9))

    def draw_palace_lines(self, painter):
        painter.setPen(QPen(self.LINE_COLOR, 1))
        painter.drawLine(self.get_x(3), self.get_y(9), self.get_x(5), self.get_y(7))
        painter.drawLine(self.get_x(5), self.get_y(9), self.get_x(3), self.get_y(7))
        painter.drawLine(self.get_x(3), self.get_y(2), self.get_x(5), self.get_y(0))
        painter.drawLine(self.get_x(5), self.get_y(2), self.get_x(3), self.get_y(0))

    def draw_river_and_border(self, painter):
        # 绘制楚河汉界文字 - 始终显示在河界中央
        painter.setFont(QFont("KaiTi", 20, QFont.Bold))
        # 河界始终在棋盘视觉中央 (行4和行5之间)
        # 使用固定的Y坐标计算，不管flip状态
        center_y = 20 + 4 * self.CELL_SIZE + 10  # 行4和5之间的固定位置
        # 楚河: 左侧区域 (列2附近)
        chuhe_x = self.get_x(2) + 20
        # 汉界: 右侧区域 (列6附近)
        hanjie_x = self.get_x(6) - 20
        # 绘制 - 使用矩形区域居中对齐
        painter.drawText(int(chuhe_x - 30), int(center_y), 60, 30, Qt.AlignCenter, "楚")
        painter.drawText(int(chuhe_x + 10), int(center_y), 60, 30, Qt.AlignCenter, "河")
        painter.drawText(int(hanjie_x - 30), int(center_y), 60, 30, Qt.AlignCenter, "汉")
        painter.drawText(int(hanjie_x + 10), int(center_y), 60, 30, Qt.AlignCenter, "界")

    def draw_highlights(self, painter):
        if self.last_move:
            (from_r, from_c), (to_r, to_c) = self.last_move
            highlight_color = QColor(255, 255, 0, 100)  # 黄色高亮
            for r, c in [(from_r, from_c), (to_r, to_c)]:
                x = self.get_x(c) - self.CELL_SIZE // 2
                y = self.get_y(r) - self.CELL_SIZE // 2
                painter.fillRect(x, y, self.CELL_SIZE, self.CELL_SIZE, highlight_color)
        for r, c in self.legal_moves:
            x, y = self.get_x(c), self.get_y(r)
            painter.setBrush(QBrush(self.LEGAL_MOVE_COLOR))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x, y, 15, 15)

    def draw_pieces(self, painter):
        for row in range(self.BOARD_ROWS):
            for col in range(self.BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if piece:
                    self.draw_piece(painter, row, col, piece)

    def draw_piece(self, painter, row, col, piece):
        x, y = self.get_x(col), self.get_y(row)
        piece_type, color = piece
        piece_color = QColor(180, 30, 30) if color == 1 else QColor(30, 30, 30)
        text_color = QColor(255, 215, 0)
        r = self.PIECE_RADIUS
        # 绘制圆形棋子 - drawEllipse使用左上角坐标+宽高
        painter.setBrush(QBrush(piece_color))
        painter.setPen(QPen(QColor(255, 215, 0), 2))
        painter.drawEllipse(x - r, y - r, r * 2, r * 2)
        # 绘制棋子文字 - 居中显示
        from backend.board import Piece
        char = Piece.to_char(piece_type, color)
        painter.setPen(text_color)
        painter.setFont(QFont("KaiTi", 16, QFont.Bold))
        painter.drawText(x - r, y - r, r * 2, r * 2, Qt.AlignCenter, char)

    def get_x(self, col):
        return 20 + col * self.CELL_SIZE + self.CELL_SIZE // 2

    def get_y(self, row):
        if self.flipped:
            # 翻转: row 0 显示在底部
            return 20 + (self.BOARD_ROWS - 1 - row) * self.CELL_SIZE + self.CELL_SIZE // 2
        return 20 + row * self.CELL_SIZE + self.CELL_SIZE // 2

    def get_row_from_y(self, y):
        """根据y坐标获取row"""
        if self.flipped:
            row = (y - 20 - self.CELL_SIZE // 2) // self.CELL_SIZE
            row = self.BOARD_ROWS - 1 - row
            return max(0, min(self.BOARD_ROWS - 1, row))
        else:
            row = (y - 20 - self.CELL_SIZE // 2) // self.CELL_SIZE
            return max(0, min(self.BOARD_ROWS - 1, row))

    def get_col_from_x(self, x):
        """根据x坐标获取col"""
        col = (x - 20 - self.CELL_SIZE // 2) // self.CELL_SIZE
        return max(0, min(self.BOARD_COLS - 1, col))

    def get_square_at(self, x, y):
        # 使用精确的行列计算
        row = self.get_row_from_y(y)
        col = self.get_col_from_x(x)
        # 验证是否在有效范围内
        if 0 <= row < self.BOARD_ROWS and 0 <= col < self.BOARD_COLS:
            return row, col
        return None

    def mousePressEvent(self, event):
        if not self.board:
            return
        pos = event.pos()
        square = self.get_square_at(pos.x(), pos.y())
        if square:
            row, col = square
            piece = self.board.get_piece(row, col)
            if self.selected_piece:
                if (row, col) in self.legal_moves:
                    self.square_clicked.emit(row, col)
                else:
                    self.selected_piece = None
                    self.legal_moves = []
            else:
                if piece and piece[1] == self.board.current_player:
                    self.selected_piece = (row, col)
                    self.update_legal_moves()
            self.update()

    def update_legal_moves(self):
        if not self.selected_piece or not self.board:
            self.legal_moves = []
            return
        from backend.move import MoveGenerator
        r, c = self.selected_piece
        all_moves = MoveGenerator.get_legal_moves(self.board)
        self.legal_moves = [(m.to_row, m.to_col) for m in all_moves if m.from_row == r and m.from_col == c]

    def set_selected_piece(self, row, col):
        self.selected_piece = (row, col)
        self.update_legal_moves()
        self.update()

    def clear_selection(self):
        self.selected_piece = None
        self.legal_moves = []
        self.update()

    def set_last_move(self, move):
        self.last_move = move
        self.update()
