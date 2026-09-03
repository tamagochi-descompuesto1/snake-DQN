import json
import os

from typing import Callable

from libs.main.agent import Agent
from libs.snake_game import SnakeGame

class Orchestrator:
    def __init__(
        self,
        game: SnakeGame,
        agent: Agent,
        on_step_callback: Callable[[dict], None],
        check_point_path: str | None = None,
    ) -> None:
        self.game = game
        self.agent = agent
        self.on_step_callback = on_step_callback
        self.check_point_path = check_point_path
        self.record = 0
        self.total_score = 0
        self.paused = False

        self._load_stats()

        self._last_info: dict = {
            "snake": self.game.snake,
            "food": self.game.food,
            "score": 0,
            "reward": 0,
            "game_over": False,
            "record": self.record,
            "n_games": self.agent.n_games,
            "mean_score": self._mean_score(),
            "state": self.agent.get_state(self.game),
            "epsilon": self.agent.epsilon,
            "loss": 0.0,
            "q_values": self.agent.last_q_values,
            "steps_this_game": self.game.frame_iteration,
            "action": [1, 0, 0],
        }

    def step(self) -> dict:
        if self.paused:
            self.on_step_callback(self._last_info)
            return self._last_info

        state = self.agent.get_state(self.game)
        action = self.agent.get_action(state)
        reward, game_over, score = self.game.play_step(action)

        state_new = self.agent.get_state(self.game)
        loss = self.agent.train_short_memory(state, action, reward, state_new, game_over)
        self.agent.remember(state, action, reward, state_new, game_over)
        steps_this_game = self.game.frame_iteration

        if game_over:
            self.agent.train_long_memory()
            self._save_checkpoint_if_record(score)
            self.total_score += score
            self._save_stats()
            self.game.reset()

        info = {
            "snake": self.game.snake,
            "food": self.game.food,
            "score": score,
            "reward": reward,
            "game_over": game_over,
            "record": self.record,
            "n_games": self.agent.n_games,
            "mean_score": self._mean_score(),
            "state": state_new,
            "epsilon": self.agent.epsilon,
            "loss": loss,
            "q_values": self.agent.last_q_values,
            "steps_this_game": steps_this_game,
            "action": action,
        }
        self._last_info = info
        self.on_step_callback(info)
        return info

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def _mean_score(self) -> float:
        if self.agent.n_games == 0:
            return 0.0
        return self.total_score / self.agent.n_games

    def _save_checkpoint_if_record(self, score: int) -> None:
        if score > self.record:
            self.record = score
            if self.check_point_path is not None:
                self.agent.save(self.check_point_path)

    @staticmethod
    def _stats_path(check_point_path: str) -> str:
        base, _ = os.path.splitext(check_point_path)
        return base + "_stats.json"

    def _load_stats(self) -> None:
        if self.check_point_path is None or not os.path.exists(self.check_point_path):
            return

        stats_file = self._stats_path(self.check_point_path)
        if not os.path.exists(stats_file):
            return

        with open(stats_file, "r") as f:
            data = json.load(f)

        self.total_score = data.get("total_score", 0)
        self.record = data.get("record", 0)

    def _save_stats(self) -> None:
        if self.check_point_path is None:
            return

        stats_file = self._stats_path(self.check_point_path)
        with open(stats_file, "w") as f:
            json.dump({"total_score": self.total_score, "record": self.record}, f)
