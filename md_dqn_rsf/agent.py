"""DQN and MD-DQN-RSF agent implementations."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import copy
import random

import numpy as np
import torch
from torch import nn


class QNetwork(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128), nn.ReLU(),
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@dataclass(frozen=True)
class AgentConfig:
    gamma: float = 0.97
    lr: float = 3e-4
    batch_size: int = 128
    buffer_size: int = 100_000
    target_interval: int = 250
    epsilon_start: float = 1.0
    epsilon_end: float = 0.05
    epsilon_decay_steps: int = 18_000
    use_reset: bool = False
    use_selective: bool = False
    use_flush: bool = False
    reset_fraction: float = 0.45
    flush_fraction: float = 0.72
    reset_epsilon: float = 0.65
    selective_factor: float = 1.8
    steps_per_episode: int = 64


class ReplayBuffer:
    def __init__(self, capacity: int):
        self.data = deque(maxlen=capacity)

    def add(self, transition):
        self.data.append(transition)

    def clear(self):
        self.data.clear()

    def sample(self, size: int, rng: random.Random):
        batch = rng.sample(self.data, size)
        return map(np.asarray, zip(*batch))

    def __len__(self):
        return len(self.data)


class DQNAgent:
    def __init__(self, state_dim: int, action_dim: int, config: AgentConfig,
                 device: torch.device, seed: int, total_episodes: int):
        self.config = config
        self.device = device
        self.action_dim = action_dim
        self.rng = random.Random(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        self.online = QNetwork(state_dim, action_dim).to(device)
        self.target = copy.deepcopy(self.online).to(device).eval()
        self.optimizer = torch.optim.Adam(self.online.parameters(), lr=config.lr)
        self.buffer = ReplayBuffer(config.buffer_size)
        self.steps = 0
        self.epsilon = config.epsilon_start
        self.reset_episode = int(total_episodes * config.reset_fraction)
        self.flush_episode = int(total_episodes * config.flush_fraction)
        self.did_reset = False
        self.did_flush = False
        self.loss_ema: float | None = None
        self.skipped_updates = 0

    def act(self, state: np.ndarray, explore: bool = True) -> int:
        if explore and self.rng.random() < self.epsilon:
            return self.rng.randrange(self.action_dim)
        with torch.no_grad():
            x = torch.as_tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
            return int(self.online(x).argmax(dim=1).item())

    def schedule_episode_events(self, episode: int):
        if self.config.use_reset and not self.did_reset and episode >= self.reset_episode:
            self.epsilon = self.config.reset_epsilon
            self.did_reset = True
        if self.config.use_flush and not self.did_flush and episode >= self.flush_episode:
            self.buffer.clear()
            self.did_flush = True

    def decay_epsilon(self):
        fraction = min(1.0, self.steps / self.config.epsilon_decay_steps)
        scheduled = self.config.epsilon_start + fraction * (
            self.config.epsilon_end - self.config.epsilon_start
        )
        if self.did_reset:
            post_steps = max(
                0, self.steps - int(self.reset_episode * self.config.steps_per_episode)
            )
            post_fraction = min(1.0, post_steps / max(1, self.config.epsilon_decay_steps // 2))
            scheduled = self.config.reset_epsilon + post_fraction * (
                self.config.epsilon_end - self.config.reset_epsilon
            )
        self.epsilon = max(self.config.epsilon_end, scheduled)

    def observe(self, state, action, reward, next_state, done):
        self.buffer.add((state, action, reward, next_state, float(done)))
        self.steps += 1
        self.decay_epsilon()

    def update(self) -> float | None:
        if len(self.buffer) < self.config.batch_size:
            return None
        states, actions, rewards, next_states, dones = self.buffer.sample(
            self.config.batch_size, self.rng
        )
        states = torch.as_tensor(states, dtype=torch.float32, device=self.device)
        actions = torch.as_tensor(actions, dtype=torch.int64, device=self.device)
        rewards = torch.as_tensor(rewards, dtype=torch.float32, device=self.device)
        next_states = torch.as_tensor(next_states, dtype=torch.float32, device=self.device)
        dones = torch.as_tensor(dones, dtype=torch.float32, device=self.device)

        q = self.online(states).gather(1, actions[:, None]).squeeze(1)
        with torch.no_grad():
            target = rewards + self.config.gamma * (1 - dones) * self.target(next_states).max(1).values
        loss = nn.functional.smooth_l1_loss(q, target)
        loss_value = float(loss.item())
        if self.loss_ema is None:
            self.loss_ema = loss_value
        threshold = self.config.selective_factor * max(self.loss_ema, 1e-5)
        should_update = not (
            self.config.use_selective and self.did_reset and loss_value > threshold
        )
        if should_update:
            self.optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(self.online.parameters(), 10.0)
            self.optimizer.step()
            self.loss_ema = 0.98 * self.loss_ema + 0.02 * loss_value
        else:
            self.skipped_updates += 1
        if self.steps % self.config.target_interval == 0:
            self.target.load_state_dict(self.online.state_dict())
        return loss_value
