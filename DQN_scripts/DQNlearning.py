import torch
import torch.nn as nn
import torch.nn.functional as F

class DQN(nn.Module):

    def __init__(self, n_observations, n_actions=3 ):
        super(DQN, self).__init__()
        self.Input = nn.Linear(n_observations, 128)
        self.layer1 = nn.Linear(128, 128)
        self.layer2 = nn.Linear(128, 32)
        self.Output = nn.Linear(32, n_actions)

    # Called with either one element to determine next action, or a batch
    # during optimization. Returns tensor([[left0exp,right0exp]...]).
    def forward(self, x):
        x = F.relu(self.Input(x))
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.Output(x) #idx 0: action_id, idx 1: LINEAR_SPEED [0, 1], idx 2: ANGULAR_SPEED[-1, 1]