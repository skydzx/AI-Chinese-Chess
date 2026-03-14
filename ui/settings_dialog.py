# ui/settings_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QCheckBox, QPushButton, QGroupBox


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # AI难度
        ai_group = QGroupBox("AI设置")
        ai_layout = QVBoxLayout()

        self.mcts_simulations = QSpinBox()
        self.mcts_simulations.setRange(10, 500)
        self.mcts_simulations.setValue(50)
        self.mcts_simulations.setSuffix(" 次模拟")
        ai_layout.addWidget(QLabel("MCTS模拟次数:"))
        ai_layout.addWidget(self.mcts_simulations)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # 显示设置
        display_group = QGroupBox("显示设置")
        display_layout = QVBoxLayout()

        self.show_legal_moves = QCheckBox("显示合法落子点")
        self.show_legal_moves.setChecked(True)
        display_layout.addWidget(self.show_legal_moves)

        self.show_last_move = QCheckBox("显示最后一步")
        self.show_last_move.setChecked(True)
        display_layout.addWidget(self.show_last_move)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
