import argparse
import json
import os

from libs.main import Agent
from libs.snake_game import SnakeGame

parser = argparse.ArgumentParser()
parser.add_argument("--save-file", type=str, default=None, help="Ruta del checkpoint a guardar/cargar")
parser.add_argument("--reward-shaping", action="store_true", help="Premia acercarse/alejarse de la comida en vez de reward=0 por paso")
args = parser.parse_args()

checkpoint_path = args.save_file


def stats_path(checkpoint_path: str) -> str:
    base, _ = os.path.splitext(checkpoint_path)
    return base + "_stats.json"


if checkpoint_path is not None:
    os.makedirs(os.path.dirname(checkpoint_path) or ".", exist_ok=True)

game = SnakeGame(reward_shaping=args.reward_shaping)
agent = Agent(file_name=checkpoint_path)

total_score = 0
record = 0

if checkpoint_path is not None and os.path.exists(stats_path(checkpoint_path)):
    with open(stats_path(checkpoint_path), "r") as f:
        stats = json.load(f)
    total_score = stats.get("total_score", 0)
    record = stats.get("record", 0)

while True:
    state = game.get_state()
    action = agent.get_action(state)

    reward, game_over, score = game.play_step(action)
    state_new = game.get_state()

    agent.train_short_memory(state, action, reward, state_new, game_over)
    agent.remember(state, action, reward, state_new, game_over)

    if game_over:
        agent.train_long_memory()
        game.reset()

        if score > record:
            record = score
            if checkpoint_path is not None:
                agent.save(checkpoint_path)

        total_score += score
        mean_score = total_score / agent.n_games

        if checkpoint_path is not None:
            with open(stats_path(checkpoint_path), "w") as f:
                json.dump({"total_score": total_score, "record": record}, f)

        print(f"<GAME: {agent.n_games} -- SCORE: {score} -- RECORD: {record} -- MEAN: {mean_score:.2f}>")
