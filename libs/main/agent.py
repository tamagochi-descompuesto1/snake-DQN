import os
import json
import torch

import random as rd

from collections import deque
from libs.model import Linear_QNet
from libs.snake_game import SnakeGame
from libs.main.qtrainer import QTrainer

BATCH_SIZE = 1000
UPPER_LIMIT = 200
ACTIONS = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

class Agent:
    def __init__(
        self,
        gamma: float = 0.9,
        file_name: str | None = None,
        epsilon_start: int = 100,
    ) -> None:
        self.n_games: int = 0
        self.gamma: float = gamma
        self.epsilon_start: int = epsilon_start
        self.memory: deque[tuple[list[bool], list[int], int, list[bool], bool]] = deque(maxlen=100000)
        self.model: Linear_QNet = Linear_QNet()

        if file_name is not None and os.path.exists(file_name):
            self.model.load(file_name)
            self.n_games = self._load_n_games(file_name)

        self.epsilon: float = self.epsilon_start - self.n_games
        self.trainer: QTrainer = QTrainer(self.model, gamma=self.gamma)
        self.last_q_values: list[float] = [0.0, 0.0, 0.0]

    @staticmethod
    def _metadata_path(file_name: str) -> str:
        base, _ = os.path.splitext(file_name)
        return base + ".json"

    def _load_n_games(self, file_name: str) -> int:
        meta_path = self._metadata_path(file_name)
        if not os.path.exists(meta_path):
            return 0

        with open(meta_path, "r") as f:
            data = json.load(f)

        return data.get("n_games", 0)

    @staticmethod
    def get_state(game: SnakeGame) -> list[bool]:
        return game.get_state()

    def get_action(self, state: list[bool]) -> list[int]:
        state_t = torch.tensor(state, dtype=torch.float)

        with torch.no_grad():
            prediction = self.model(state_t)

        self.last_q_values = prediction.tolist()

        val = rd.randint(0, UPPER_LIMIT)
        if val < self.epsilon:
            return rd.choice(ACTIONS)

        move = int(torch.argmax(prediction).item())
        return ACTIONS[move]

    def remember(
        self, 
        state: list[bool], 
        action: list[int], 
        reward: int,
        next_state: list[bool], 
        done: bool
    ) -> None:
        self.memory.append((state, action, reward, next_state, done))

    def train_short_memory(
        self, 
        state: list[bool], 
        action: list[int], 
        reward: int,
        next_state: list[bool], 
        done: bool
    ) -> float:
        return self.trainer.train_step(state, action, reward, next_state, done)

    def train_long_memory(self) -> float:
        if len(self.memory) > BATCH_SIZE:
            batch = rd.sample(list(self.memory), BATCH_SIZE)
        else:
            batch = list(self.memory)

        states, actions, rewards, next_states, dones = zip(*batch)
        loss = self.trainer.train_step(
            list(states),
            list(actions),
            list(rewards),
            list(next_states),
            list(dones)
        )

        self.n_games += 1
        self.epsilon = self.epsilon_start - self.n_games

        return loss

    def save_n_games(self, file_name: str) -> None:
        meta_path = self._metadata_path(file_name)

        with open(meta_path, "w") as f:
            json.dump({"n_games": self.n_games}, f)

    def save(self, file_name: str) -> None:
        self.model.save(file_name)
        self.save_n_games(file_name)