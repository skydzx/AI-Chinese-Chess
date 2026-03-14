# ui/analysis_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt


class AnalysisPanel(QWidget):
    """局面分析面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("局面分析")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.eval_label = QLabel("评估: --")
        layout.addWidget(self.eval_label)

        self.best_move_label = QLabel("最佳走法: --")
        layout.addWidget(self.best_move_label)

        self.candidate_label = QLabel("候选走法:")
        layout.addWidget(self.candidate_label)

        self.candidate_edit = QTextEdit()
        self.candidate_edit.setReadOnly(True)
        self.candidate_edit.setMaximumHeight(150)
        layout.addWidget(self.candidate_edit)

        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.clicked.connect(self.on_analyze)
        layout.addWidget(self.analyze_btn)

        layout.addStretch()
        self.setLayout(layout)

    def set_board(self, board):
        self.board = board

    def on_analyze(self):
        if not hasattr(self, 'board') or not self.board:
            return
        try:
            import torch
            from ai.network import ChineseChessNet
            from ai.mcts import MCTS
            from backend.move import MoveGenerator
            from backend.board import Piece

            net = ChineseChessNet(num_channels=64, num_res_blocks=4)
            try:
                net.load_state_dict(torch.load('data/models/model_latest.pth', map_location='cpu')['network'])
            except:
                pass

            mcts = MCTS(net, num_simulations=30)
            policy, value = mcts.search(self.board)

            # 显示评估
            v = value.item() if hasattr(value, 'item') else value
            eval_text = f"评估: {v:+.3f}"
            if v > 0.3:
                eval_text += " (红方优势)"
            elif v < -0.3:
                eval_text += " (黑方优势)"
            self.eval_label.setText(eval_text)

            # 显示最佳走法
            best_idx = policy.argmax()
            from backend.move import MOVE_INDEX_TO_ACTION
            if best_idx in MOVE_INDEX_TO_ACTION:
                fr, fc, tr, tc = MOVE_INDEX_TO_ACTION[best_idx]
                self.best_move_label.setText(f"最佳走法: {fc}{9-fr}->{tc}{9-tr}")

            # 显示候选走法
            moves = MoveGenerator.get_legal_moves(self.board)
            moves.sort(key=lambda m: policy[m.to_index()] if m.to_index() >= 0 else 0, reverse=True)
            top_moves = moves[:5]
            text = ""
            for i, m in enumerate(top_moves):
                prob = policy[m.to_index()] if m.to_index() >= 0 else 0
                text += f"{i+1}. {m.from_col}{9-m.from_row}-{m.to_col}{9-m.to_row} ({prob:.2%})\n"
            self.candidate_edit.setText(text)

        except Exception as e:
            self.eval_label.setText(f"分析出错: {e}")

    def update_position(self, board):
        self.board = board
        self.on_analyze()
