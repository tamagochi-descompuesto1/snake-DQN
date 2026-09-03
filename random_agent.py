import random as rd

from libs.snake_game import SnakeGame

ACTIONS = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

game = SnakeGame()
for i in range(50):
    while True:
        action = rd.choice(ACTIONS)

        reward, game_over, score = game.play_step(action)

        print(f"<GAME: {i + 1} -- REWARD: {reward} -- GAME_OVER: {game_over} -- SCORE: {score}>")
        if game_over:
            game.reset()
            break