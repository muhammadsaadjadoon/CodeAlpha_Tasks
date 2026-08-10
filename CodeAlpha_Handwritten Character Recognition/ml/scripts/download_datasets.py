import argparse
from ml.datasets import build_dataset

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--datasets",nargs="+",default=["mnist","emnist-balanced","emnist-byclass"]); args=parser.parse_args()
    for name in args.datasets:
        print(f"Downloading/verifying {name}...")
        train=build_dataset(name,True,False,True); test=build_dataset(name,False,False,True)
        print(f"{name}: train={len(train):,}, test={len(test):,}, classes={len(train.classes)}")
if __name__=="__main__": main()
