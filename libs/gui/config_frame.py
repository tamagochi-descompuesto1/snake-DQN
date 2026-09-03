import os
import tkinter as tk

from typing import Callable

from libs.theme import (
    BG_CHROME, FG_TEXT, FG_ACCENT, FONT_SMALL,
    retro_frame, retro_button, retro_label, title_label,
)
from libs.gui.train_config import TrainConfig

DEFAULT_CHECKPOINT = "model/model.pth"


class ConfigFrame(tk.Frame):
    """Pre-training settings screen: gamma, starting epsilon, whether to
    load an existing checkpoint, and render speed."""

    def __init__(
        self,
        master: tk.Misc,
        on_start: Callable[[TrainConfig], None],
        on_info: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master, bg=BG_CHROME)
        self.on_start = on_start
        self.on_info = on_info

        self.gamma_var = tk.StringVar(value="0.9")
        self.epsilon_var = tk.StringVar(value="100")
        self.speed_var = tk.StringVar(value="50")
        self.reward_shaping_var = tk.BooleanVar(value=True)
        self.load_checkpoint_var = tk.BooleanVar(
            value=os.path.exists(DEFAULT_CHECKPOINT)
        )

        title_label(self, text="SNAKE // DQN").pack(pady=(24, 4))
        retro_label(
            self, text="-- training configuration --", fg=FG_ACCENT, font=FONT_SMALL
        ).pack(pady=(0, 20))

        panel = retro_frame(self)
        panel.pack(padx=40, pady=10)

        self._add_field(panel, "Gamma (discount):", self.gamma_var, row=0)
        self._add_field(panel, "Starting epsilon:", self.epsilon_var, row=1)
        self._add_field(panel, "Speed (ms/tick):", self.speed_var, row=2)

        checkbox_row = tk.Frame(panel, bg=BG_CHROME)
        checkbox_row.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=6)
        tk.Checkbutton(
            checkbox_row, text="Load existing checkpoint", variable=self.load_checkpoint_var,
            bg=BG_CHROME, fg=FG_TEXT, activebackground=BG_CHROME, selectcolor=BG_CHROME,
            font=FONT_SMALL,
        ).pack(anchor="w")
        tk.Checkbutton(
            checkbox_row, text="Reward shaping (closer/farther from food)",
            variable=self.reward_shaping_var,
            bg=BG_CHROME, fg=FG_TEXT, activebackground=BG_CHROME, selectcolor=BG_CHROME,
            font=FONT_SMALL,
        ).pack(anchor="w")

        button_row = tk.Frame(self, bg=BG_CHROME)
        button_row.pack(pady=24)
        retro_button(button_row, "▶ TRAIN", self._start).pack(side="left", padx=6)
        if self.on_info is not None:
            retro_button(button_row, "? INFO", self.on_info).pack(side="left", padx=6)

    def _add_field(self, panel: tk.Frame, label: str, var: tk.StringVar, row: int) -> None:
        retro_label(panel, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        entry = tk.Entry(panel, textvariable=var, width=10, font=FONT_SMALL, relief="sunken", bd=2)
        entry.grid(row=row, column=1, sticky="w", padx=10, pady=6)

    def _start(self) -> None:
        config = TrainConfig(
            gamma=self._safe_float(self.gamma_var.get(), 0.9),
            epsilon_start=self._safe_int(self.epsilon_var.get(), 100),
            load_checkpoint=self.load_checkpoint_var.get(),
            render_speed=self._safe_int(self.speed_var.get(), 50),
            reward_shaping=self.reward_shaping_var.get(),
            checkpoint_path=DEFAULT_CHECKPOINT,
        )
        self.on_start(config)

    @staticmethod
    def _safe_float(value: str, default: float) -> float:
        try:
            return float(value)
        except ValueError:
            return default

    @staticmethod
    def _safe_int(value: str, default: int) -> int:
        try:
            return int(value)
        except ValueError:
            return default
