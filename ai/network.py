import torch
import torch.nn as nn
import torch.nn.functional as F


class ChineseChessNet(nn.Module):
    """中国象棋神经网络 - AlphaZero风格"""

    def __init__(self, num_channels=128, num_res_blocks=8):
        super().__init__()

        # 输入: [batch, 56, 10, 9] (14通道 x 4步历史)
        self.conv_input = nn.Conv2d(56, num_channels, kernel_size=3, padding=1)
        self.bn_input = nn.BatchNorm2d(num_channels)

        # 残差块
        self.res_blocks = nn.ModuleList([
            ResidualBlock(num_channels) for _ in range(num_res_blocks)
        ])

        # 策略头
        self.policy_conv = nn.Conv2d(num_channels, 32, kernel_size=1)
        self.policy_bn = nn.BatchNorm2d(32)
        self.policy_fc = nn.Linear(32 * 10 * 9, 2098)  # 2098种走法

        # 价值头
        self.value_conv = nn.Conv2d(num_channels, 1, kernel_size=1)
        self.value_bn = nn.BatchNorm2d(1)
        self.value_fc1 = nn.Linear(10 * 9, 64)
        self.value_fc2 = nn.Linear(64, 1)

    def forward(self, x):
        # 输入层
        x = F.relu(self.bn_input(self.conv_input(x)))

        # 残差块
        for block in self.res_blocks:
            x = block(x)

        # 策略头
        p = F.relu(self.policy_bn(self.policy_conv(x)))
        p = p.view(p.size(0), -1)
        p = F.softmax(self.policy_fc(p), dim=1)

        # 价值头
        v = F.relu(self.value_bn(self.value_conv(x)))
        v = v.view(v.size(0), -1)
        v = F.tanh(self.value_fc2(F.relu(self.value_fc1(v))))

        return p, v


class ResidualBlock(nn.Module):
    """残差块"""

    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x = F.relu(x + residual)
        return x
