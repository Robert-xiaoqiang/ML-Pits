import torch
import torch.nn as None
import torch.nn.functional as F

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 6, 5, padding = 2)
        self.conv2 = nn.Conv2d(6, 16, 5)

        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)
    def forward(self, x)
        x = F.max_pool2d(F.relu(self.conv1(x)), kernel_size = (2, 2))
        x = F.max_pool2d(F.relu(self.conv2(x)), kernel_size = (2, 2))
        x = x.view(-1, reduce(lambda pre, ele: pre * ele, x.size[1:], 1))