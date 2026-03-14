# AIChineseChess 用户界面实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现完整的中国象棋用户界面，包含PyQt5主界面、棋盘渲染、对弈流程控制

**Architecture:** 使用PyQt5构建传统中国风界面，模块化设计便于维护和扩展

**Tech Stack:** Python 3.8+, PyQt5

---

## 文件结构

```
AIChineseChess/
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   ├── chess_board.py      # 棋盘组件
│   ├── chess_piece.py      # 棋子组件
│   ├── analysis_panel.py   # 分析面板
│   └── toolbar.py          # 工具栏
├── game/
│   ├── __init__.py
│   ├── game_controller.py  # 对弈控制器
│   └── game_state.py       # 游戏状态
└── requirements.txt
```

---

## Chunk 1: 基础界面框架

### Task 1: 项目配置与依赖

**Files:**
- Create: `requirements.txt`
- Create: `ui/__init__.py`
- Create: `game/__init__.py`

- [ ] **Step 1: 创建requirements.txt**

```txt
PyQt5>=5.15.0
numpy>=1.19.0
torch>=1.9.0
```

- [ ] **Step 2: 创建模块初始化文件**

```python
# ui/__init__.py
# UI模块
```

- [ ] **Step 3: 提交**

```bash
git add requirements.txt ui/__init__.py game/__init__.py
git commit -m "feat: add UI module structure"
```

---

### Task 2: 主窗口框架

**Files:**
- Create: `ui/main_window.py`

- [ ] **Step 1: 创建主窗口类**

```python
# ui/main_window.py
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QMenuBar, QMenu, QAction,
                             QToolBar, QStatusBar, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QKeySequence


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("AIChineseChess - 中国象棋AI")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)

        # 创建中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 主布局
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # 创建组件
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()

        # 显示界面
        self.center()

    def center(self):
        """窗口居中"""
        screen = self.screen()
        rect = self.frameGeometry()
        rect.moveCenter(screen.geometry().center())
        self.move(rect.topLeft())

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')

        new_action = QAction('新建(&N)', self)
        new_action.setShortcut(QKeySequence.New)
        file_menu.addAction(new_action)

        open_action = QAction('打开(&O)...', self)
        open_action.setShortcut(QKeySequence.Open)
        file_menu.addAction(open_action)

        save_action = QAction('保存(&S)', self)
        save_action.setShortcut(QKeySequence.Save)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        import_action = QAction('导入棋谱...', self)
        file_menu.addAction(import_action)

        export_action = QAction('导出棋谱...', self)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence.Quit)
        file_menu.addAction(exit_action)

        # 对弈菜单
        game_menu = menubar.addMenu('对弈(&G)')

        self.pvp_action = QAction('人人对战', self)
        game_menu.addAction(self.pvp_action)

        self.pve_action = QAction('人机对战', self)
        game_menu.addAction(self.pve_action)

        self.ai_watch_action = QAction('AI观察', self)
        game_menu.addAction(self.ai_watch_action)

        game_menu.addSeparator()

        resign_action = QAction('认输', self)
        game_menu.addAction(resign_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')

        about_action = QAction('关于', self)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 添加工具按钮
        new_action = QAction('新建', self)
        toolbar.addAction(new_action)

        open_action = QAction('打开', self)
        toolbar.addAction(open_action)

        save_action = QAction('保存', self)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        undo_action = QAction('悔棋', self)
        toolbar.addAction(undo_action)

        redo_action = QAction('撤销', self)
        toolbar.addAction(redo_action)

        toolbar.addSeparator()

        analyze_action = QAction('分析', self)
        toolbar.addAction(analyze_action)

    def create_status_bar(self):
        """创建状态栏"""
        self.statusBar().showMessage('就绪')

    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self, '确认退出',
            '确定要退出吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
```

- [ ] **Step 2: 测试主窗口**

```bash
cd "D:/PycharmProjects/AIChineseChess"
python -c "
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
print('Main window created successfully')
"
```

- [ ] **Step 3: 提交**

```bash
git add ui/main_window.py
git commit -m "feat: add main window framework"
```

---

## Chunk 2: 棋盘与棋子组件

### Task 3: 棋盘组件

**Files:**
- Create: `ui/chess_board.py`

- [ ] **Step 1: 创建棋盘组件**

```python
# ui/chess_board.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainter


class ChessBoard(QWidget):
    """棋盘组件 - 10行9列"""

    # 信号
    piece_clicked = pyqtSignal(int, int)  # 点击棋子 (row, col)
    square_clicked = pyqtSignal(int, int)  # 点击格子 (row, col)

    # 棋盘配置
    BOARD_ROWS = 10
    BOARD_COLS = 9
    CELL_SIZE = 60  # 格子大小
    PIECE_RADIUS = 26  # 棋子半径

    # 颜色配置
    BOARD_COLOR = QColor(139, 69, 19)  # 榧木色
    LINE_COLOR = QColor(80, 40, 10)  # 深棕色
    HIGHLIGHT_COLOR = QColor(255, 255, 0, 100)  # 选中高亮
    LAST_MOVE_COLOR = QColor(173, 216, 230, 100)  # 最后一步
    LEGAL_MOVE_COLOR = QColor(0, 255, 0, 80)  # 合法落子点

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board = None  # 后端棋盘对象
        self.selected_piece = None  # 选中的棋子 (row, col)
        self.legal_moves = []  # 合法落子点列表
        self.last_move = None  # 最后一步 ((from_r, from_c), (to_r, to_c))

        # 计算组件尺寸
        self.setMinimumSize(
            self.BOARD_COLS * self.CELL_SIZE + 40,
            self.BOARD_ROWS * self.CELL_SIZE + 40
        )

    def set_board(self, board):
        """设置棋盘对象"""
        self.board = board
        self.update()

    def paintEvent(self, event):
        """绘制棋盘"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制棋盘背景
        self.draw_board_background(painter)

        # 绘制网格线
        self.draw_grid_lines(painter)

        # 绘制九宫斜线
        self.draw_palace_lines(painter)

        # 绘制楚河汉界
        self.draw_river_and_border(painter)

        # 绘制高亮
        self.draw_highlights(painter)

        # 绘制棋子
        if self.board:
            self.draw_pieces(painter)

    def draw_board_background(self, painter):
        """绘制棋盘背景"""
        painter.fillRect(self.rect(), self.BOARD_COLOR)

    def draw_grid_lines(self, painter):
        """绘制网格线"""
        painter.setPen(QPen(self.LINE_COLOR, 2))

        # 绘制横线
        for row in range(self.BOARD_ROWS):
            y = self.get_y(row)
            painter.drawLine(
                self.get_x(0), y,
                self.get_x(self.BOARD_COLS - 1), y
            )

        # 绘制竖线 (中间7条，两端不画)
        for col in range(1, self.BOARD_COLS - 1):
            x = self.get_x(col)
            painter.drawLine(x, self.get_y(0), x, self.get_y(4))
            painter.drawLine(x, self.get_y(5), x, self.get_y(9))

        # 两端竖线
        painter.drawLine(self.get_x(0), self.get_y(0), self.get_x(0), self.get_y(9))
        painter.drawLine(self.get_x(8), self.get_y(0), self.get_x(8), self.get_y(9))

    def draw_palace_lines(self, painter):
        """绘制九宫斜线"""
        painter.setPen(QPen(self.LINE_COLOR, 1))

        # 红方九宫 (7-9行, 3-5列)
        # 士位斜线
        painter.drawLine(
            self.get_x(3), self.get_y(9),
            self.get_x(5), self.get_y(7)
        )
        painter.drawLine(
            self.get_x(5), self.get_y(9),
            self.get_x(3), self.get_y(7)
        )

        # 黑方九宫 (0-2行, 3-5列)
        painter.drawLine(
            self.get_x(3), self.get_y(2),
            self.get_x(5), self.get_y(0)
        )
        painter.drawLine(
            self.get_x(5), self.get_y(2),
            self.get_x(3), self.get_y(0)
        )

    def draw_river_and_border(self, painter):
        """绘制楚河汉界"""
        painter.setPen(QPen(self.LINE_COLOR, 2))

        # 楚河汉界线
        y1 = self.get_y(4) + self.CELL_SIZE // 2
        y2 = self.get_y(5) + self.CELL_SIZE // 2
        painter.drawLine(self.get_x(0), y1, self.get_x(8), y1)
        painter.drawLine(self.get_x(0), y2, self.get_x(8), y2)

        # 文字
        painter.setFont(QFont("KaiTi", 20, QFont.Bold))
        painter.drawText(self.get_x(1), y1 + 5, "楚")
        painter.drawText(self.get_x(2), y1 + 5, "河")
        painter.drawText(self.get_x(6), y1 + 5, "汉")
        painter.drawText(self.get_x(7), y1 + 5, "界")

    def draw_highlights(self, painter):
        """绘制高亮"""
        # 选中棋子高亮
        if self.selected_piece:
            r, c = self.selected_piece
            x = self.get_x(c)
            y = self.get_y(r)
            painter.fillRect(
                x - self.CELL_SIZE // 2,
                y - self.CELL_SIZE // 2,
                self.CELL_SIZE,
                self.CELL_SIZE
            )

        # 最后一步高亮
        if self.last_move:
            (from_r, from_c), (to_r, to_c) = self.last_move
            # 起点
            painter.fillRect(
                self.get_x(from_c) - self.CELL_SIZE // 2,
                self.get_y(from_r) - self.CELL_SIZE // 2,
                self.CELL_SIZE,
                self.CELL_SIZE
            )
            # 终点
            painter.fillRect(
                self.get_x(to_c) - self.CELL_SIZE // 2,
                self.get_y(to_r) - self.CELL_SIZE // 2,
                self.CELL_SIZE,
                self.CELL_SIZE
            )

        # 合法落子点
        for r, c in self.legal_moves:
            x = self.get_x(c)
            y = self.get_y(r)
            painter.setBrush(QBrush(self.LEGAL_MOVE_COLOR))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x, y, 15, 15)

    def draw_pieces(self, painter):
        """绘制棋子"""
        for row in range(self.BOARD_ROWS):
            for col in range(self.BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if piece:
                    self.draw_piece(painter, row, col, piece)

    def draw_piece(self, painter, row, col, piece):
        """绘制单个棋子"""
        x = self.get_x(col)
        y = self.get_y(row)
        piece_type, color = piece

        # 棋子颜色
        if color == 1:  # 红方
            piece_color = QColor(180, 30, 30)
            text_color = QColor(255, 215, 0)  # 金色
        else:  # 黑方
            piece_color = QColor(30, 30, 30)
            text_color = QColor(255, 215, 0)  # 金色

        # 绘制棋子圆形
        painter.setBrush(QBrush(piece_color))
        painter.setPen(QPen(QColor(255, 215, 0), 2))  # 金边
        painter.drawEllipse(x, y, self.PIECE_RADIUS * 2, self.PIECE_RADIUS * 2)

        # 绘制棋子文字
        from backend.board import Piece
        char = Piece.to_char(piece_type, color)
        painter.setPen(text_color)
        font = QFont("KaiTi", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(x - 10, y + 7, char)

    def get_x(self, col):
        """获取列的x坐标"""
        return 20 + col * self.CELL_SIZE + self.CELL_SIZE // 2

    def get_y(self, row):
        """获取行的y坐标"""
        return 20 + row * self.CELL_SIZE + self.CELL_SIZE // 2

    def get_square_at(self, x, y):
        """获取点击位置对应的格子坐标"""
        for row in range(self.BOARD_ROWS):
            for col in range(self.BOARD_COLS):
                sx = self.get_x(col)
                sy = self.get_y(row)
                if abs(x - sx) < self.CELL_SIZE // 2 and abs(y - sy) < self.CELL_SIZE // 2:
                    return row, col
        return None

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        pos = event.pos()
        square = self.get_square_at(pos.x(), pos.y())

        if square:
            row, col = square
            piece = self.board.get_piece(row, col) if self.board else None

            if self.selected_piece:
                # 如果已经选中棋子，检查是否点击了合法落子点
                if (row, col) in self.legal_moves:
                    self.square_clicked.emit(row, col)
                elif piece and piece[1] == self.board.current_player:
                    # 选中自己的另一个棋子
                    self.selected_piece = (row, col)
                    self.update_legal_moves()
                else:
                    # 点击其他地方，取消选中
                    self.selected_piece = None
                    self.legal_moves = []
            else:
                # 没有选中棋子
                if piece and self.board:
                    if piece[1] == self.board.current_player:
                        self.selected_piece = (row, col)
                        self.update_legal_moves()
                self.piece_clicked.emit(row, col)

            self.update()

    def update_legal_moves(self):
        """更新合法落子点"""
        if not self.selected_piece or not self.board:
            self.legal_moves = []
            return

        from backend.move import MoveGenerator
        r, c = self.selected_piece
        all_moves = MoveGenerator.get_legal_moves(self.board)
        self.legal_moves = [(m.to_row, m.to_col) for m in all_moves
                            if m.from_row == r and m.from_col == c]

    def set_selected_piece(self, row, col):
        """设置选中的棋子"""
        self.selected_piece = (row, col)
        self.update_legal_moves()
        self.update()

    def clear_selection(self):
        """清除选中"""
        self.selected_piece = None
        self.legal_moves = []
        self.update()

    def set_last_move(self, move):
        """设置最后一步"""
        self.last_move = move
        self.update()
```

- [ ] **Step 2: 测试棋盘组件**

```bash
cd "D:/PycharmProjects/AIChineseChess"
python -c "
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.chess_board import ChessBoard

app = QApplication(sys.argv)
board = ChessBoard()
print('ChessBoard created successfully')
"
```

- [ ] **Step 3: 提交**

```bash
git add ui/chess_board.py
git commit -m "feat: add chess board component"
```

---

## Chunk 3: 对弈控制器

### Task 4: 对弈控制器

**Files:**
- Create: `game/game_controller.py`

- [ ] **Step 1: 创建对弈控制器**

```python
# game/game_controller.py
from enum import Enum
from backend.board import Board, Piece
from backend.move import Move, MoveGenerator


class GameMode(Enum):
    """游戏模式"""
    PVP = 0  # 人人对战
    PVE = 1  # 人机对战
    AI_WATCH = 2  # AI观察


class GameController:
    """对弈控制器"""

    def __init__(self):
        self.board = Board()
        self.mode = None
        self.player_color = Piece.RED  # 玩家颜色
        self.move_history = []  # 走法历史
        self.redo_stack = []  # 撤销栈

    def start_game(self, mode: GameMode, player_color=Piece.RED):
        """开始游戏"""
        self.mode = mode
        self.player_color = player_color
        self.board.reset()
        self.move_history = []
        self.redo_stack = []

    def make_move(self, from_row, from_col, to_row, to_col) -> bool:
        """执行走法"""
        move = Move(from_row, from_col, to_row, to_col)

        # 检查是否合法
        legal_moves = MoveGenerator.get_legal_moves(self.board)
        if move not in legal_moves:
            return False

        # 执行走法
        self.board.make_move(move)
        self.move_history.append(move)
        self.redo_stack.clear()

        return True

    def undo_move(self) -> bool:
        """悔棋"""
        if not self.move_history:
            return False

        move = self.move_history.pop()
        self.board.undo_move()
        self.redo_stack.append(move)

        return True

    def redo_move(self) -> bool:
        """撤销悔棋"""
        if not self.redo_stack:
            return False

        move = self.redo_stack.pop()
        self.board.make_move(move)
        self.move_history.append(move)

        return True

    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return self.board.is_game_over()

    def get_result(self) -> int:
        """获取游戏结果"""
        return self.board.get_result()

    def get_current_player(self):
        """获取当前玩家"""
        return self.board.current_player

    def get_legal_moves(self):
        """获取当前合法走法"""
        return MoveGenerator.get_legal_moves(self.board)

    def is_player_turn(self) -> bool:
        """是否轮到玩家走棋"""
        if self.mode == GameMode.PVE:
            return self.board.current_player == self.player_color
        return True
```

- [ ] **Step 2: 测试对弈控制器**

```bash
cd "D:/PycharmProjects/AIChineseChess"
python -c "
from game.game_controller import GameController, GameMode
from backend.board import Piece

controller = GameController()
controller.start_game(GameMode.PVP)
print('Game started')
print(f'Current player: {controller.get_current_player()}')
print(f'Legal moves: {len(controller.get_legal_moves())}')
"
```

- [ ] **Step 3: 提交**

```bash
git add game/game_controller.py
git commit -m "feat: add game controller"
```

---

## Chunk 4: 集成测试

### Task 5: 完整集成

**Files:**
- Modify: `ui/main_window.py`

- [ ] **Step 1: 集成棋盘到主窗口**

```python
# 在 main_window.py 中添加
from ui.chess_board import ChessBoard
from game.game_controller import GameController, GameMode
from backend.board import Piece
from backend.move import Move

# 在 __init__ 中添加
self.game_controller = GameController()
self.chess_board = ChessBoard()
self.main_layout.addWidget(self.chess_board)

# 连接信号
self.chess_board.square_clicked.connect(self.on_square_clicked)
```

- [ ] **Step 2: 添加走棋处理**

```python
def on_square_clicked(self, row, col):
    """处理点击格子"""
    if not self.game_controller.is_player_turn():
        return

    # 获取当前选中棋子
    selected = self.chess_board.selected_piece

    if selected:
        from_row, from_col = selected
        if self.game_controller.make_move(from_row, from_col, row, col):
            # 走棋成功
            self.chess_board.set_last_move(
                ((from_row, from_col), (row, col))
            )
            self.chess_board.clear_selection()

            # 检查游戏结束
            if self.game_controller.is_game_over():
                result = self.game_controller.get_result()
                self.show_game_over(result)

            # 切换到AI
            if self.game_controller.mode == GameMode.PVE:
                self.request_ai_move()
    else:
        # 选中新棋子
        piece = self.game_controller.board.get_piece(row, col)
        if piece and piece[1] == self.game_controller.get_current_player():
            self.chess_board.set_selected_piece(row, col)

def show_game_over(self, result):
    """显示游戏结束"""
    from PyQt5.QtWidgets import QMessageBox
    if result == 1:
        QMessageBox.information(self, '游戏结束', '红方获胜！')
    elif result == -1:
        QMessageBox.information(self, '游戏结束', '黑方获胜！')
    else:
        QMessageBox.information(self, '游戏结束', '平局！')

def request_ai_move(self):
    """请求AI走棋"""
    # TODO: 实现AI走棋
    pass
```

- [ ] **Step 3: 测试完整流程**

```bash
cd "D:/PycharmProjects/AIChineseChess"
python -c "
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from game.game_controller import GameMode

app = QApplication(sys.argv)
window = MainWindow()

# 启动人人对战测试
window.game_controller.start_game(GameMode.PVP)
window.chess_board.set_board(window.game_controller.board)
window.show()

print('Full UI test passed')
"
```

- [ ] **Step 4: 提交**

```bash
git add ui/main_window.py
git commit -m "feat: integrate chess board and game controller into main window"
```

---

## 总结

此计划实现完整的中国象棋UI界面：

1. **主窗口** - 菜单栏、工具栏、状态栏
2. **棋盘组件** - 10×9棋盘绘制、棋子渲染、高亮效果
3. **对弈控制器** - 游戏模式管理、走棋、悔棋
4. **完整集成** - 人人对战流程

完成后可进行基本的人人对战测试。
