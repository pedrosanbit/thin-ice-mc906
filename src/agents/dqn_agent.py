# src/agents/dqn_agent.py

import random
import numpy as np
from collections import deque

import torch
import torch.nn as nn
import torch.optim as optim
from src.agents.networks import CnnQNet


class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def add(self, s, a, r, s_next, done):
        self.buffer.append((s, a, r, s_next, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        s, a, r, s_next, d = map(np.array, zip(*batch))
        return (
            torch.tensor(s, dtype=torch.float32),
            torch.tensor(a, dtype=torch.int64),
            torch.tensor(r, dtype=torch.float32),
            torch.tensor(s_next, dtype=torch.float32),
            torch.tensor(d, dtype=torch.float32)
        )

    def __len__(self):
        return len(self.buffer)


class DQNAgent:
    def __init__(
        self,
        state_shape,
        n_actions,
        device="cuda" if torch.cuda.is_available() else "cpu",
        buffer_size=500_000,
        gamma=0.99,
        lr=1e-4,
        batch_size=128,
        update_target_every=5000,
        epsilon_start=1.0,
        epsilon_end=0.05,
        epsilon_decay=50_000,
        double_dqn=True
    ):
        self.device = device
        self.n_actions = n_actions
        self.gamma = gamma
        self.batch_size = batch_size
        self.update_target_every = update_target_every
        self.double_dqn = double_dqn

        self.policy_net = CnnQNet(state_shape[0], n_actions).to(device)
        self.target_net = CnnQNet(state_shape[0], n_actions).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=5000, gamma=0.9)
        self.loss_fn = nn.SmoothL1Loss()

        self.buffer = ReplayBuffer(buffer_size)

        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.step_count = 0

    def act(self, state, action_mask=None):
        self.step_count += 1
        eps_threshold = self.epsilon_min + (self.epsilon - self.epsilon_min) * \
                        np.exp(-1. * self.step_count / self.epsilon_decay)

        if action_mask is None:
            action_mask = np.ones(self.n_actions, dtype=bool)

        valid_actions = np.where(action_mask)[0]
        if len(valid_actions) == 0:
            return random.randint(0, self.n_actions - 1)

        if random.random() < eps_threshold:
            return np.random.choice(valid_actions)

        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.policy_net(state_tensor)[0].cpu().numpy()

        q_values[~action_mask] = -np.inf
        return int(np.argmax(q_values))

    def remember(self, s, a, r, s_next, done):
        self.buffer.add(s, a, r, s_next, done)

    def update(self):
        if len(self.buffer) < self.batch_size:
            return

        s, a, r, s_next, d = self.buffer.sample(self.batch_size)

        s = s.to(self.device)
        s_next = s_next.to(self.device)
        a = a.to(self.device)
        r = r.to(self.device)
        d = d.to(self.device)

        q_values = self.policy_net(s).gather(1, a.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            if self.double_dqn:
                a_max = self.policy_net(s_next).argmax(dim=1, keepdim=True)
                q_target_next = self.target_net(s_next).gather(1, a_max).squeeze(1)
            else:
                q_target_next = self.target_net(s_next).max(1)[0]

            q_target = r + self.gamma * q_target_next * (1 - d)

        loss = self.loss_fn(q_values, q_target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.scheduler.step()

        if self.step_count % self.update_target_every == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

    def save(self, path):
        torch.save(self.policy_net.state_dict(), path)

    def load(self, path):
        self.policy_net.load_state_dict(torch.load(path, map_location=self.device))
        self.target_net.load_state_dict(self.policy_net.state_dict())

