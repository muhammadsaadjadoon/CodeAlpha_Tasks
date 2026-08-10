# WriteLens — Complete File Map

## Root
- `.env.example`
- `.gitignore`
- `README.md`
- `FILES.md`
- `COMMANDS.md`

## Backend
- `backend/requirements.txt`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/0001_initial.py`
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/db.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/security.py`
- `backend/app/deps.py`
- `backend/app/middleware.py`
- `backend/app/routers/auth.py`
- `backend/app/routers/profile.py`
- `backend/app/routers/recognition.py`
- `backend/app/routers/history.py`
- `backend/app/routers/model_info.py`
- `backend/app/services/image_preprocessing.py`
- `backend/app/services/model_runtime.py`
- `backend/tests/test_preprocessing.py`
- `backend/tests/test_privacy_contract.py`

## Frontend
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/vite.config.ts`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/api.ts`
- `frontend/src/types.ts`
- `frontend/src/styles.css`
- `frontend/src/components/Brand.tsx`
- `frontend/src/components/UserAvatar.tsx`
- `frontend/src/components/Dropzone.tsx`
- `frontend/src/components/DrawingPad.tsx`
- `frontend/src/components/ResultPanel.tsx`
- `frontend/src/pages/AuthPage.tsx`
- `frontend/src/pages/RecognizePage.tsx`
- `frontend/src/pages/HistoryPage.tsx`
- `frontend/src/pages/ModelLabPage.tsx`
- `frontend/src/pages/GuidePage.tsx`
- `frontend/src/pages/AccountPage.tsx`
- `frontend/public/brand/writelens-light.png`
- `frontend/public/brand/writelens-dark.png`

## Machine learning
- `ml/requirements-train.txt`
- `ml/datasets.py`
- `ml/models/cnn.py`
- `ml/models/crnn.py`
- `ml/training/engine.py`
- `ml/training/metrics.py`
- `ml/scripts/download_datasets.py`
- `ml/scripts/train_classifier.py`
- `ml/scripts/train_all.py`
- `ml/scripts/evaluate_checkpoint.py`
- `ml/scripts/register_models.py`
- `ml/scripts/train_crnn.py`

## Docs and scripts
- `docs/REQUIREMENTS_TRACEABILITY.md`
- `docs/TRAINING_STRATEGY.md`
- `docs/PRIVACY_STORAGE.md`
- `docs/API_OVERVIEW.md`
- `scripts/setup.ps1`
- `scripts/dev.ps1`
- `scripts/train_all.ps1`
- `scripts/preflight.ps1`
- `scripts/verify_models.ps1`
- `VALIDATION.md`
