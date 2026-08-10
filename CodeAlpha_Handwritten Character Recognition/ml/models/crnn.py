import torch
from torch import nn

class WriteLensCRNN(nn.Module):
    """Word/line extension: CNN -> BiLSTM -> CTC logits."""
    def __init__(self,num_symbols:int,hidden:int=192):
        super().__init__()
        self.cnn=nn.Sequential(
            nn.Conv2d(1,64,3,padding=1),nn.BatchNorm2d(64),nn.ReLU(),nn.MaxPool2d(2,2),
            nn.Conv2d(64,128,3,padding=1),nn.BatchNorm2d(128),nn.ReLU(),nn.MaxPool2d(2,2),
            nn.Conv2d(128,256,3,padding=1),nn.BatchNorm2d(256),nn.ReLU(),nn.MaxPool2d((2,1)),
            nn.Conv2d(256,256,3,padding=1),nn.BatchNorm2d(256),nn.ReLU(),nn.AdaptiveAvgPool2d((1,None)),
        )
        self.sequence=nn.LSTM(256,hidden,num_layers=2,bidirectional=True,dropout=0.2,batch_first=False)
        self.classifier=nn.Linear(hidden*2,num_symbols)
    def forward(self,x):
        x=self.cnn(x).squeeze(2).permute(2,0,1)
        x,_=self.sequence(x)
        return self.classifier(x).log_softmax(2)
