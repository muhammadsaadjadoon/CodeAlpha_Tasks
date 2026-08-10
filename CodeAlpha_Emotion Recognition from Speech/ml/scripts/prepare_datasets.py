import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from inflect_ml.datasets import build_manifest
from inflect_ml.split import speaker_disjoint_split

parser=argparse.ArgumentParser()
parser.add_argument("--data-root",type=Path,default=Path("data/raw"))
parser.add_argument("--output",type=Path,default=Path("data/manifests/inflect.csv"))
args=parser.parse_args()
df=build_manifest(args.data_root)
if df.empty: raise SystemExit("No supported audio files found. Read data/README.md.")
df=speaker_disjoint_split(df)
args.output.parent.mkdir(parents=True,exist_ok=True)
df.to_csv(args.output,index=False)
print(df.groupby(["dataset","split","label"]).size())
print(f"Saved {len(df)} records to {args.output}")
