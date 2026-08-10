# WriteLens — Commands, One by One

Run from the project root in PowerShell.

## Setup
```powershell
Copy-Item .env.example .env
```
```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
Put that value in `.env` as `APP_SECRET`.

```powershell
py -3.14 -m venv backend\.venv
```
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
```powershell
& ".\backend\.venv\Scripts\Activate.ps1"
```
```powershell
python -m pip install --upgrade pip setuptools wheel
```
```powershell
python -m pip install -r backend\requirements.txt
```
```powershell
python -m pip install -r ml\requirements-train.txt
```
```powershell
python -m alembic -c backend\alembic.ini upgrade head
```
```powershell
cd frontend
npm install
cd ..
```

## Download datasets
```powershell
python ml\scripts\download_datasets.py --datasets mnist emnist-balanced emnist-byclass
```

## Train models
```powershell
python ml\scripts\train_classifier.py --dataset mnist --epochs 15 --batch-size 256 --lr 0.001 --output-name mnist_digit
```
```powershell
python ml\scripts\train_classifier.py --dataset emnist-balanced --epochs 25 --batch-size 256 --lr 0.001 --output-name emnist_balanced
```
```powershell
python ml\scripts\train_classifier.py --dataset emnist-byclass --epochs 30 --batch-size 256 --lr 0.001 --output-name emnist_byclass
```

## Register trained app models
```powershell
python ml\scripts\register_models.py --digit models\checkpoints\mnist_digit.pt --character models\checkpoints\emnist_byclass.pt
```

## Tests
```powershell
python -m pytest backend\tests -v
```

## Run frontend + backend
```powershell
powershell -ExecutionPolicy Bypass -File scripts\dev.ps1
```
Frontend: `http://localhost:5173`  
API docs: `http://127.0.0.1:8000/docs`

## Train all through one command
```powershell
powershell -ExecutionPolicy Bypass -File scripts\train_all.ps1
```

## CRNN extension
Create `data\processed\word_manifest.tsv` where each line is `image_path<TAB>transcription`, then:
```powershell
python ml\scripts\train_crnn.py --manifest data\processed\word_manifest.tsv --epochs 25
```

## Submission preflight
```powershell
powershell -ExecutionPolicy Bypass -File scripts\preflight.ps1
```

## Verify trained application models
```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_models.ps1
```
