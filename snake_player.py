import tkinter as tk

from libs.snake_game import SnakeGame, Direction, WIDTH, HEIGHT, CLOCKWISE, BLOCK_SIZE

KEY_TO_DIRECTION = {
    "Up": Direction.UP,
    "Down": Direction.DOWN,
    "Left": Direction.LEFT,
    "Right": Direction.RIGHT,
}

# Order must match SnakeGame.get_state()'s documented layout
STATE_LABELS = [
    "Danger ahead",
    "Danger left",
    "Danger right",
    "Dir: left",
    "Dir: right",
    "Dir: up",
    "Dir: down",
    "Food: left",
    "Food: right",
    "Food: up",
    "Food: down",
]

HUD_HEIGHT = 40      # header strip above the board, for score/reward/length
PANEL_WIDTH = 220    # side panel, for the state vector
PANEL_PADDING = 12
LINE_HEIGHT = 20

game = SnakeGame()
state = { "action": [1, 0, 0] }
gen = 1

root = tk.Tk()
canvas = tk.Canvas(root, width=WIDTH + PANEL_WIDTH, height=HUD_HEIGHT + HEIGHT, bg="black")
canvas.pack()

# Separators between header/board and board/panel
canvas.create_line(0, HUD_HEIGHT, WIDTH + PANEL_WIDTH, HUD_HEIGHT, fill="#333333")
canvas.create_line(WIDTH, HUD_HEIGHT, WIDTH, HUD_HEIGHT + HEIGHT, fill="#333333")

food_id = canvas.create_rectangle(
    game.food.x, game.food.y + HUD_HEIGHT,
    game.food.x + BLOCK_SIZE, game.food.y + HUD_HEIGHT + BLOCK_SIZE,
    fill="red",
)

snake_ids = []
for point in game.snake:
    snake_ids.append(canvas.create_rectangle(
        point.x, point.y + HUD_HEIGHT,
        point.x + BLOCK_SIZE, point.y + HUD_HEIGHT + BLOCK_SIZE,
        fill="green",
    ))

hud_text_id = canvas.create_text(
    10, 10,
    text="Score: 0   Reward: 0   Length: 0",
    fill="#39FF14",
    font=("Consolas", 14, "bold"),
    anchor="nw",
)

canvas.create_text(
    WIDTH + PANEL_PADDING, PANEL_PADDING,
    text="STATE",
    fill="#39FF14",
    font=("Consolas", 13, "bold"),
    anchor="nw",
)

state_text_ids = []
for i, label in enumerate(STATE_LABELS):
    y = PANEL_PADDING + (i + 2) * LINE_HEIGHT
    state_text_ids.append(canvas.create_text(
        WIDTH + PANEL_PADDING, y,
        text=f"{label}: -",
        fill="white",
        font=("Consolas", 11),
        anchor="nw",
    ))

def move_snake(event: tk.Event) -> None:
    target_direction = KEY_TO_DIRECTION.get(event.keysym)
    if target_direction is None:
        return

    idx_current = CLOCKWISE.index(game.direction)
    idx_target = CLOCKWISE.index(target_direction)

    diff = (idx_target - idx_current) % 4

    if diff == 0:
        state["action"] = [1, 0, 0]
    elif diff == 1:
        state["action"] = [0, 1, 0]
    elif diff == 3:
        state["action"] = [0, 0, 1]


def tick():
    reward, game_over, score = game.play_step(state["action"])
    state["action"] = [1, 0, 0]

    canvas.coords(
        food_id,
        game.food.x, game.food.y + HUD_HEIGHT,
        game.food.x + BLOCK_SIZE, game.food.y + HUD_HEIGHT + BLOCK_SIZE,
    )

    for rect_id in snake_ids:
        canvas.delete(rect_id)

    snake_ids.clear()
    for point in game.snake:
        snake_ids.append(canvas.create_rectangle(
            point.x, point.y + HUD_HEIGHT,
            point.x + BLOCK_SIZE, point.y + HUD_HEIGHT + BLOCK_SIZE,
            fill="green",
        ))

    canvas.itemconfig(hud_text_id, text=f"Score: {score}   Reward: {reward}   Length: {len(snake_ids)}")

    for text_id, label, value in zip(state_text_ids, STATE_LABELS, game.get_state()):
        canvas.itemconfig(text_id, text=f"{label}: {value}")

    if game_over:
        game.reset()

    root.after(80, tick)

root.bind("<Key>", move_snake)

tick()
root.mainloop()
