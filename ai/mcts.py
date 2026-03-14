import math
import copy
import numpy as np
import torch
from typing import Dict, Tuple

from backend.board import Board
from backend.encoder import BoardEncoder
from backend.move import MoveGenerator, Move


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

    def __init__(self, network, num_simulations=100, c_puct=1.5):
        self.network = network
        self.num_simulations = num_simulations
        self.c_puct = c_puct

    def search(self, board: Board) -> Tuple[np.ndarray, float]:
        """
        执行MCTS搜索
        返回: (策略概率, 局面价值)
        """
        root_state = (copy.deepcopy(board), board.current_player)
        root = MCTSNode(root_state)

        # 初始化根节点
        self._expand_node(root, board)

        for _ in range(self.num_simulations):
            board_copy = copy.deepcopy(board)
            node = root
            history = []  # 记录路径用于回溯

            # 选择
            while node.is_expanded() and not board_copy.is_game_over():
                move, node = self._select_child(node, board_copy)
                history.append((node, board_copy.current_player))
                board_copy.make_move(move)

            # 展开
            if not board_copy.is_game_over():
                self._expand_node(node, board_copy)

            # 评估
            value = self._evaluate(board_copy)

            # 回溯
            self._backpropagate(node, value, history)

        # 返回根节点策略 (访问次数归一化)
        return self._get_policy(root), root.q_value

    def _select_child(self, node: MCTSNode, board: Board):
        """PUCT选择"""
        best_score = -float('inf')
        best_child = None
        best_move = None

        for move, child in node.children.items():
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
                best_move = move

        return best_move, best_child

    def _expand_node(self, node: MCTSNode, board: Board):
        """展开节点 - 使用神经网络预测"""
        # 编码棋盘
        encoder = BoardEncoder()
        x = encoder.encode(board)

        # 检查是否有GPU
        device = next(self.network.parameters()).device
        x_tensor = torch.from_numpy(x).unsqueeze(0).to(device)

        with torch.no_grad():
            policy_logits, value = self.network(x_tensor)

        policy = policy_logits.squeeze(0).cpu().numpy()

        # 获取合法走法
        legal_moves = MoveGenerator.get_legal_moves(board)

        # 创建子节点
        for move in legal_moves:
            idx = move.to_index()
            if 0 <= idx < len(policy):
                prior = policy[idx]
                node.children[move] = MCTSNode(
                    (board, -board.current_player),
                    parent=node,
                    prior=prior
                )

    def _evaluate(self, board: Board) -> float:
        """评估局面"""
        encoder = BoardEncoder()
        x = encoder.encode(board)

        device = next(self.network.parameters()).device
        x_tensor = torch.from_numpy(x).unsqueeze(0).to(device)

        with torch.no_grad():
            _, value = self.network(x_tensor)

        return value.item()

    def _backpropagate(self, node: MCTSNode, value: float, history: list):
        """回溯更新"""
        # 首先更新最后访问的节点
        while node is not None:
            node.visit_count += 1
            node.value_sum += value
            value = -value  # 翻转视角
            node = node.parent

    def _get_policy(self, root: MCTSNode) -> np.ndarray:
        """获取策略分布"""
        visits = np.zeros(2098)
        for move, child in root.children.items():
            idx = move.to_index()
            if 0 <= idx < 2098:
                visits[idx] = child.visit_count

        # 归一化
        total = visits.sum()
        if total > 0:
            visits /= total
        return visits
