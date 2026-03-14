#!/usr/bin/env python3
"""训练脚本 - 使用自对弈强化学习训练AI"""

import os
import sys
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

    def play_one_game(self, temperature=1.0):
        """下一局自对弈"""
        board = Board()
        mcts = MCTS(self.net, num_simulations=100)

        game_data = []
        history = []

        while not board.is_game_over():
            # MCTS搜索
            policy, _ = mcts.search(board)

            # 记录状态
            encoder = BoardEncoder()
            state = encoder.encode(board, history[-3:] if history else None)
            game_data.append((state, policy.copy()))

            # 采样走法
            if temperature > 0.001:
                p = policy ** (1/temperature)
                p /= p.sum()
                action = np.random.choice(len(p), p=p)
            else:
                action = policy.argmax()

            move = Move.from_index(action)
            board.make_move(move)
            history.append(copy.deepcopy(board))

        # 计算结果
        result = board.get_result()

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
    # 快速测试
    print("测试自对弈...")
    games = trainer.selfplay(2)
    print(f"生成了 {len(games)} 个训练数据")
