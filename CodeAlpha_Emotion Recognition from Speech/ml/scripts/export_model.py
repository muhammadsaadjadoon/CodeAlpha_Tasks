import argparse, shutil
from pathlib import Path
parser=argparse.ArgumentParser(); parser.add_argument("--source",default="ml/outputs/wav2vec2/champion"); parser.add_argument("--destination",default="models/champion"); args=parser.parse_args()
src=Path(args.source); dst=Path(args.destination)
if not (src/"config.json").exists(): raise SystemExit("Champion model not found. Train the model first.")
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(src,dst)
print(f"Deployed model to {dst}")
