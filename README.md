# CodeAlpha_Tasks

A collection of four full-stack machine learning projects completed during my Machine Learning Internship at CodeAlpha. Each project pairs a real ML system with a production-style web application — React frontends, FastAPI backends, trained model artifacts, tests, and deployment configuration — demonstrating practical end-to-end ML engineering and real-world development experience.

Each project folder has its own detailed README with setup instructions, model documentation, and API references.

## Projects

### 1. Credora — Credit Risk Intelligence
**Folder:** `CodeAlpha_Credit Scoring Model`

A full-stack ML credit-risk assessment workspace. Benchmarks Logistic Regression, Decision Tree, and Random Forest models under one preprocessing pipeline, with 29 engineered operational features, a 300–850 credit score mapping, and four risk bands. Includes a React 18 + Vite dashboard frontend, a FastAPI backend (SQLAlchemy, SQLite, Pydantic v2, Uvicorn), Pytest test coverage, and a docker-compose setup.

### 2. HeartTrack — Smart Heart Risk Intelligence
**Folder:** `CodeAlpha_Disease Prediction From Medical Data`

A complete ML product for guided cardiovascular risk assessment. Takes 13 structured clinical features through an FastAPI backend serving the best of Logistic Regression, SVM, Random Forest, and XGBoost models selected by 5-fold cross-validated ROC-AUC (selected artifact: sigmoid-calibrated SVM, holdout ROC-AUC 0.8951). React 19 + React Router 7 + Vite 8 frontend; JWT authentication in HttpOnly SameSite cookies with Argon2 password hashing; trained and evaluated on the UCI Heart Disease cohorts (920 records).

### 3. INFLECT — Speech Emotion Intelligence
**Folder:** `CodeAlpha_Emotion Recognition from Speech`

A privacy-first, full-stack Speech Emotion Recognition platform for recording or uploading speech, running local acoustic emotion inference, and explaining the results. React + TypeScript + Vite frontend, FastAPI backend (SQLAlchemy 2 + Alembic), and a PyTorch/TorchAudio/Librosa audio stack. Inference runs on a portable local acoustic ensemble (two calibrated RBF-SVM experts with PCA and temperature scaling) trained on RAVDESS speech-only data (1,440 clips, 24 actors, 7 emotion classes). Raw audio is transient only — only result metadata is stored.

### 4. WriteLens — See What You Write
**Folder:** `CodeAlpha_Handwritten Character Recognition`

A privacy-first, full-stack handwritten character recognition workspace powered by custom PyTorch CNNs. Draw on a React + TypeScript + Vite canvas frontend, get predictions from a FastAPI backend with OpenCV/Pillow preprocessing. Two registered specialist models: the MNIST Digit Specialist (10 classes, 99.74% test accuracy) and the EMNIST ByClass Character Model (62 classes, 83.95% test accuracy), exported as TorchScript for fast inference.

## Tech Stack

- **Languages:** Python, TypeScript, JavaScript
- **Machine Learning:** scikit-learn, PyTorch, TorchAudio, XGBoost, NumPy, Pandas, Matplotlib, Librosa, SoundFile, OpenCV
- **Backend:** FastAPI, Pydantic, SQLAlchemy, Alembic, Uvicorn, JWT authentication
- **Frontend:** React (18 & 19), TypeScript, Vite, React Router, Lucide React
- **DevOps & Tooling:** Docker, Docker Compose, Pytest, Make

## Getting Started

Each project folder is self-contained with its own README — start there for install steps, quick-start guides, and contribution/security notes.

## Author

Muhammad Saad Jadoon — AI Engineer
