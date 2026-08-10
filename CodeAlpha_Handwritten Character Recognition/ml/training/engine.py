from dataclasses import dataclass
import copy
import numpy as np
import torch
from sklearn.metrics import f1_score
from tqdm import tqdm

@dataclass
class EpochResult:
    loss: float
    accuracy: float
    macro_f1: float

@torch.no_grad()
def evaluate(model,loader,criterion,device):
    model.eval(); losses=[]; preds=[]; targets=[]
    for x,y in loader:
        x,y=x.to(device),y.to(device); logits=model(x); losses.append(float(criterion(logits,y).item())); preds.extend(logits.argmax(1).cpu().tolist()); targets.extend(y.cpu().tolist())
    acc=float(np.mean(np.array(preds)==np.array(targets))) if targets else 0.0
    f1=float(f1_score(targets,preds,average="macro",zero_division=0)) if targets else 0.0
    return EpochResult(float(np.mean(losses)) if losses else 0.0,acc,f1),targets,preds

def train_model(model,train_loader,val_loader,criterion,optimizer,scheduler,device,epochs:int,patience:int=6):
    scaler=torch.cuda.amp.GradScaler(enabled=device.type=="cuda")
    best_state=copy.deepcopy(model.state_dict()); best_f1=-1.0; stale=0; history=[]
    for epoch in range(1,epochs+1):
        model.train(); total_loss=0.0; seen=0; correct=0
        bar=tqdm(train_loader,desc=f"epoch {epoch}/{epochs}",leave=False)
        for x,y in bar:
            x,y=x.to(device),y.to(device); optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=device.type=="cuda"):
                logits=model(x); loss=criterion(logits,y)
            scaler.scale(loss).backward(); scaler.unscale_(optimizer); torch.nn.utils.clip_grad_norm_(model.parameters(),5.0); scaler.step(optimizer); scaler.update()
            if scheduler is not None: scheduler.step()
            n=y.size(0); seen+=n; total_loss+=float(loss.item())*n; correct+=int((logits.argmax(1)==y).sum().item())
            bar.set_postfix(loss=f"{total_loss/max(seen,1):.4f}",acc=f"{correct/max(seen,1):.3f}")
        val,_,_=evaluate(model,val_loader,criterion,device)
        row={"epoch":epoch,"train_loss":total_loss/max(seen,1),"train_accuracy":correct/max(seen,1),"val_loss":val.loss,"val_accuracy":val.accuracy,"val_macro_f1":val.macro_f1}; history.append(row); print(row)
        if val.macro_f1>best_f1+1e-4: best_f1=val.macro_f1; best_state=copy.deepcopy(model.state_dict()); stale=0
        else:
            stale+=1
            if stale>=patience: print(f"Early stopping at epoch {epoch}."); break
    model.load_state_dict(best_state); return history,best_f1
