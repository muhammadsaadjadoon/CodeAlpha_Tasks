# Architecture

HeartTrack is organized as three cooperating layers: the React client, the FastAPI application, and the machine-learning pipeline.

## Request Flow

```text
React UI
   │
   │  /api requests
   ▼
Vite development proxy
   │
   ▼
FastAPI
   ├── Authentication
   ├── Health / model information
   ├── Dataset report
   └── Prediction endpoint
            │
            ▼
     HeartModelService
            │
            ▼
 model_bundle.joblib
```

## Frontend

The frontend is a React single-page application. It provides:

- authentication and account creation
- overview dashboard
- guided assessment flow
- result presentation
- session case review
- model and dataset exploration
- reports, profile, settings, and system status

During development, Vite proxies `/api` requests to `127.0.0.1:8000`. This keeps browser requests on the frontend origin while the API runs as a separate development service.

## Backend

FastAPI exposes authentication, prediction, health, model-report, and dataset-report routes. Pydantic schemas validate incoming assessment values before they reach the model service.

Authentication is based on signed HttpOnly cookies. Account passwords are hashed with Argon2.

## Model Service

`backend/app/model_service.py` loads the serialized model bundle and performs inference. The bundle contains:

- calibrated estimator
- expected feature order
- model name
- decision threshold
- feature reference values used for local influence comparisons

For each prediction, HeartTrack calculates the model probability and compares each submitted feature with a reference value to produce a compact local influence summary.

## Training Pipeline

`backend/ml/train.py`:

1. builds the combined dataset
2. performs a stratified train/test split
3. evaluates four candidate algorithms
4. tunes candidates using cross-validation in full mode
5. selects the highest cross-validated ROC-AUC model
6. calibrates the selected estimator
7. writes the model bundle and evaluation report

The holdout set remains separate from model selection.
