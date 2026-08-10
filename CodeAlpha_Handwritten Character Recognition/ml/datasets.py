from pathlib import Path
from torchvision import datasets, transforms
from torchvision.transforms import functional as TF

DATA_ROOT=Path("data/raw/torchvision")

class FixEMNISTOrientation:
    def __call__(self,image):
        return TF.hflip(TF.rotate(image,-90))

def transform_for(name:str,train:bool):
    ops=[]
    if name.startswith("emnist-"):
        ops.append(FixEMNISTOrientation())
    if train:
        ops.extend([
            transforms.RandomAffine(degrees=12,translate=(0.10,0.10),scale=(0.90,1.10),shear=5,fill=0),
            transforms.RandomPerspective(distortion_scale=0.12,p=0.20,fill=0),
        ])
    ops.extend([transforms.ToTensor(),transforms.Normalize((0.5,),(0.5,))])
    return transforms.Compose(ops)

def build_dataset(name:str,train:bool,augment:bool=False,download:bool=True):
    root=str(DATA_ROOT)
    transform=transform_for(name,train and augment)
    if name=="mnist":
        ds=datasets.MNIST(root=root,train=train,download=download,transform=transform)
    elif name=="emnist-balanced":
        ds=datasets.EMNIST(root=root,split="balanced",train=train,download=download,transform=transform)
    elif name=="emnist-byclass":
        ds=datasets.EMNIST(root=root,split="byclass",train=train,download=download,transform=transform)
    else:
        raise ValueError(f"Unsupported dataset: {name}")
    return ds
