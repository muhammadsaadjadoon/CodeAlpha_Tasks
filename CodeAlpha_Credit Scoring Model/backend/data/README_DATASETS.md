# Credora datasets

This project now includes two training datasets:

1. `credit_dataset.csv` — the existing synthetic credit-risk dataset.
2. `kaggle_credit_risk_dataset.csv` — the provided Kaggle credit-risk dataset.

Train with the synthetic dataset:

```powershell
cd backend
python -m app.ml.train --dataset synthetic
```

Train with the Kaggle dataset:

```powershell
cd backend
python -m app.ml.train --dataset kaggle
```

The training pipeline automatically maps Kaggle columns such as `person_age`, `person_income`, `loan_amnt`, `loan_intent`, `loan_status`, `cb_person_default_on_file`, and `cb_person_cred_hist_length` into Credora's internal feature names. For Kaggle `loan_status`, the target is normalized so that `1` means creditworthy inside Credora and `0` means higher credit risk.
