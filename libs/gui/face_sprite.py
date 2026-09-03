import os
import tkinter as tk

from libs.theme import BG_SCREEN

ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "faces",
)

EXPRESSION_FILES = {
    "normal": "normal.png",
    "happy": "eat.png",
    "dead": "game_over.png",
}

# The source PNGs don't have a real alpha channel -- their "transparent"
# background got baked in as an actual gray checkerboard pattern. Strip it
# by making near-neutral-gray pixels in that brightness band transparent.
CHECKER_MAX_CHANNEL_SPREAD = 8
CHECKER_MIN_BRIGHTNESS = 160
CHECKER_MAX_BRIGHTNESS = 235


def _strip_checkerboard(image: tk.PhotoImage) -> None:
    width, height = image.width(), image.height()
    for y in range(height):
        for x in range(width):
            r, g, b = image.get(x, y)
            spread = max(r, g, b) - min(r, g, b)
            brightness = (r + g + b) / 3
            if spread <= CHECKER_MAX_CHANNEL_SPREAD and CHECKER_MIN_BRIGHTNESS <= brightness <= CHECKER_MAX_BRIGHTNESS:
                image.transparency_set(x, y, True)


class FaceSprite:
    """Agent status portrait -- swaps between a few pre-made PNGs
    (normal / eating / game-over), scaled up to fill as much of its holder
    as possible. tk.PhotoImage only supports integer zoom (no Pillow), so
    resize() picks the largest whole-number zoom that still fits, and gets
    called again whenever the holder's real size becomes known/changes
    (e.g. once the window finishes going fullscreen)."""

    def __init__(self, master: tk.Misc, max_width: int = 200, max_height: int = 200) -> None:
        self._raw: dict[str, tk.PhotoImage] = {}
        for expression, filename in EXPRESSION_FILES.items():
            image = tk.PhotoImage(file=os.path.join(ASSETS_DIR, filename))
            _strip_checkerboard(image)
            self._raw[expression] = image

        first_raw = next(iter(self._raw.values()))
        self._native_w = first_raw.width()
        self._native_h = first_raw.height()

        self.canvas = tk.Canvas(master, bg=BG_SCREEN, highlightthickness=0)
        self.canvas.pack(expand=True)

        self._images: dict[str, tk.PhotoImage] = {}
        self._expression = ""
        self.resize(max_width, max_height)
        self.set_expression("normal")

    def resize(self, max_width: int, max_height: int) -> None:
        zoom = max(1, min(max_width // self._native_w, max_height // self._native_h))
        self._images = {
            expression: (image.zoom(zoom, zoom) if zoom > 1 else image)
            for expression, image in self._raw.items()
        }

        first = next(iter(self._images.values()))
        self.canvas.config(width=first.width(), height=first.height())
        if self._expression:
            self._redraw()

    def set_expression(self, expression: str) -> None:
        if expression == self._expression:
            return
        self._expression = expression
        self._redraw()

    def _redraw(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self._images[self._expression], anchor="nw")
