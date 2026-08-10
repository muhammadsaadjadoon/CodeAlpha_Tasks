import argparse,json
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import DataLoader
from ml.datasets import build_dataset
from ml.training.engine import evaluate
from ml.training.metrics import classification_metrics

def main():
    p=argparse.ArgumentParser(); p.add_argument("--checkpoint",required=True); p.add_argument("--batch-size",type=int,default=256); a=p.parse_args()
    cp=Path(a.checkpoint); meta=json.loads(cp.with_suffix(".json").read_text(encoding="utf-8")); ds=build_dataset(meta["dataset"],False,False,True); loader=DataLoader(ds,batch_size=a.batch_size,shuffle=False)
    model=torch.jit.load(str(cp),map_location="cpu").eval(); criterion=nn.CrossEntropyLoss(); result,y_true,y_pred=evaluate(model,loader,criterion,torch.device("cpu")); metrics=classification_metrics(y_true,y_pred,meta["classes"]); metrics["loss"]=result.loss; print(json.dumps({k:metrics[k] for k in ["accuracy","macro_f1","uar","loss"]},indent=2))
if __name__=="__main__": main()
