from dataclasses import dataclass


@dataclass
class TrainConfig:
    """Settings gathered from ConfigFrame before starting a training session."""

    gamma: float = 0.9
    epsilon_start: int = 100
    load_checkpoint: bool = False
    render_speed: int = 50
    reward_shaping: bool = True
    checkpoint_path: str = "model/model.pth"
