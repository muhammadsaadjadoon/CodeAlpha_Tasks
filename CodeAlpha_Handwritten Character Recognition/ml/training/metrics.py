from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, recall_score

def classification_metrics(y_true,y_pred,classes):
    return {
        "accuracy":float(accuracy_score(y_true,y_pred)),
        "macro_f1":float(f1_score(y_true,y_pred,average="macro",zero_division=0)),
        "uar":float(recall_score(y_true,y_pred,average="macro",zero_division=0)),
        "classification_report":classification_report(y_true,y_pred,labels=list(range(len(classes))),target_names=[str(x) for x in classes],zero_division=0,output_dict=True),
    }

def save_confusion(y_true,y_pred,classes,path:Path):
    cm=confusion_matrix(y_true,y_pred,labels=list(range(len(classes))),normalize="true")
    size=max(8,min(22,len(classes)*0.35))
    fig,ax=plt.subplots(figsize=(size,size))
    im=ax.imshow(cm,interpolation="nearest",cmap="Blues",vmin=0,vmax=1)
    ax.set_title("Normalized Confusion Matrix")
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    if len(classes)<=20:
        ticks=np.arange(len(classes)); ax.set_xticks(ticks,classes,rotation=90); ax.set_yticks(ticks,classes)
    fig.colorbar(im,ax=ax,fraction=0.046,pad=0.04)
    fig.tight_layout(); path.parent.mkdir(parents=True,exist_ok=True); fig.savefig(path,dpi=180); plt.close(fig)
