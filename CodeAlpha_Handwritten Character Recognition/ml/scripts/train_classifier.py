import argparse, json, random
from pathlib import Path
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Subset
from ml.datasets import build_dataset
from ml.models.cnn import WriteLensCNN
from ml.training.engine import evaluate, train_model
from ml.training.metrics import classification_metrics, save_confusion

def seed_all(seed:int):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dataset",choices=["mnist","emnist-balanced","emnist-byclass"],required=True)
    p.add_argument("--epochs",type=int,default=25); p.add_argument("--batch-size",type=int,default=256); p.add_argument("--lr",type=float,default=1e-3); p.add_argument("--weight-decay",type=float,default=1e-4); p.add_argument("--val-size",type=float,default=0.10); p.add_argument("--patience",type=int,default=6); p.add_argument("--workers",type=int,default=0); p.add_argument("--seed",type=int,default=42); p.add_argument("--output-name",required=True)
    args=p.parse_args(); seed_all(args.seed)
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("device:",device)
    train_aug=build_dataset(args.dataset,True,True,True); train_eval=build_dataset(args.dataset,True,False,True); test_ds=build_dataset(args.dataset,False,False,True)
    labels=np.asarray(train_eval.targets)
    indices=np.arange(len(labels)); train_idx,val_idx=train_test_split(indices,test_size=args.val_size,random_state=args.seed,stratify=labels)
    train_loader=DataLoader(Subset(train_aug,train_idx),batch_size=args.batch_size,shuffle=True,num_workers=args.workers,pin_memory=device.type=="cuda")
    val_loader=DataLoader(Subset(train_eval,val_idx),batch_size=args.batch_size,shuffle=False,num_workers=args.workers,pin_memory=device.type=="cuda")
    test_loader=DataLoader(test_ds,batch_size=args.batch_size,shuffle=False,num_workers=args.workers,pin_memory=device.type=="cuda")
    classes=[str(x) for x in train_eval.classes]; num_classes=len(classes)
    counts=np.bincount(labels[train_idx],minlength=num_classes).astype(np.float64); weights=counts.sum()/np.maximum(counts,1); weights=weights/weights.mean()
    criterion=nn.CrossEntropyLoss(weight=torch.tensor(weights,dtype=torch.float32,device=device),label_smoothing=0.05)
    model=WriteLensCNN(num_classes).to(device); optimizer=torch.optim.AdamW(model.parameters(),lr=args.lr,weight_decay=args.weight_decay)
    scheduler=torch.optim.lr_scheduler.OneCycleLR(optimizer,max_lr=args.lr,epochs=args.epochs,steps_per_epoch=len(train_loader),pct_start=0.15,div_factor=10,final_div_factor=100)
    history,best_f1=train_model(model,train_loader,val_loader,criterion,optimizer,scheduler,device,args.epochs,args.patience)
    test_result,y_true,y_pred=evaluate(model,test_loader,criterion,device); metrics=classification_metrics(y_true,y_pred,classes); metrics.update({"dataset":args.dataset,"test_loss":test_result.loss,"best_val_macro_f1":best_f1,"epochs_completed":len(history),"history":history,"seed":args.seed,"class_count":num_classes})
    checkpoints=Path("models/checkpoints"); reports=Path("models/reports"); checkpoints.mkdir(parents=True,exist_ok=True); reports.mkdir(parents=True,exist_ok=True)
    model_cpu=model.cpu().eval(); scripted=torch.jit.script(model_cpu); pt=checkpoints/f"{args.output_name}.pt"; scripted.save(str(pt))
    metadata={"name":args.output_name,"model_version":f"{args.output_name}-v1","dataset":args.dataset,"classes":classes,"input_shape":[1,28,28],"normalization":{"mean":0.5,"std":0.5},"architecture":"WriteLensCNN","torchscript":True}
    (checkpoints/f"{args.output_name}.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    (reports/f"{args.output_name}.metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    save_confusion(y_true,y_pred,classes,reports/f"{args.output_name}.confusion.png")
    print(json.dumps({k:metrics[k] for k in ["accuracy","macro_f1","uar"]},indent=2)); print("saved:",pt)
if __name__=="__main__": main()
