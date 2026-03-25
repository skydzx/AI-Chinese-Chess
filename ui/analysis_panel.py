# ui/analysis_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QListWidget
from PyQt5.QtCore import Qt


class AnalysisPanel(QWidget):
    """局面分析面板 - 显示走棋记录和AI思路"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.move_history = []  # 记录所有走法
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 标题
        title = QLabel("对弈记录")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # 红方走法
        red_label = QLabel("🔴 红方")
        red_label.setStyleSheet("color: #c41e3a; font-weight: bold;")
        layout.addWidget(red_label)

        self.red_moves_list = QListWidget()
        self.red_moves_list.setMaximumHeight(120)
        layout.addWidget(self.red_moves_list)

        # 黑方走法
        black_label = QLabel("⚫ 黑方")
        black_label.setStyleSheet("color: #2d2d2d; font-weight: bold;")
        layout.addWidget(black_label)

        self.black_moves_list = QListWidget()
        self.black_moves_list.setMaximumHeight(120)
        layout.addWidget(self.black_moves_list)

        # AI思路
        ai_label = QLabel("🤖 AI思路")
        ai_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        layout.addWidget(ai_label)

        self.ai_thinking = QTextEdit()
        self.ai_thinking.setReadOnly(True)
        self.ai_thinking.setMaximumHeight(150)
        self.ai_thinking.setPlaceholderText("等待AI分析...")
        layout.addWidget(self.ai_thinking)

        # 局面评估
        self.eval_label = QLabel("评估: --")
        self.eval_label.setStyleSheet("font-size: 14px; padding: 5px; background: #f0f0f0;")
        layout.addWidget(self.eval_label)

        layout.addStretch()
        self.setLayout(layout)

    def set_board(self, board):
        self.board = board

    def add_move(self, move_text, is_red):
        """添加一步走法"""
        self.move_history.append((move_text, is_red))
        if is_red:
            item_text = f"{len(self.red_moves_list) + 1}. {move_text}"
            self.red_moves_list.addItem(item_text)
        else:
            item_text = f"{len(self.black_moves_list) + 1}. {move_text}"
            self.black_moves_list.addItem(item_text)

    def set_ai_thinking(self, text):
        """设置AI思路"""
        self.ai_thinking.setText(text)

    def update_eval(self, text):
        """更新评估"""
        self.eval_label.setText(text)

    def clear(self):
        """清空记录"""
        self.move_history.clear()
        self.red_moves_list.clear()
        self.black_moves_list.clear()
        self.ai_thinking.clear()
        self.eval_label.setText("评估: --")
