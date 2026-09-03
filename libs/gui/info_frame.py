import tkinter as tk

from typing import Callable

from libs.theme import BG_CHROME, BG_SCREEN, FG_TERMINAL, FONT_SMALL, retro_frame, retro_button, title_label

INFO_TEXT = """\
DQN (Deep Q-Network)

The snake is controlled by a neural network that learns to
play through trial and error, with nobody telling it the rules.

STATE: at every moment, the network receives 14 values that
describe what the snake "sees" -- nearby danger in 3
directions (at 1 and 2 cells out), which way it's heading, and
which direction the food is in.

ACTION: the network picks one of 3 things -- go straight, turn
right, or turn left (always relative to where it's already
heading, not absolute directions).

REWARD: +10 for eating, -10 for dying, plus a small bonus for
getting closer to the food each step (reward shaping).

EPSILON (exploration): early on, the snake moves a lot at
random -- it "explores" to find out what works. With every
game played, epsilon goes down, and the snake trusts more in
what the network already learned ("exploits" its knowledge).

Over time, the average score should go up -- that's the
evidence that the network is really learning.
"""


class InfoFrame(tk.Frame):
    def __init__(self, master: tk.Misc, on_back: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_CHROME)

        title_label(self, text="HOW IT WORKS").pack(pady=(20, 10))

        panel = retro_frame(self)
        panel.pack(padx=30, pady=10, fill="both", expand=True)

        text_widget = tk.Text(
            panel,
            bg=BG_SCREEN,
            fg=FG_TERMINAL,
            font=FONT_SMALL,
            relief="sunken",
            bd=3,
            wrap="word",
            width=60,
            height=22,
        )
        text_widget.insert("1.0", INFO_TEXT)
        text_widget.config(state="disabled")
        text_widget.pack(padx=10, pady=10, fill="both", expand=True)

        retro_button(self, "◀ MENU", on_back).pack(pady=16)
