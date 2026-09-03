import os
import time
import tkinter as tk

from typing import Callable

from libs.theme import (
    BG_CHROME, BG_SCREEN, FG_TERMINAL, FG_ACCENT, YELLOW, AQUA, FUCHSIA,
    FONT_SMALL, retro_frame, screen_frame, retro_button, terminal_label, title_label,
)
from libs.gui.score_chart import ScoreChart, LineChart
from libs.gui.bar_chart import QValueBars
from libs.gui.face_sprite import FaceSprite
from libs.gui.train_config import TrainConfig
from libs.main import Agent, Orchestrator
from libs.render import GameRenderer
from libs.snake_game import SnakeGame, WIDTH, HEIGHT, BLOCK_SIZE, REWARD_FOOD

# Order must match SnakeGame.get_state()'s documented layout
STATE_LABELS = [
    "Danger ahead",
    "Danger left",
    "Danger right",
    "Danger ahead x2",
    "Danger left x2",
    "Danger right x2",
    "Dir: left",
    "Dir: right",
    "Dir: up",
    "Dir: down",
    "Food: left",
    "Food: right",
    "Food: up",
    "Food: down",
]

ACTION_INDEX = {
    (1, 0, 0): 0,
    (0, 1, 0): 1,
    (0, 0, 1): 2,
}

STATE_WIDTH = 260
STEP_WIDTH = 300
GEN_WIDTH = 300
CHROME_BUDGET_H = 260  # title + stats bar + buttons + padding, roughly

HAPPY_HOLD_SECONDS = 0.4
DEAD_HOLD_SECONDS = 1.0


class TrainFrame(tk.Frame):
    """Hosts a live Orchestrator-driven training/visualization session."""

    def __init__(self, master: tk.Misc, config: TrainConfig, on_menu: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_CHROME)
        self.config = config

        os.makedirs(os.path.dirname(config.checkpoint_path) or ".", exist_ok=True)

        checkpoint_path = config.checkpoint_path if config.load_checkpoint else None

        self.game = SnakeGame(reward_shaping=config.reward_shaping)
        self.agent = Agent(
            gamma=config.gamma,
            file_name=checkpoint_path,
            epsilon_start=config.epsilon_start,
        )

        title_label(self, text="SNAKE // DQN -- TRAINING", font=("Courier New", 16, "bold")).pack(pady=(6, 4))

        stats_bar = screen_frame(self)
        stats_bar.pack(fill="x", padx=10)
        self.stats_label = terminal_label(stats_bar, text="Gen: 0   Score: 0   Record: 0   Mean: 0.00   Reward: 0")
        self.stats_label.pack(fill="x", padx=10, pady=4)

        body = tk.Frame(self, bg=BG_CHROME)
        body.pack(padx=10, pady=8, fill="both", expand=True)

        # -- Left: board --------------------------------------------------
        board_column = tk.Frame(body, bg=BG_CHROME)
        board_column.pack(side="left", fill="y")

        board_holder = screen_frame(board_column)
        board_holder.pack()
        cell_px = self._fit_cell_px()
        self.renderer = GameRenderer(board_holder, cell_px=cell_px)
        self._face_until = 0.0

        # -- Right: 3 panels on top, sprite panel spanning the full width below
        right_area = tk.Frame(body, bg=BG_CHROME)
        right_area.pack(side="left", fill="both", expand=True, padx=(10, 0))

        top_row = tk.Frame(right_area, bg=BG_CHROME)
        top_row.pack(fill="x")

        # -- state vector -----------------------------------------
        state_col = retro_frame(top_row, width=STATE_WIDTH)
        state_col.pack(side="left", fill="y")

        state_holder = screen_frame(state_col)
        state_holder.pack(fill="both", expand=True, padx=8, pady=8)
        terminal_label(state_holder, text="-- STATE --", fg=FG_ACCENT, font=FONT_SMALL).pack(anchor="w", padx=6, pady=(4, 2))

        self.state_labels: list[tk.Label] = []
        for name in STATE_LABELS:
            lbl = terminal_label(state_holder, text=f"{name}: -", font=FONT_SMALL)
            lbl.pack(anchor="w", padx=6)
            self.state_labels.append(lbl)

        # -- per-step charts ----------------------------------------
        step_col = retro_frame(top_row, width=STEP_WIDTH)
        step_col.pack(side="left", fill="y", padx=(10, 0))

        terminal_col_header = tk.Label(step_col, text="PER STEP", bg=BG_CHROME, fg=FG_ACCENT, font=FONT_SMALL)
        terminal_col_header.pack(pady=(4, 0))

        qvalues_holder = screen_frame(step_col)
        qvalues_holder.pack(fill="x", padx=8, pady=(4, 4))
        self.q_bars = QValueBars(qvalues_holder, width=STEP_WIDTH - 24, height=110)

        loss_holder = screen_frame(step_col)
        loss_holder.pack(fill="x", padx=8, pady=4)
        self.loss_chart = LineChart(
            loss_holder, title="LOSS", color=AQUA,
            width=STEP_WIDTH - 24, height=70, max_points=200,
        )

        reward_holder = screen_frame(step_col)
        reward_holder.pack(fill="x", padx=8, pady=4)
        self.reward_chart = LineChart(
            reward_holder, title="REWARD", color=FUCHSIA,
            width=STEP_WIDTH - 24, height=70, max_points=200, allow_negative=True,
        )

        survival_holder = screen_frame(step_col)
        survival_holder.pack(fill="x", padx=8, pady=(4, 8))
        self.survival_chart = LineChart(
            survival_holder, title="STEPS THIS GAME", color="#00BFFF",
            width=STEP_WIDTH - 24, height=70, max_points=300,
        )

        # -- per-generation charts -----------------------------------
        gen_col = retro_frame(top_row, width=GEN_WIDTH)
        gen_col.pack(side="left", fill="y", padx=(10, 0))

        tk.Label(gen_col, text="PER GENERATION", bg=BG_CHROME, fg=FG_ACCENT, font=FONT_SMALL).pack(pady=(4, 0))

        chart_holder = screen_frame(gen_col)
        chart_holder.pack(fill="x", padx=8, pady=(4, 4))
        self.score_chart = ScoreChart(chart_holder, width=GEN_WIDTH - 24, height=80)

        epsilon_holder = screen_frame(gen_col)
        epsilon_holder.pack(fill="x", padx=8, pady=4)
        self.epsilon_chart = LineChart(
            epsilon_holder, title="EPSILON", color=YELLOW,
            width=GEN_WIDTH - 24, height=70,
        )

        mean_holder = screen_frame(gen_col)
        mean_holder.pack(fill="x", padx=8, pady=(4, 8))
        self.mean_chart = LineChart(
            mean_holder, title="MEAN SCORE", color=FG_TERMINAL,
            width=GEN_WIDTH - 24, height=70,
        )

        # -- Sprite panel: spans the full width of the 3 panels above ------
        sprite_panel = retro_frame(right_area)
        sprite_panel.pack(fill="both", expand=True, pady=(10, 0))
        tk.Label(sprite_panel, text="AGENT STATUS", bg=BG_CHROME, fg=FG_ACCENT, font=FONT_SMALL).pack(pady=(8, 0))

        face_holder = screen_frame(sprite_panel)
        face_holder.pack(fill="both", expand=True, padx=8, pady=8)
        self.face = FaceSprite(face_holder)
        face_holder.bind("<Configure>", self._on_face_holder_resize)

        button_row = tk.Frame(self, bg=BG_CHROME)
        button_row.pack(pady=8)
        self.pause_button = retro_button(button_row, "⏸ PAUSE", self.toggle_pause)
        self.pause_button.pack(side="left", padx=6)
        retro_button(button_row, "◀ MENU", on_menu).pack(side="left", padx=6)

        self.orchestrator = Orchestrator(
            self.game,
            self.agent,
            on_step_callback=self._on_step_complete,
            check_point_path=config.checkpoint_path,
        )

        self._last_n_games = self.agent.n_games
        self.renderer.draw_initial({"snake": self.game.snake, "food": self.game.food})
        self._after_id: str | None = None
        self._tick()

    def _fit_cell_px(self) -> float:
        """Size the board's cells to fill the available screen space."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        cols = WIDTH // BLOCK_SIZE
        rows = HEIGHT // BLOCK_SIZE

        width_budget = screen_w - STATE_WIDTH - STEP_WIDTH - GEN_WIDTH - 100
        height_budget = screen_h - CHROME_BUDGET_H

        cell_px = min(width_budget / cols, height_budget / rows)
        return max(8, min(24, cell_px))

    def _on_face_holder_resize(self, event: tk.Event) -> None:
        self.face.resize(max(50, event.width - 16), max(50, event.height - 16))

    def toggle_pause(self) -> None:
        self.orchestrator.toggle_pause()
        self.pause_button.config(text="▶ RESUME" if self.orchestrator.paused else "⏸ PAUSE")

    def _update_face(self, info: dict) -> None:
        now = time.monotonic()

        if info["game_over"]:
            self.face.set_expression("dead")
            self._face_until = now + DEAD_HOLD_SECONDS
        elif info["reward"] == REWARD_FOOD:
            self.face.set_expression("happy")
            self._face_until = now + HAPPY_HOLD_SECONDS
        elif now >= self._face_until:
            self.face.set_expression("normal")

    def _on_step_complete(self, info: dict) -> None:
        self.renderer.redraw(info)
        self._update_face(info)

        self.stats_label.config(
            text=(
                f"Gen: {info['n_games']}   "
                f"Score: {info['score']}   "
                f"Record: {info['record']}   "
                f"Mean: {info['mean_score']:.2f}   "
                f"Reward: {info['reward']}   "
                f"Epsilon: {info['epsilon']:.0f}"
            )
        )

        for lbl, name, value in zip(self.state_labels, STATE_LABELS, info["state"]):
            lbl.config(text=f"{name}: {value}")

        chosen = ACTION_INDEX.get(tuple(info.get("action", [1, 0, 0])), 0)
        self.q_bars.update(info["q_values"], chosen=chosen)

        self.loss_chart.push(info["loss"])
        self.reward_chart.push(info["reward"])
        self.survival_chart.push(info["steps_this_game"])

        if info["n_games"] != self._last_n_games:
            self._last_n_games = info["n_games"]
            self.score_chart.push(info["score"])
            self.epsilon_chart.push(info["epsilon"])
            self.mean_chart.push(info["mean_score"])

    def _tick(self) -> None:
        self.orchestrator.step()
        self._after_id = self.after(self.config.render_speed, self._tick)

    def destroy(self) -> None:
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        super().destroy()
