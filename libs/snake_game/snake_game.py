import random as rd

from enum import Enum
from collections import namedtuple

WIDTH = 500
HEIGHT = 500
BLOCK_SIZE = 10

REWARD_FOOD = 10
REWARD_DEATH = -10
REWARD_STEP = 0
REWARD_CLOSER = 0.1
REWARD_FARTHER = -0.1

# Force game_over if the snake goes this many steps (relative to its own
# length) without eating, to cut off endless wandering/tail-chasing loops.
STEP_LIMIT_MULTIPLIER = 100

Point = namedtuple('Point', 'x, y')

class Direction(Enum):
    RIGHT = 1
    LEFT  = 2
    UP    = 3
    DOWN  = 4

# Clockwise order of directions, used to resolve relative turns (straight/right/left)
CLOCKWISE = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]

# (dx, dy) movement offset for each absolute direction.
# y follows canvas/screen convention (grows downward), so UP is negative.
DIRECTION_VECTORS = {
    Direction.RIGHT: (BLOCK_SIZE, 0),
    Direction.LEFT:  (-BLOCK_SIZE, 0),
    Direction.UP:    (0, -BLOCK_SIZE),
    Direction.DOWN:  (0, BLOCK_SIZE),
}

# One-hot [left, right, up, down] flags for each absolute direction
DIRECTION_FLAGS = {
    Direction.LEFT:  [True, False, False, False],
    Direction.RIGHT: [False, True, False, False],
    Direction.UP:    [False, False, True, False],
    Direction.DOWN:  [False, False, False, True],
}


class SnakeGame:
    """Core Snake game logic: state, movement, collisions and scoring."""

    def __init__(self, reward_shaping: bool = False):
        """Initialize a new game with a fresh snake, direction, score and food.

        Args:
            reward_shaping: if True, non-terminal steps reward getting closer
                to the food (REWARD_CLOSER) and penalize moving away
                (REWARD_FARTHER) instead of the flat REWARD_STEP.
        """
        self.reward_shaping = reward_shaping
        self.snake: list[Point] = [
            Point(70, 50), # Head first
            Point(60, 50),
            Point(50, 50)
        ]
        self.snake_positions: set[Point] = set(self.snake)
        self.direction: Direction = Direction.RIGHT
        self.score: int = 0
        self.frame_iteration: int = 0
        self._place_food()

    def reset(self) -> None:
        """Reset the game back to its initial state."""
        self.__init__(reward_shaping=self.reward_shaping)

    def play_step(self, action: list[int]) -> tuple[float, bool, int]:
        """Advance the game by one step given a relative action.

        Args:
            action: One-hot list [straight, right, left] describing the turn
                to apply, relative to the snake's current direction.

        Returns:
            A tuple of (reward, game_over, score).
        """
        self.frame_iteration += 1

        # Change snake direction
        idx = CLOCKWISE.index(self.direction)

        if action == [1, 0, 0]:
            self.direction = CLOCKWISE[idx]              # Straight
        elif action == [0, 1, 0]:
            self.direction = CLOCKWISE[(idx + 1) % 4]     # Right
        else:  # [0, 0, 1]
            self.direction = CLOCKWISE[(idx - 1) % 4]     # Left

        # Move snake
        dx, dy = DIRECTION_VECTORS[self.direction]
        head = self.snake[0]
        new_head = Point(head.x + dx, head.y + dy)

        # Handle collision, or stalling too long without making progress
        # (checked before mutating snake/snake_positions)
        stalled = self.frame_iteration > STEP_LIMIT_MULTIPLIER * len(self.snake)
        if self._is_collision(new_head) or stalled:
            return (REWARD_DEATH, True, self.score)

        self.snake.insert(0, new_head)
        self.snake_positions.add(new_head)

        # Handle eating food
        if new_head == self.food:
            self.score += 10
            self.frame_iteration = 0
            self._place_food()
            return (REWARD_FOOD, False, self.score)
        else:
            tail = self.snake.pop()
            self.snake_positions.discard(tail)

            reward: float = REWARD_STEP
            if self.reward_shaping:
                old_distance = abs(head.x - self.food.x) + abs(head.y - self.food.y)
                new_distance = abs(new_head.x - self.food.x) + abs(new_head.y - self.food.y)
                reward = REWARD_CLOSER if new_distance < old_distance else REWARD_FARTHER

            return (reward, False, self.score)

    def get_state(self) -> list[bool]:
        """Build the 14-value state vector used by the agent.

        Layout: [danger ahead, danger left, danger right,
                 danger ahead x2, danger left x2, danger right x2,
                 direction left, direction right, direction up, direction down,
                 food left, food right, food up, food down]
        """
        head = self.snake[0]
        idx = CLOCKWISE.index(self.direction)
        dir_ahead = CLOCKWISE[idx]
        dir_right = CLOCKWISE[(idx + 1) % 4]
        dir_left = CLOCKWISE[(idx - 1) % 4]

        def point_towards(direction: Direction, steps: int = 1) -> Point:
            """Return the point `steps` blocks away from the head in `direction`."""
            dx, dy = DIRECTION_VECTORS[direction]
            return Point(head.x + dx * steps, head.y + dy * steps)

        state = [
            self._is_collision(point_towards(dir_ahead)),
            self._is_collision(point_towards(dir_left)),
            self._is_collision(point_towards(dir_right)),
            self._is_collision(point_towards(dir_ahead, steps=2)),
            self._is_collision(point_towards(dir_left, steps=2)),
            self._is_collision(point_towards(dir_right, steps=2)),
            *DIRECTION_FLAGS[self.direction],
            head.x > self.food.x,
            head.x < self.food.x,
            head.y > self.food.y,
            head.y < self.food.y,
        ]

        return state

    def _is_collision(self, point: Point) -> bool:
        """Check whether a point hits a wall or the snake's own body."""
        return (point.x < 0 or point.x > WIDTH - BLOCK_SIZE) or (point.y < 0 or point.y > HEIGHT - BLOCK_SIZE) or (point in self.snake_positions)

    def _place_food(self) -> None:
        """Place food on a random grid cell that doesn't overlap the snake."""
        x = rd.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE  # Round to nearest int locked to block size
        y = rd.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)

        if self.food in self.snake_positions:
            # Try again if generated Point overlaps with snake
            return self._place_food()
