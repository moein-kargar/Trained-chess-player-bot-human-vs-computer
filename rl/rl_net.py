# rl/rl_net.py
import torch
import torch.nn as nn
import torch.nn.functional as F

from .rl_utils import ACTION_SIZE


class ChessNet(nn.Module):
    def __init__(self, in_channels=13):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, 64, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)

        self.res_layers = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(64, 64, 3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.Conv2d(64, 64, 3, padding=1),
                nn.BatchNorm2d(64),
            )
            for _ in range(3)
        ])

        self.policy_head = nn.Sequential(
            nn.Conv2d(64, 32, 1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(32 * 8 * 8, ACTION_SIZE),
        )

        self.value_head = nn.Sequential(
            nn.Conv2d(64, 8, 1),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(8 * 8 * 8, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Tanh(),
        )

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        for r in self.res_layers:
            y = r(x)
            x = F.relu(x + y)
        return self.policy_head(x), self.value_head(x).squeeze(-1)
