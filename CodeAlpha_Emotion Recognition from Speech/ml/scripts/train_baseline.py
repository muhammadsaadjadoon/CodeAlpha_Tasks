import argparse
from pathlib import Path
import random
import numpy as np
import pandas as pd
import torch
import torchaudio
from torch import nn
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import f1_score, recall_score
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from inflect_ml.labels import LABELS, LABEL2ID

class SpeechDataset(Dataset):
    def __init__(self, frame: pd.DataFrame, sample_rate: int = 16000, seconds: int = 8):
        self.frame=frame.reset_index(drop=True); self.sr=sample_rate; self.length=sample_rate*seconds
        self.mel=torchaudio.transforms.MelSpectrogram(sample_rate=sample_rate,n_fft=400,hop_length=160,n_mels=64)
        self.db=torchaudio.transforms.AmplitudeToDB()
    def __len__(self): return len(self.frame)
    def __getitem__(self,index):
        row=self.frame.iloc[index]; wave,sr=torchaudio.load(row.path); wave=wave.mean(0,keepdim=True)
        if sr!=self.sr: wave=torchaudio.functional.resample(wave,sr,self.sr)
        wave=wave[:,:self.length]; wave=torch.nn.functional.pad(wave,(0,max(0,self.length-wave.shape[1])))
        feature=self.db(self.mel(wave)).clamp(-80,0)/80+1
        return feature, LABEL2ID[row.label]

class MelCNN(nn.Module):
    def __init__(self):
        super().__init__(); self.net=nn.Sequential(
            nn.Conv2d(1,32,3,padding=1),nn.BatchNorm2d(32),nn.GELU(),nn.MaxPool2d(2),
            nn.Conv2d(32,64,3,padding=1),nn.BatchNorm2d(64),nn.GELU(),nn.MaxPool2d(2),
            nn.Conv2d(64,128,3,padding=1),nn.BatchNorm2d(128),nn.GELU(),nn.AdaptiveAvgPool2d((1,1)))
        self.head=nn.Sequential(nn.Flatten(),nn.Dropout(.25),nn.Linear(128,len(LABELS)))
    def forward(self,x): return self.head(self.net(x))

def evaluate(model,loader,device):
    model.eval(); truth=[]; pred=[]; loss=[]; criterion=nn.CrossEntropyLoss()
    with torch.inference_mode():
        for x,y in loader:
            x,y=x.to(device),y.to(device); logits=model(x); loss.append(criterion(logits,y).item()); truth.extend(y.cpu()); pred.extend(logits.argmax(1).cpu())
    return np.mean(loss), f1_score(truth,pred,average="macro",zero_division=0), recall_score(truth,pred,average="macro",zero_division=0)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--manifest",default="data/manifests/inflect.csv"); parser.add_argument("--epochs",type=int,default=25); parser.add_argument("--output",default="ml/outputs/baseline"); args=parser.parse_args()
    torch.manual_seed(42); df=pd.read_csv(args.manifest); device="cuda" if torch.cuda.is_available() else "cpu"
    loaders={split:DataLoader(SpeechDataset(df[df.split==split]),batch_size=16,shuffle=split=="train",num_workers=2,pin_memory=True) for split in ["train","validation","test"]}
    model=MelCNN().to(device); optimizer=torch.optim.AdamW(model.parameters(),lr=3e-4,weight_decay=1e-3); criterion=nn.CrossEntropyLoss(); best=-1
    output=Path(args.output); output.mkdir(parents=True,exist_ok=True)
    for epoch in range(1,args.epochs+1):
        model.train()
        for x,y in loaders["train"]:
            x,y=x.to(device),y.to(device); optimizer.zero_grad(); loss=criterion(model(x),y); loss.backward(); optimizer.step()
        val_loss,val_f1,val_uar=evaluate(model,loaders["validation"],device); print(epoch,val_loss,val_f1,val_uar)
        if val_f1>best: best=val_f1; torch.save({"model":model.state_dict(),"labels":LABELS},output/"best.pt")
    model.load_state_dict(torch.load(output/"best.pt",map_location=device)["model"]); print("test",evaluate(model,loaders["test"],device))
if __name__=="__main__": main()
