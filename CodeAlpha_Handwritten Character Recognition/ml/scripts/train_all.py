import argparse, subprocess, sys

def run(args): print("+",*args); subprocess.run(args,check=True)
def main():
    p=argparse.ArgumentParser(); p.add_argument("--batch-size",type=int,default=256); p.add_argument("--quick",action="store_true"); a=p.parse_args()
    epochs=(5,8,10) if a.quick else (15,25,30)
    run([sys.executable,"ml/scripts/train_classifier.py","--dataset","mnist","--epochs",str(epochs[0]),"--batch-size",str(a.batch_size),"--lr","0.001","--output-name","mnist_digit"])
    run([sys.executable,"ml/scripts/train_classifier.py","--dataset","emnist-balanced","--epochs",str(epochs[1]),"--batch-size",str(a.batch_size),"--lr","0.001","--output-name","emnist_balanced"])
    run([sys.executable,"ml/scripts/train_classifier.py","--dataset","emnist-byclass","--epochs",str(epochs[2]),"--batch-size",str(a.batch_size),"--lr","0.001","--output-name","emnist_byclass"])
    run([sys.executable,"ml/scripts/register_models.py","--digit","models/checkpoints/mnist_digit.pt","--character","models/checkpoints/emnist_byclass.pt"])
if __name__=="__main__": main()
