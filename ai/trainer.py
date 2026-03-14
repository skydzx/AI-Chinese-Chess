import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import numpy as np
import copy
import os


class Trainer:
    """AlphaZero训练器"""

    def __init__(self, network, data_dir="data"):
        self.network = network
        self.data_dir = data_dir

        self.optimizer = optim.Adam(network.parameters(), lr=0.001)
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=100
        )

        # 创建模型目录
        os.makedirs(data_dir + "/models", exist_ok=True)

        self.replay_buffer = deque(maxlen=100000)

    def train(self, num_epochs=100, selfplay_games_per_epoch=100):
        """训练主循环"""
        from ai.mcts import MCTS
        from backend.board import Board
        from backend.encoder import BoardEncoder
        from backend.move import Move

        for epoch in range(num_epochs):
            print(f"\n=== Epoch {epoch+1}/{num_epochs} ===")

            # 1. 自对弈收集数据
            print("Self-play...")
            games = self.selfplay(selfplay_games_per_epoch)

            # 2. 加入回放池
            for game in games:
                self.replay_buffer.extend(game)

            # 3. 训练网络
            print("Training...")
            loss = self.train_step(batch_size=128)

            print(f"Loss: {loss:.4f}")
            self.scheduler.step()

            # 4. 保存检查点
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(f"model_epoch_{epoch+1}.pth")

    def selfplay(self, num_games: int) -> list:
        """自对弈生成训练数据"""
        from ai.mcts import MCTS
        from backend.board import Board
        from backend.encoder import BoardEncoder
        from backend.move import Move

        games = []

        for _ in range(num_games):
            game_data = self.play_one_game(temperature=1.0)
            games.append(game_data)

        return games

    def play_one_game(self, temperature=1.0) -> list:
        """下一局自对弈"""
        from ai.mcts import MCTS
        from backend.board import Board
        from backend.encoder import BoardEncoder
        from backend.move import Move

        board = Board()
        mcts = MCTS(self.network)

        game_data = []  # [(state, policy, value), ...]
        history_boards = []

        while not board.is_game_over():
            # MCTS搜索
            policy, value = mcts.search(board)

            # 保存数据 (状态, 策略, 价值)
            encoder = BoardEncoder()
            state = encoder.encode(board, history_boards[-3:] if history_boards else None)
            game_data.append((state, policy, value))

            # 采样走法
            if temperature > 0.001:
                # 加温度采样
                p = policy ** (1/temperature)
                p /= p.sum()
                action = np.random.choice(len(p), p=p)
            else:
                action = np.argmax(policy)

            # 执行走法
            move = Move.from_index(action)
            board.make_move(move)

            # 更新历史
            history_boards.append(copy.deepcopy(board))

        # 计算最终回报
        result = board.get_result()  # 1:红胜, -1:黑胜, 0:和

        # 回溯赋值
        for i, (state, policy, _) in enumerate(game_data):
            # 最后一手之后的结果
            if i % 2 == 0:  # 红方
                game_data[i] = (state, policy, result)
            else:
                game_data[i] = (state, policy, -result)

        return game_data

    def train_step(self, batch_size=128) -> float:
        """单步训练"""
        if len(self.replay_buffer) < batch_size:
            return 0.0

        # 采样
        batch = random.sample(self.replay_buffer, batch_size)

        states = torch.tensor(np.array([b[0] for b in batch]), dtype=torch.float32)
        target_pis = torch.tensor(np.array([b[1] for b in batch]), dtype=torch.float32)
        target_vs = torch.tensor(np.array([b[2] for b in batch]), dtype=torch.float32).unsqueeze(1)

        # 检查是否有GPU
        device = next(self.network.parameters()).device
        states = states.to(device)
        target_pis = target_pis.to(device)
        target_vs = target_vs.to(device)

        # 前向
        policy, value = self.network(states)

        # 损失
        policy_loss = -torch.sum(target_pis * torch.log(policy + 1e-8)) / batch_size
        value_loss = nn.MSELoss()(value, target_vs)

        loss = policy_loss + value_loss

        # 反向
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def save_checkpoint(self, filename: str):
        """保存模型"""
        path = f"{self.data_dir}/models/{filename}"
        torch.save({
            'network': self.network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }, path)
        print(f"Saved: {path}")

    def load_checkpoint(self, filename: str):
        """加载模型"""
        path = f"{self.data_dir}/models/{filename}"
        checkpoint = torch.load(path, map_location='cpu')
        self.network.load_state_dict(checkpoint['network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        print(f"Loaded: {path}")
