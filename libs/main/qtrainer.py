import torch

import torch.nn as nn
import torch.optim as optim

from libs.model import Linear_QNet

class QTrainer:
    def __init__(
        self,
        model: Linear_QNet,
        lr: float=0.01, 
        gamma: float=0.9
    ) -> None:
        self.model = model
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        self.lr = lr
        self.gamma = gamma


    def train_step(
        self,
        state: list[bool] | list[list[bool]],
        action: list[int] | list[list[int]],
        reward: int | list[int],
        next_state: list[bool] | list[list[bool]],
        done: bool | list[bool]
    ) -> float:
        state_t = torch.tensor(state, dtype=torch.float)
        next_state_t = torch.tensor(next_state, dtype=torch.float)
        action_t = torch.tensor(action, dtype=torch.long)
        reward_t = torch.tensor(reward, dtype=torch.float)
        done_seq: tuple[bool, ...] = (done, ) if isinstance(done, bool) else tuple(done)

        if len(state_t.shape) == 1:
            state_t = torch.unsqueeze(state_t, 0)
            next_state_t = torch.unsqueeze(next_state_t, 0)
            action_t = torch.unsqueeze(action_t, 0)
            reward_t = torch.unsqueeze(reward_t, 0)

        pred = self.model(state_t)
        target = pred.clone().detach()

        with torch.no_grad():
            for idx in range(len(done_seq)):
                Q_new = reward_t[idx]
                if not done_seq[idx]:
                    Q_new = reward_t[idx] + self.gamma * torch.max(self.model(next_state_t[idx]))

                action_idx = torch.argmax(action_t[idx]).item()
                target[idx][action_idx] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()

        return loss.item()

    
