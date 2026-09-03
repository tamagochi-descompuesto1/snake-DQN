from libs.main import Agent
from libs.snake_game import SnakeGame

game = SnakeGame()
agent = Agent()

total_score = 0
record = 0
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

        total_score += score
        mean_score = total_score / agent.n_games

        print(f"<GAME: {agent.n_games} -- SCORE: {score} -- RECORD: {record} -- MEAN: {mean_score:.2f}>")