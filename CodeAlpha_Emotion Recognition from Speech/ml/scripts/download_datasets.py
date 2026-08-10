import argparse
import io
import shutil
import subprocess
import zipfile
from pathlib import Path
import requests
from tqdm import tqdm

RAVDESS_ZIP = "https://zenodo.org/records/1188976/files/Audio_Speech_Actors_01-24.zip?download=1"
CREMA_REPO = "https://github.com/CheyneyComputerScience/CREMA-D.git"

def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=(10, 180)) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        with destination.open("wb") as handle, tqdm(total=total, unit="B", unit_scale=True, desc=destination.name) as bar:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    handle.write(chunk); bar.update(len(chunk))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--ravdess", action="store_true")
    parser.add_argument("--crema", action="store_true")
    args = parser.parse_args()
    if not args.ravdess and not args.crema:
        args.ravdess = args.crema = True
    if args.ravdess:
        archive = args.data_root / "ravdess.zip"
        download(RAVDESS_ZIP, archive)
        target = args.data_root / "ravdess"; target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as zf: zf.extractall(target)
        archive.unlink()
    if args.crema:
        target = args.data_root / "crema_d"
        if target.exists(): shutil.rmtree(target)
        subprocess.run(["git", "clone", "--depth", "1", CREMA_REPO, str(target)], check=True)
    print("RAVDESS and CREMA-D are ready. TESS must be downloaded from the official Borealis Dataverse and placed in data/raw/tess.")

if __name__ == "__main__":
    main()
