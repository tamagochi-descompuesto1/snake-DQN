import argparse
import os
import tkinter as tk

from libs.main import Agent, Orchestrator
from libs.render import GameRenderer
from libs.snake_game import SnakeGame

CHECKPOINT_PATH = "model/model.pth"
TICK_MS = 50

parser = argparse.ArgumentParser()
parser.add_argument("--reward-shaping", action="store_true", help="Premia acercarse/alejarse de la comida en vez de reward=0 por paso")
args = parser.parse_args()

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

os.makedirs(os.path.dirname(CHECKPOINT_PATH) or ".", exist_ok=True)

root = tk.Tk()
root.title("Snake DQN")
root.configure(bg="black")

game = SnakeGame(reward_shaping=args.reward_shaping)
agent = Agent(file_name=CHECKPOINT_PATH)
renderer = GameRenderer(root)

stats_frame = tk.Frame(root, bg="black")
stats_frame.pack(fill="x", padx=8, pady=4)

stats_label = tk.Label(
    stats_frame,
    text="Gen: 0   Score: 0   Record: 0   Mean: 0.00   Reward: 0",
    fg="#39FF14",
    bg="black",
    font=("Consolas", 12, "bold"),
    anchor="w",
)
stats_label.pack(fill="x")

state_frame = tk.Frame(root, bg="black")
state_frame.pack(fill="x", padx=8, pady=4)

state_value_labels: list[tk.Label] = []
for i, label in enumerate(STATE_LABELS):
    row, col = divmod(i, 4)
    cell = tk.Label(
        state_frame,
        text=f"{label}: -",
        fg="white",
        bg="black",
        font=("Consolas", 10),
        anchor="w",
        width=16,
    )
    cell.grid(row=row, column=col, sticky="w", padx=4, pady=1)
    state_value_labels.append(cell)


def on_step(info: dict) -> None:
    renderer.redraw(info)

    stats_label.config(
        text=(
            f"Gen: {info['n_games']}   "
            f"Score: {info['score']}   "
            f"Record: {info['record']}   "
            f"Mean: {info['mean_score']:.2f}   "
            f"Reward: {info['reward']}"
        )
    )

    for lbl, name, value in zip(state_value_labels, STATE_LABELS, info["state"]):
        lbl.config(text=f"{name}: {value}")


orchestrator = Orchestrator(
    game,
    agent,
    on_step_callback=on_step,
    check_point_path=CHECKPOINT_PATH,
)


def toggle_pause() -> None:
    orchestrator.toggle_pause()


pause_button = tk.Button(root, text="Pausa / Reanudar", command=toggle_pause)
pause_button.pack(pady=4)


def tick() -> None:
    orchestrator.step()
    root.after(TICK_MS, tick)


renderer.draw_initial({"snake": game.snake, "food": game.food})
tick()
root.mainloop()
