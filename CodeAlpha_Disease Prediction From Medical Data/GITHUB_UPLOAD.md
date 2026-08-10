# Publish HeartTrack to GitHub

Create an empty repository on GitHub, then run these commands from the HeartTrack repository folder.

```powershell
git init
git add .
git commit -m "Initial HeartTrack release"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

## Before the first push

Confirm that environment files and dependency folders are not staged:

```powershell
git status
```

The repository should not contain:

- `.env`
- `.venv`
- `node_modules`
- `frontend/dist`
- Python cache folders
- editor/OS files

The repository intentionally includes the trained model artifact, evaluation metrics, processed dataset, and raw UCI cohort files so that the application can display model and dataset information immediately after setup.

## Recommended repository description

```text
Full-stack heart-risk prediction application built with React, FastAPI, scikit-learn, and XGBoost.
```

## Suggested GitHub topics

```text
machine-learning
fastapi
react
healthcare
heart-disease
scikit-learn
xgboost
python
vite
classification
```
