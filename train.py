#!/usr/bin/env python3
"""训练脚本 - 使用自对弈强化学习训练AI"""

import os
import sys

# 解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import torch
import numpy as np
from collections import deque
import random
import copy

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.board import Board, Piece
from backend.move import Move, MoveGenerator
from backend.encoder import BoardEncoder
from ai.network import ChineseChessNet
from ai.mcts import MCTS


class Trainer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        self.net = ChineseChessNet(num_channels=128, num_res_blocks=8).to(self.device)
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=0.001)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=100)

        self.replay_buffer = deque(maxlen=50000)

        # 创建模型目录
        os.makedirs("data/models", exist_ok=True)

    def selfplay(self, num_games=10, temperature=1.0):
        """自对弈生成训练数据"""
        games = []
        for _ in range(num_games):
            game_data = self.play_one_game(temperature)
            games.extend(game_data)
        return games

    def play_one_game(self, temperature=1.0, max_moves=200):
        """下一局自对弈"""
        from backend.move import LEGAL_MOVE_INDICES

        board = Board()
        mcts = MCTS(self.net, num_simulations=100)

        game_data = []
        history = []
        move_count = 0

        while not board.is_game_over() and move_count < max_moves:
            move_count += 1
            # MCTS搜索
            policy, _ = mcts.search(board)

            # 过滤非法走法和NaN
            legal_moves = MoveGenerator.get_legal_moves(board)
            valid_policy = np.zeros(8010)  # 神经网络输出维度

            for move in legal_moves:
                raw_idx = move.to_index()
                policy_idx = LEGAL_MOVE_INDICES.get(raw_idx, -1)
                if policy_idx >= 0 and policy_idx < len(policy) and not np.isnan(policy[policy_idx]) and policy[policy_idx] > 0:
                    valid_policy[policy_idx] = policy[policy_idx]

            # 归一化
            if valid_policy.sum() > 0:
                valid_policy /= valid_policy.sum()
            else:
                # 如果没有有效策略，使用均匀分布
                for move in legal_moves:
                    raw_idx = move.to_index()
                    policy_idx = LEGAL_MOVE_INDICES.get(raw_idx, -1)
                    if policy_idx >= 0:
                        valid_policy[policy_idx] = 1.0 / len(legal_moves)

            # 记录状态
            encoder = BoardEncoder()
            state = encoder.encode(board, history[-3:] if history else None)
            game_data.append((state, valid_policy.copy()))

            # 采样走法
            if temperature > 0.001:
                p = valid_policy ** (1/temperature)
                if p.sum() > 0:
                    p /= p.sum()
                    policy_idx = np.random.choice(len(p), p=p)
                else:
                    # 随机选择
                    policy_idx = random.choice([LEGAL_MOVE_INDICES.get(m.to_index(), 0) for m in legal_moves])
            else:
                policy_idx = valid_policy.argmax()

            # 将 policy 索引转回原始 move
            from backend.move import MOVE_INDEX_TO_ACTION
            fr, fc, tr, tc = MOVE_INDEX_TO_ACTION[policy_idx]
            move = Move(fr, fc, tr, tc)
            board.make_move(move)
            history.append(copy.deepcopy(board))

        # 计算结果
        if board.is_game_over():
            result = board.get_result()
        else:
            # 超时平局
            result = 0

        # 回溯赋值
        for i, (state, policy) in enumerate(game_data):
            player = Piece.RED if i % 2 == 0 else Piece.BLACK
            value = result if player == Piece.RED else -result
            game_data[i] = (state, policy, value)

        return game_data

    def train_step(self, batch_size=128):
        if len(self.replay_buffer) < batch_size:
            return 0.0

        batch = random.sample(self.replay_buffer, batch_size)

        states = torch.tensor(np.array([b[0] for b in batch]), dtype=torch.float32).to(self.device)
        target_pis = torch.tensor(np.array([b[1] for b in batch]), dtype=torch.float32).to(self.device)
        target_vs = torch.tensor(np.array([b[2] for b in batch]), dtype=torch.float32).unsqueeze(1).to(self.device)

        policy, value = self.net(states)

        policy_loss = -torch.sum(target_pis * torch.log(policy + 1e-8)) / batch_size
        value_loss = torch.nn.MSELoss()(value, target_vs)

        loss = policy_loss + value_loss

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def train(self, num_epochs=50, games_per_epoch=100):
        print("开始训练...")

        for epoch in range(num_epochs):
            print(f"\n=== Epoch {epoch+1}/{num_epochs} ===")

            # 自对弈
            print("自对弈中...")
            games = self.selfplay(games_per_epoch)
            self.replay_buffer.extend(games)
            print(f"收集了 {len(games)} 个局面")

            # 训练
            print("训练中...")
            loss = self.train_step(batch_size=256)
            print(f"Loss: {loss:.4f}")

            self.scheduler.step()

            # 保存
            if (epoch + 1) % 10 == 0:
                self.save_model(f"model_epoch_{epoch+1}.pth")
                print(f"已保存: model_epoch_{epoch+1}.pth")

        self.save_model("model_latest.pth")
        print("训练完成!")

    def save_model(self, filename):
        path = f"data/models/{filename}"
        torch.save({
            'network': self.net.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }, path)


if __name__ == "__main__":
    trainer = Trainer()
    # 运行训练
    print("开始训练...")
    sys.stdout.flush()
    trainer.train(num_epochs=100, games_per_epoch=10)
