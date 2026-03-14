# ui/main_window.py
import sys
import threading
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QMenuBar, QMenu, QAction,
                             QToolBar, QStatusBar, QMessageBox, QFileDialog, QLabel)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.game_controller = None
        self.chess_board = None
        self.ai_engine = None
        self.ai_thinking = False
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("AIChineseChess - 中国象棋AI")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.center()

    def center(self):
        screen = self.screen()
        rect = self.frameGeometry()
        rect.moveCenter(screen.geometry().center())
        self.move(rect.topLeft())

    def create_menu_bar(self):
        menubar = self.menuBar()

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

        game_menu = menubar.addMenu('对弈(&G)')
        pvp_action = QAction('人人对战', self)
        pvp_action.triggered.connect(lambda: self.start_game(0))
        game_menu.addAction(pvp_action)

        pve_action = QAction('人机对战(执红)', self)
        pve_action.triggered.connect(lambda: self.start_game(1))
        game_menu.addAction(pve_action)

        pve_black_action = QAction('人机对战(执黑)', self)
        pve_black_action.triggered.connect(lambda: self.start_game(2))
        game_menu.addAction(pve_black_action)

        game_menu.addSeparator()
        resign_action = QAction('认输', self)
        resign_action.triggered.connect(self.on_resign)
        game_menu.addAction(resign_action)

        help_menu = menubar.addMenu('帮助(&H)')
        about_action = QAction('关于', self)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
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
        self.status_label = QLabel('就绪')
        self.move_label = QLabel('')
        self.statusBar().addWidget(self.status_label)
        self.statusBar().addWidget(self.move_label)

    def on_new_game(self):
        if self.game_controller:
            mode = self.game_controller.mode.value if self.game_controller.mode else 0
            self.game_controller.start_game(type(self.game_controller.mode)(mode))
            if self.chess_board:
                self.chess_board.set_board(self.game_controller.board)
                self.chess_board.update()
            self.update_status('新建游戏')

    def start_game(self, mode):
        from game.game_controller import GameController, GameMode
        from backend.board import Piece

        self.game_controller = GameController()

        # mode: 0=PVP, 1=PVE红, 2=PVE黑
        if mode == 0:
            self.game_controller.start_game(GameMode.PVP)
        elif mode == 1:
            self.game_controller.start_game(GameMode.PVE, Piece.RED)
        else:
            self.game_controller.start_game(GameMode.PVE, Piece.BLACK)

        from ui.chess_board import ChessBoard
        if not self.chess_board:
            self.chess_board = ChessBoard()
            self.main_layout.addWidget(self.chess_board, 1)
            self.chess_board.square_clicked.connect(self.on_square_clicked)

        self.chess_board.set_board(self.game_controller.board)
        self.chess_board.update()

        mode_name = ['人人对战', '人机对战(执红)', '人机对战(执黑)'][mode]
        self.update_status(mode_name)

        # 如果是PVE模式且AI先手，让AI走第一步
        if mode in [1, 2]:
            if mode == 2:  # AI执红先手
                QTimer.singleShot(500, self.request_ai_move)

    def on_square_clicked(self, row, col):
        if not self.game_controller or self.ai_thinking:
            return

        # PVE模式下检查是否轮到玩家
        if self.game_controller.mode.value == 1:  # 玩家执红
            if self.game_controller.get_current_player() != self.game_controller.player_color:
                return
        elif self.game_controller.mode.value == 2:  # 玩家执黑
            if self.game_controller.get_current_player() != self.game_controller.player_color:
                return

        selected = self.chess_board.selected_piece
        if selected:
            from_row, from_col = selected
            if self.game_controller.make_move(from_row, from_col, row, col):
                self.chess_board.set_last_move(((from_row, from_col), (row, col)))
                self.chess_board.clear_selection()
                self.chess_board.update()
                self.update_move_count()

                if self.game_controller.is_game_over():
                    result = self.game_controller.get_result()
                    self.show_game_over(result)
                elif self.game_controller.mode.value in [1, 2]:
                    # PVE模式，AI走棋
                    QTimer.singleShot(300, self.request_ai_move)
        else:
            piece = self.game_controller.board.get_piece(row, col)
            if piece and piece[1] == self.game_controller.get_current_player():
                self.chess_board.set_selected_piece(row, col)

    def request_ai_move(self):
        """请求AI走棋"""
        if not self.game_controller:
            return
        if self.game_controller.is_game_over():
            return
        if self.game_controller.mode.value == 1:  # 玩家执红，AI是黑方
            if self.game_controller.get_current_player() != -1:  # RED=1, BLACK=-1
                return
        elif self.game_controller.mode.value == 2:  # 玩家执黑，AI是红方
            if self.game_controller.get_current_player() != 1:
                return
        else:
            return  # PVP模式不需要AI

        self.ai_thinking = True
        self.update_status('AI思考中...')

        def ai_thread():
            try:
                move = self.get_ai_move()
                if move:
                    from backend.move import Move
                    m = Move(move[0], move[1], move[2], move[3])
                    self.game_controller.board.make_move(m)
                    self.game_controller.move_history.append(m)
                    self.chess_board.set_last_move(((move[0], move[1]), (move[2], move[3])))
                    self.chess_board.update()
                    self.update_move_count()

                    if self.game_controller.is_game_over():
                        result = self.game_controller.get_result()
                        QMessageBox.information(self, '游戏结束', '红方获胜！' if result == 1 else ('黑方获胜！' if result == -1 else '平局！'))
            except Exception as e:
                print(f"AI error: {e}")
            finally:
                self.ai_thinking = False
                self.update_status('轮到你走棋')

        threading.Thread(target=ai_thread, daemon=True).start()

    def get_ai_move(self):
        """简单的随机AI（后续可以替换为MCTS）"""
        from backend.move import MoveGenerator
        import random

        moves = MoveGenerator.get_legal_moves(self.game_controller.board)
        if moves:
            m = random.choice(moves)
            return (m.from_row, m.from_col, m.to_row, m.to_col)
        return None

    def show_game_over(self, result):
        msg = '红方获胜！' if result == 1 else ('黑方获胜！' if result == -1 else '平局！')
        QMessageBox.information(self, '游戏结束', msg)

    def on_undo(self):
        if self.game_controller and self.game_controller.undo_move():
            # PVE模式下需要撤销两步
            if self.game_controller.mode.value in [1, 2]:
                self.game_controller.undo_move()
            self.chess_board.update()
            self.update_move_count()

    def on_resign(self):
        if self.game_controller:
            result = -self.game_controller.get_current_player()
            self.show_game_over(result)

    def update_status(self, text):
        self.status_label.setText(text)

    def update_move_count(self):
        count = len(self.game_controller.move_history)
        player = '红方' if self.game_controller.get_current_player() == 1 else '黑方'
        self.move_label.setText(f'步数:{count} | {player}回合')


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
