import torch
from torch import nn

class ConvBlock(nn.Module):
    def __init__(self,in_channels:int,out_channels:int,dropout:float):
        super().__init__()
        self.net=nn.Sequential(
            nn.Conv2d(in_channels,out_channels,3,padding=1,bias=False),
            nn.BatchNorm2d(out_channels),
            nn.GELU(),
            nn.Conv2d(out_channels,out_channels,3,padding=1,bias=False),
            nn.BatchNorm2d(out_channels),
            nn.GELU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout),
        )
    def forward(self,x): return self.net(x)

class WriteLensCNN(nn.Module):
    def __init__(self,num_classes:int):
        super().__init__()
        self.features=nn.Sequential(
            ConvBlock(1,32,0.05),
            ConvBlock(32,64,0.08),
            ConvBlock(64,128,0.12),
            nn.AdaptiveAvgPool2d((2,2)),
        )
        self.head=nn.Sequential(
            nn.Flatten(),
            nn.Linear(128*2*2,256),
            nn.GELU(),
            nn.Dropout(0.35),
            nn.Linear(256,num_classes),
        )
    def forward(self,x): return self.head(self.features(x))
