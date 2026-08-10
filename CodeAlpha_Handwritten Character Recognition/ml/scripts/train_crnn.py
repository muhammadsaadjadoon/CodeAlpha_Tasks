import argparse, random
from pathlib import Path
from PIL import Image
import torch
from torch import nn
from torch.utils.data import Dataset,DataLoader
from torchvision import transforms
from ml.models.crnn import WriteLensCRNN

class ManifestDataset(Dataset):
    def __init__(self,path):
        self.root=Path(path).resolve().parent; self.rows=[]
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            image,text=line.split("\t",1); self.rows.append((image,text))
        self.transform=transforms.Compose([transforms.Grayscale(),transforms.Resize((32,160)),transforms.ToTensor(),transforms.Normalize((0.5,),(0.5,))])
    def __len__(self): return len(self.rows)
    def __getitem__(self,i):
        image,text=self.rows[i]; p=Path(image); p=p if p.is_absolute() else self.root/p
        return self.transform(Image.open(p).convert("RGB")),text

def main():
    p=argparse.ArgumentParser(); p.add_argument("--manifest",required=True); p.add_argument("--epochs",type=int,default=25); p.add_argument("--batch-size",type=int,default=32); a=p.parse_args()
    ds=ManifestDataset(a.manifest)
    if not ds.rows: raise SystemExit("Manifest is empty.")
    charset=sorted(set("".join(text for _,text in ds.rows))); index={c:i+1 for i,c in enumerate(charset)} # 0 blank
    def collate(batch):
        images=torch.stack([x for x,_ in batch]); texts=[t for _,t in batch]; targets=torch.tensor([index[c] for t in texts for c in t],dtype=torch.long); lengths=torch.tensor([len(t) for t in texts],dtype=torch.long); return images,targets,lengths
    loader=DataLoader(ds,batch_size=a.batch_size,shuffle=True,collate_fn=collate); device=torch.device("cuda" if torch.cuda.is_available() else "cpu"); model=WriteLensCRNN(len(charset)+1).to(device); opt=torch.optim.AdamW(model.parameters(),lr=3e-4); loss_fn=nn.CTCLoss(blank=0,zero_infinity=True)
    for epoch in range(1,a.epochs+1):
        model.train(); total=0
        for images,targets,target_lengths in loader:
            images,targets=images.to(device),targets.to(device); opt.zero_grad(); log_probs=model(images); input_lengths=torch.full((images.size(0),),log_probs.size(0),dtype=torch.long); loss=loss_fn(log_probs,targets,input_lengths,target_lengths); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),5.0); opt.step(); total+=float(loss.item())
        print({"epoch":epoch,"ctc_loss":total/max(len(loader),1)})
    out=Path("models/checkpoints/writelens_crnn.pt"); out.parent.mkdir(parents=True,exist_ok=True); torch.jit.script(model.cpu().eval()).save(str(out)); out.with_suffix(".charset.txt").write_text("".join(charset),encoding="utf-8"); print("saved",out)
if __name__=="__main__": main()
