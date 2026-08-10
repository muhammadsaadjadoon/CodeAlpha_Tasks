<div align="center">
  <img src="frontend/src/assets-hearttrack-logo.png" alt="HeartTrack logo" width="110" />

# HeartTrack

### Smart Heart Risk Prediction

A full-stack heart-risk assessment application built with React, FastAPI, and a calibrated machine-learning pipeline.

</div>

---

## Overview

HeartTrack provides a guided workflow for entering structured cardiovascular data, generating a model-based risk estimate, reviewing model evidence, exploring the training dataset, and exporting assessment results.

The application combines a responsive React interface with a FastAPI backend and a reproducible training pipeline that compares Logistic Regression, SVM, Random Forest, and XGBoost classifiers.

> **Important:** HeartTrack is intended for educational and informational use. Its predictions are not clinically validated and must not be used as a diagnosis or as a substitute for professional medical advice.

## Highlights

- Guided 13-feature heart-risk assessment
- Calibrated probability and risk-level output
- Local feature influence summary for each prediction
- Model comparison dashboard with training and evaluation metrics
- Dataset inspection for the combined UCI Heart Disease cohorts
- Secure HttpOnly-cookie authentication
- Account creation and session management
- Session case review and report export
- Responsive dark clinical interface
- Reproducible model training and evaluation scripts
- Automated backend tests

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router, Vite |
| Backend | FastAPI, Pydantic, Uvicorn |
| Machine Learning | scikit-learn, XGBoost, pandas, NumPy |
| Authentication | HttpOnly cookies, PyJWT, Argon2 |
| Testing | pytest, HTTPX |

## Machine-Learning Pipeline

HeartTrack evaluates four classifiers:

1. Logistic Regression
2. Support Vector Machine (SVM)
3. Random Forest
4. XGBoost

Model selection is based on five-fold cross-validated ROC-AUC. The selected estimator is then probability-calibrated before serving predictions.

The repository currently includes a trained **SVM with sigmoid calibration** artifact. The included evaluation report records:

| Metric | Value |
|---|---:|
| ROC-AUC | 0.8951 |
| Accuracy | 78.26% |
| Recall | 84.31% |
| F1 score | 0.8113 |
| Brier score | 0.1343 |

See [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md) for methodology, limitations, and evaluation details.

## Dataset

The training data combines the processed UCI Heart Disease cohorts from:

- Cleveland — 303 records
- Hungarian — 294 records
- VA Long Beach — 200 records
- Switzerland — 123 records

Total: **920 records** with **13 predictive features**.

See [`docs/DATASET.md`](docs/DATASET.md) for the feature list and preprocessing notes.

## Repository Structure

```text
HeartTrack/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── model_service.py
│   │   └── schemas.py
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── ml/
│   │   ├── artifacts/
│   │   ├── data.py
│   │   ├── evaluate.py
│   │   ├── predict_cli.py
│   │   └── train.py
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── data/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
├── docs/
├── scripts/
├── .gitattributes
├── .gitignore
├── CONTRIBUTING.md
├── QUICK_START.md
├── SECURITY.md
└── README.md
```

## Requirements

- Python 3.14.x
- Node.js 22.x or another version supported by Vite 8
- npm
- Windows PowerShell for the included helper scripts

The application can also be started manually on other operating systems.

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd HeartTrack
```

### 2. Create the Python environment

Windows PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary=:all: -r backend\requirements.txt
```

### 3. Configure the backend

```powershell
Copy-Item backend\.env.example backend\.env
```

For a public or deployed environment, replace `HEARTTRACK_SECRET_KEY` with a strong random value and review the cookie/security settings before use.

### 4. Configure the frontend

```powershell
Copy-Item frontend\.env.example frontend\.env
```

The default frontend configuration uses `/api`, which is proxied to the FastAPI server during Vite development.

### 5. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

## Run the Application

Open two terminals.

### Backend

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

### Included access account

```text
Email: demo@hearttrack.ai
Password: HeartTrack@2026
```

The credentials can be overridden through backend environment variables.

## Rebuild the Dataset and Models

The repository includes the processed dataset, metrics, and trained model artifact, so retraining is not required to start the application.

To reproduce the pipeline:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m ml.data
python -m ml.train --mode full
python -m ml.evaluate
```

For a faster development run:

```powershell
python -m ml.train --mode fast
```

Training outputs are written to:

```text
backend/ml/artifacts/model_bundle.joblib
backend/ml/artifacts/metrics.json
backend/ml/artifacts/dataset_report.json
```

## Tests

From the backend directory:

```powershell
python -m pytest -q
```

Frontend production build:

```powershell
cd frontend
npm run build
```

## Main API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/auth/register` | Create an account |
| `POST` | `/api/auth/login` | Start an authenticated session |
| `GET` | `/api/auth/me` | Read the current account |
| `POST` | `/api/auth/logout` | End the session |
| `GET` | `/api/health` | Service and model status |
| `POST` | `/api/prediction/heart` | Generate a heart-risk estimate |
| `GET` | `/api/models/report` | Read model evaluation data |
| `GET` | `/api/models/dataset` | Read dataset summary data |

## Privacy and Data Handling

- Authentication uses a signed HttpOnly cookie.
- Patient assessments and session cases are not persisted to browser storage by the application.
- Newly created accounts are kept in server memory for the active API process.
- Restarting the API clears accounts created during that process.
- The application should not be used to store or process real clinical data without an appropriate production security, privacy, and compliance review.

## Documentation

- [Quick Start](QUICK_START.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Dataset Notes](docs/DATASET.md)
- [Model Card](docs/MODEL_CARD.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [GitHub Publishing Guide](GITHUB_UPLOAD.md)

## Medical Disclaimer

HeartTrack is a software demonstration of a machine-learning workflow. It is not a medical device, has not been clinically validated, and does not provide medical advice. Any health concern should be discussed with a qualified healthcare professional.
