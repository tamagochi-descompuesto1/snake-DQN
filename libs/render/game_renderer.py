import tkinter as tk

from typing import Any
from libs.snake_game import WIDTH, HEIGHT, BLOCK_SIZE
from libs.theme import BG_SCREEN, SNAKE_COLOR, FOOD_COLOR, FG_ACCENT, GRID_LINE

class GameRenderer:
    def __init__(
        self,
        master: tk.Misc,
        cell_px: float=BLOCK_SIZE,
        bg: str=BG_SCREEN
    ) -> None:
        self.cell_px = cell_px
        self.cols = WIDTH // BLOCK_SIZE
        self.rows = HEIGHT // BLOCK_SIZE

        self.canvas = tk.Canvas(
            master,
            width=self.cols * self.cell_px,
            height=self.rows * self.cell_px,
            bg=bg,
            highlightthickness=0,
        )

        self.canvas.pack()

        self.cell_ids: list[list[int]] = []

    def draw_initial(self, game_state: dict[str, Any]) -> None:
        self.cell_ids = []

        for row in range(self.rows):
            row_ids = []
            for col in range(self.cols):
                x1 = col * self.cell_px
                y1 = row * self.cell_px
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x1 + self.cell_px, y1 + self.cell_px,
                    fill=BG_SCREEN, outline=GRID_LINE
                )
                row_ids.append(rect_id)
            self.cell_ids.append(row_ids)
        self.redraw(game_state)

    def redraw(self, game_state: dict[str, Any]) -> None:
        for row_ids in self.cell_ids:
            for rect_id in row_ids:
                self.canvas.itemconfig(rect_id, fill=BG_SCREEN)

        snake = game_state["snake"]
        for point in snake:
            col, row = point.x // BLOCK_SIZE, point.y // BLOCK_SIZE
            self.canvas.itemconfig(self.cell_ids[row][col], fill=SNAKE_COLOR)

        if snake:
            head = snake[0]
            col, row = head.x // BLOCK_SIZE, head.y // BLOCK_SIZE
            self.canvas.itemconfig(self.cell_ids[row][col], fill=FG_ACCENT)

        food = game_state["food"]
        col, row = food.x // BLOCK_SIZE, food.y // BLOCK_SIZE
        self.canvas.itemconfig(self.cell_ids[row][col], fill=FOOD_COLOR)
