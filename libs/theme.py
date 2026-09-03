"""Retro visual theme: classic 16-color palette, chunky pixel-ish fonts and
beveled Windows-3.1/old-Paint-style widget factories, all built on plain
tkinter (its default relief/bevel look already IS the retro aesthetic --
no need to fight it with a modern widget toolkit)."""

import tkinter as tk
from typing import Callable

# Classic 16-color VGA/Paint palette
BLACK   = "#000000"
WHITE   = "#FFFFFF"
GRAY    = "#808080"
SILVER  = "#C0C0C0"
RED     = "#FF0000"
MAROON  = "#800000"
YELLOW  = "#FFFF00"
OLIVE   = "#808000"
LIME    = "#00FF00"
GREEN   = "#008000"
AQUA    = "#00FFFF"
TEAL    = "#008080"
BLUE    = "#0000FF"
NAVY    = "#000080"
FUCHSIA = "#FF00FF"
PURPLE  = "#800080"

# Semantic roles
BG_CHROME = SILVER      # window/frame chrome, like old Windows dialogs
BG_SCREEN = BLACK       # game board / "monitor" background
FG_TEXT = BLACK         # text over chrome
FG_TERMINAL = LIME      # text over screen (matrix-green terminal look)
FG_ACCENT = FUCHSIA
FG_WARN = YELLOW
SNAKE_COLOR = LIME
FOOD_COLOR = RED
GRID_LINE = "#003300"   # subtle dark green grid over the black board

FONT_FAMILY = "Courier New"
FONT_TITLE = (FONT_FAMILY, 22, "bold")
FONT_HEADING = (FONT_FAMILY, 14, "bold")
FONT_BODY = (FONT_FAMILY, 11, "bold")
FONT_SMALL = (FONT_FAMILY, 9, "bold")
FONT_TERMINAL = (FONT_FAMILY, 12, "bold")

BORDER_WIDTH = 4


def retro_frame(master: tk.Misc, **kwargs) -> tk.Frame:
    """A chunky, beveled 'chrome' frame in the style of old Windows dialogs."""
    options = dict(bg=BG_CHROME, relief="raised", bd=BORDER_WIDTH)
    options.update(kwargs)
    return tk.Frame(master, **options)


def screen_frame(master: tk.Misc, **kwargs) -> tk.Frame:
    """A sunken 'monitor' frame -- black background, inset bevel."""
    options = dict(bg=BG_SCREEN, relief="sunken", bd=BORDER_WIDTH)
    options.update(kwargs)
    return tk.Frame(master, **options)


def retro_button(master: tk.Misc, text: str, command: Callable[[], None], **kwargs) -> tk.Button:
    """A chunky raised-bevel button, like an old toolbar icon button."""
    options = dict(
        text=text,
        command=command,
        bg=BG_CHROME,
        fg=FG_TEXT,
        activebackground=SILVER,
        font=FONT_BODY,
        relief="raised",
        bd=BORDER_WIDTH,
        padx=10,
        pady=4,
        cursor="hand2",
    )
    options.update(kwargs)
    return tk.Button(master, **options)


def retro_label(master: tk.Misc, text: str = "", **kwargs) -> tk.Label:
    options = dict(text=text, bg=BG_CHROME, fg=FG_TEXT, font=FONT_BODY)
    options.update(kwargs)
    return tk.Label(master, **options)


def terminal_label(master: tk.Misc, text: str = "", **kwargs) -> tk.Label:
    """Label styled like green-on-black terminal text, for the game screen."""
    options = dict(text=text, bg=BG_SCREEN, fg=FG_TERMINAL, font=FONT_TERMINAL, anchor="w")
    options.update(kwargs)
    return tk.Label(master, **options)


def title_label(master: tk.Misc, text: str = "", **kwargs) -> tk.Label:
    options = dict(text=text, bg=BG_CHROME, fg=FG_ACCENT, font=FONT_TITLE)
    options.update(kwargs)
    return tk.Label(master, **options)
