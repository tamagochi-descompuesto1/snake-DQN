import tkinter as tk

from libs.theme import BG_SCREEN, FG_ACCENT, FG_TERMINAL, GRID_LINE, FONT_SMALL, YELLOW

Q_LABELS = ["STRAIGHT", "RIGHT", "LEFT"]
Q_COLORS = [FG_TERMINAL, YELLOW, "#00BFFF"]


class QValueBars:
    """Live bar chart of the network's raw Q-value prediction for the 3
    possible actions -- the chosen action's bar is outlined to show what
    the agent is about to do (and why)."""

    def __init__(self, master: tk.Misc, width: int = 240, height: int = 110) -> None:
        self.canvas = tk.Canvas(master, width=width, height=height, bg=BG_SCREEN, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.update([0.0, 0.0, 0.0], chosen=0)

    def update(self, q_values: list[float], chosen: int) -> None:
        self.canvas.delete("all")

        width = int(self.canvas["width"])
        height = int(self.canvas["height"])
        pad = 16
        top = 24

        self.canvas.create_text(pad, 8, text="Q-VALUES", fill=FG_ACCENT, font=FONT_SMALL, anchor="w")

        lo = min(0.0, min(q_values))
        hi = max(0.0, max(q_values))
        span = (hi - lo) or 1.0

        zero_y = top + (hi - 0) / span * (height - top - pad)

        n = len(q_values)
        slot_w = (width - pad * 2) / n
        bar_w = slot_w * 0.5

        for i, value in enumerate(q_values):
            cx = pad + slot_w * i + slot_w / 2
            value_y = top + (hi - value) / span * (height - top - pad)

            y0, y1 = sorted((zero_y, value_y))
            outline = "white" if i == chosen else ""
            self.canvas.create_rectangle(
                cx - bar_w / 2, y0, cx + bar_w / 2, y1,
                fill=Q_COLORS[i % len(Q_COLORS)], outline=outline, width=2,
            )
            self.canvas.create_text(
                cx, height - 4, text=Q_LABELS[i], fill=FG_TERMINAL, font=FONT_SMALL, anchor="s"
            )

        self.canvas.create_line(pad, zero_y, width - pad, zero_y, fill=GRID_LINE)
