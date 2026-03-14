# ui/main_window.py
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QMenuBar, QMenu, QAction,
                             QToolBar, QStatusBar, QMessageBox, QFileDialog, QLabel, QVBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.game_controller = None
        self.chess_board = None
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
        new_action.triggered.connect(self.on_new_game)
        file_menu.addAction(new_action)

        open_action = QAction('打开(&O)...', self)
        open_action.setShortcut(QKeySequence.Open)
        file_menu.addAction(open_action)

        save_action = QAction('保存(&S)', self)
        save_action.setShortcut(QKeySequence.Save)
        file_menu.addAction(save_action)

        file_menu.addSeparator()
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 对弈菜单
        game_menu = menubar.addMenu('对弈(&G)')
        pvp_action = QAction('人人对战', self)
        pvp_action.triggered.connect(lambda: self.start_game(0))
        game_menu.addAction(pvp_action)

        pve_action = QAction('人机对战(执红)', self)
        pve_action.triggered.connect(lambda: self.start_game(1))
        game_menu.addAction(pve_action)

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

        new_action = QAction('新建', self)
        new_action.triggered.connect(self.on_new_game)
        toolbar.addAction(new_action)

        toolbar.addSeparator()

        undo_action = QAction('悔棋', self)
        undo_action.triggered.connect(self.on_undo)
        toolbar.addAction(undo_action)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_label = QLabel('就绪')
        self.statusBar().addWidget(self.status_label)

    def on_new_game(self):
        """新建游戏"""
        if self.game_controller:
            self.game_controller.start_game(self.game_controller.mode or 0)
            if self.chess_board:
                self.chess_board.set_board(self.game_controller.board)
                self.chess_board.update()
            self.update_status('新建游戏')

    def start_game(self, mode):
        """开始游戏"""
        from game.game_controller import GameController, GameMode
        self.game_controller = GameController()
        self.game_controller.start_game(GameMode(mode))

        from ui.chess_board import ChessBoard
        if not self.chess_board:
            self.chess_board = ChessBoard()
            self.main_layout.addWidget(self.chess_board, 1)
            self.chess_board.square_clicked.connect(self.on_square_clicked)

        self.chess_board.set_board(self.game_controller.board)
        self.chess_board.update()
        self.update_status('人人对战' if mode == 0 else '人机对战')

    def on_square_clicked(self, row, col):
        """处理点击格子"""
        if not self.game_controller:
            return

        selected = self.chess_board.selected_piece
        if selected:
            from_row, from_col = selected
            if self.game_controller.make_move(from_row, from_col, row, col):
                self.chess_board.set_last_move(((from_row, from_col), (row, col)))
                self.chess_board.clear_selection()
                self.chess_board.update()

                if self.game_controller.is_game_over():
                    result = self.game_controller.get_result()
                    self.show_game_over(result)
        else:
            piece = self.game_controller.board.get_piece(row, col)
            if piece and piece[1] == self.game_controller.get_current_player():
                self.chess_board.set_selected_piece(row, col)

    def show_game_over(self, result):
        """显示游戏结束"""
        msg = '红方获胜！' if result == 1 else ('黑方获胜！' if result == -1 else '平局！')
        QMessageBox.information(self, '游戏结束', msg)

    def on_undo(self):
        """悔棋"""
        if self.game_controller and self.game_controller.undo_move():
            self.chess_board.update()

    def update_status(self, text):
        """更新状态栏"""
        self.status_label.setText(text)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
