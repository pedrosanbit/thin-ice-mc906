# src/agents/networks.py

import torch.nn as nn

class CnnQNet(nn.Module):
    def __init__(self, in_channels, n_actions):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
            nn.Flatten(),
            nn.Linear(64 * 15 * 19, 256), nn.ReLU(),
            nn.Linear(256, n_actions)
        )

    def forward(self, x):
        return self.net(x)
