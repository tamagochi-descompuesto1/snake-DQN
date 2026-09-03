import tkinter as tk

from collections import deque

from libs.theme import BG_SCREEN, FG_TERMINAL, FG_ACCENT, GRID_LINE, FONT_SMALL


class LineChart:
    """Generic live line chart on a plain tk.Canvas (delete-and-redraw each
    push, same pattern as a Game of Life grid tick -- a handful of points is
    cheap enough that no incremental-update trick is needed here)."""

    def __init__(
        self,
        master: tk.Misc,
        title: str,
        color: str = FG_TERMINAL,
        width: int = 240,
        height: int = 100,
        max_points: int = 100,
        allow_negative: bool = False,
    ) -> None:
        self.title = title
        self.color = color
        self.allow_negative = allow_negative
        self.history: deque[float] = deque(maxlen=max_points)

        self.canvas = tk.Canvas(master, width=width, height=height, bg=BG_SCREEN, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._draw()

    def push(self, value: float) -> None:
        self.history.append(value)
        self._draw()

    def _draw(self) -> None:
        self.canvas.delete("all")

        width = int(self.canvas["width"])
        height = int(self.canvas["height"])
        pad = 16

        last = f"  ({self.history[-1]:.3g})" if self.history else ""
        self.canvas.create_text(
            pad, 8, text=f"{self.title}{last}", fill=FG_ACCENT, font=FONT_SMALL, anchor="w"
        )

        if len(self.history) < 2:
            return

        lo = 0.0 if not self.allow_negative else min(self.history)
        hi = max(self.history)
        span = (hi - lo) or 1.0
        n = len(self.history)

        plot_w = width - pad * 2
        plot_h = height - pad * 2 - 10

        def coords(i: int, value: float) -> tuple[float, float]:
            x = pad + (i / (n - 1)) * plot_w
            y = pad + 14 + plot_h - ((value - lo) / span) * plot_h
            return x, y

        self.canvas.create_line(pad, height - pad, width - pad, height - pad, fill=GRID_LINE)

        points = []
        for i, value in enumerate(self.history):
            points.extend(coords(i, value))

        self.canvas.create_line(*points, fill=self.color, width=2)


class ScoreChart(LineChart):
    """Live line chart of score-per-game."""

    def __init__(self, master: tk.Misc, width: int = 240, height: int = 100, max_points: int = 100) -> None:
        super().__init__(master, title="SCORE", color=FG_TERMINAL, width=width, height=height, max_points=max_points)
