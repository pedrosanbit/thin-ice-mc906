import torch
import torch.nn as nn

__all__ = ["DuelingCnnQNet"]  # evita imports acidentais


class DuelingCnnQNet(nn.Module):
    """
    CNN + cabeças Dueling (V, A).
    Espera entrada (B, C, 15, 19).    """

    def __init__(self, in_channels: int, n_actions: int):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
        )

        self.flatten = nn.Flatten()
        self.fc      = nn.Sequential(
            nn.Linear(64 * 15 * 19, 512), nn.ReLU(),
        )

        # heads
        self.V = nn.Linear(512, 1)
        self.A = nn.Linear(512, n_actions)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv(x)
        x = self.flatten(x)
        x = self.fc(x)
        v = self.V(x)                 # (B,1)
        a = self.A(x)                 # (B,n_actions)
        return v + (a - a.mean(dim=1, keepdim=True))