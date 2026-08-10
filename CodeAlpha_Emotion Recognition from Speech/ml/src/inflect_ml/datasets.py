from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from .labels import CREMA, RAVDESS, TESS

@dataclass
class Record:
    path: str
    label: str
    speaker_id: str
    dataset: str


def scan_ravdess(root: Path) -> list[Record]:
    records=[]
    for path in root.rglob("*.wav"):
        parts=path.stem.split("-")
        if len(parts)>=7 and parts[2] in RAVDESS:
            records.append(Record(str(path.resolve()),RAVDESS[parts[2]],f"ravdess_{parts[6]}","ravdess"))
    return records


def scan_crema(root: Path) -> list[Record]:
    records=[]
    for path in root.rglob("*.wav"):
        parts=path.stem.split("_")
        if len(parts)>=3 and parts[2] in CREMA:
            records.append(Record(str(path.resolve()),CREMA[parts[2]],f"crema_{parts[0]}","crema_d"))
    return records


def scan_tess(root: Path) -> list[Record]:
    records=[]
    for path in root.rglob("*.wav"):
        lower=path.stem.lower(); label=next((mapped for key,mapped in TESS.items() if lower.endswith(key)),None)
        if label:
            speaker="tess_oaf" if "oaf" in lower else "tess_yaf"
            records.append(Record(str(path.resolve()),label,speaker,"tess"))
    return records


def build_manifest(data_root: Path) -> pd.DataFrame:
    records=scan_ravdess(data_root/"ravdess")+scan_crema(data_root/"crema_d")+scan_tess(data_root/"tess")
    return pd.DataFrame([r.__dict__ for r in records])
