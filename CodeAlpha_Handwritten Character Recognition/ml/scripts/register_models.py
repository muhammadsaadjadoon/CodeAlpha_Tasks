import argparse,json
from pathlib import Path

def entry(name,checkpoint):
    cp=Path(checkpoint); stem=cp.stem
    return {"name":name,"checkpoint":cp.as_posix(),"metadata":(cp.with_suffix(".json")).as_posix(),"metrics":(Path("models/reports")/f"{stem}.metrics.json").as_posix()}
def main():
    p=argparse.ArgumentParser(); p.add_argument("--digit",required=True); p.add_argument("--character",required=True); a=p.parse_args()
    for value in [a.digit,a.character]:
        cp=Path(value); md=cp.with_suffix(".json")
        if not cp.exists() or not md.exists(): raise SystemExit(f"Missing trained checkpoint or metadata: {cp}")
    registry={"digit":entry("MNIST Digit Specialist",a.digit),"character":entry("EMNIST ByClass Character Model",a.character)}
    Path("models/registry.json").write_text(json.dumps(registry,indent=2),encoding="utf-8"); print("models/registry.json updated")
if __name__=="__main__": main()
