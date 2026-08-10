"""
Credora AI — Credit Scoring Model
==================================
Task 1: Predict individual creditworthiness using classification algorithms
(Logistic Regression, Decision Tree, Random Forest).

Pipeline:
1. Synthetic-but-realistic financial dataset generation (income, debts,
   payment history, credit utilization, etc.)
2. Feature engineering (ratios, buckets, interaction terms)
3. Train/test split + scaling
4. Train 3 classifiers
5. Evaluate with Precision, Recall, F1-Score, ROC-AUC, Confusion Matrix
6. Export everything (metrics, ROC curves, feature importances, sample
   predictions, model coefficients) to JSON so the frontend dashboard can
   render real numbers instead of placeholders.
"""

import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    roc_curve, confusion_matrix, accuracy_score
)

RNG = np.random.default_rng(42)
N = 6000

# ---------------------------------------------------------------------------
# 1. SYNTHETIC DATASET GENERATION
# ---------------------------------------------------------------------------
age = RNG.integers(21, 70, N)
annual_income = np.clip(RNG.normal(65000, 28000, N), 12000, 260000)
employment_length = np.clip(RNG.normal(6, 4.5, N), 0, 40)
credit_history_length = np.clip((age - RNG.integers(18, 24, N)) + RNG.normal(0, 2, N), 0, 50)
num_credit_lines = np.clip(RNG.poisson(5, N), 0, 25)
num_late_payments_12m = np.clip(RNG.poisson(0.6, N), 0, 12)
num_derogatory_marks = np.clip(RNG.poisson(0.25, N), 0, 8)
credit_utilization = np.clip(RNG.beta(2, 3.2, N), 0, 1)
existing_loan_balance = np.clip(RNG.normal(15000, 14000, N), 0, 150000)
requested_loan_amount = np.clip(RNG.normal(18000, 12000, N), 500, 120000)
savings_balance = np.clip(RNG.exponential(9000, N), 0, 300000)
num_hard_inquiries_6m = np.clip(RNG.poisson(1.1, N), 0, 10)
home_ownership = RNG.choice(["own", "mortgage", "rent"], N, p=[0.22, 0.38, 0.40])
loan_purpose = RNG.choice(
    ["debt_consolidation", "home_improvement", "auto", "business", "education", "medical"],
    N, p=[0.32, 0.16, 0.18, 0.14, 0.12, 0.08]
)

debt_to_income = np.clip(
    (existing_loan_balance * 0.03 + requested_loan_amount * 0.02) / (annual_income / 12 + 1),
    0, 1.5
)

# Latent "true" creditworthiness score driving the label (logistic combination
# of the features above — mirrors how real bureau scoring models are built).
z = (
    0.75
    - 0.85 * debt_to_income * 10
    - 2.1 * credit_utilization
    - 0.6 * num_late_payments_12m
    - 0.8 * num_derogatory_marks
    - 0.3 * num_hard_inquiries_6m
    + 0.000022 * annual_income
    + 0.05 * employment_length
    + 0.035 * credit_history_length
    + 0.000008 * savings_balance
    + 0.15 * (home_ownership == "own")
    + 0.06 * (home_ownership == "mortgage")
    + RNG.normal(0, 0.85, N)
)
prob_good = 1 / (1 + np.exp(-z))
creditworthy = (RNG.random(N) < prob_good).astype(int)

df = pd.DataFrame({
    "age": age.round(0),
    "annual_income": annual_income.round(2),
    "employment_length_years": employment_length.round(1),
    "credit_history_length_years": credit_history_length.round(1),
    "num_credit_lines": num_credit_lines,
    "num_late_payments_12m": num_late_payments_12m,
    "num_derogatory_marks": num_derogatory_marks,
    "credit_utilization": credit_utilization.round(3),
    "existing_loan_balance": existing_loan_balance.round(2),
    "requested_loan_amount": requested_loan_amount.round(2),
    "savings_balance": savings_balance.round(2),
    "num_hard_inquiries_6m": num_hard_inquiries_6m,
    "home_ownership": home_ownership,
    "loan_purpose": loan_purpose,
    "debt_to_income_ratio": debt_to_income.round(3),
    "creditworthy": creditworthy,
})

# ---------------------------------------------------------------------------
# 2. FEATURE ENGINEERING
# ---------------------------------------------------------------------------
df["income_to_loan_ratio"] = (df["annual_income"] / (df["requested_loan_amount"] + 1)).round(3)
df["savings_to_income_ratio"] = (df["savings_balance"] / (df["annual_income"] + 1)).round(3)
df["delinquency_score"] = (
    df["num_late_payments_12m"] * 2 + df["num_derogatory_marks"] * 3 + df["num_hard_inquiries_6m"]
)
df["credit_mix_score"] = (df["num_credit_lines"] / (df["credit_history_length_years"] + 1)).round(3)
df["utilization_bucket"] = pd.cut(
    df["credit_utilization"], bins=[-0.01, 0.1, 0.3, 0.6, 1.01],
    labels=["excellent", "good", "fair", "poor"]
)

df_encoded = pd.get_dummies(
    df.drop(columns=["utilization_bucket"]),
    columns=["home_ownership", "loan_purpose"], drop_first=True
)

X = df_encoded.drop(columns=["creditworthy"])
y = df_encoded["creditworthy"]
feature_names = list(X.columns)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.22, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# ---------------------------------------------------------------------------
# 3. TRAIN MODELS
# ---------------------------------------------------------------------------
models = {
    "logistic_regression": LogisticRegression(max_iter=2000, C=0.8, random_state=42),
    "decision_tree": DecisionTreeClassifier(max_depth=7, min_samples_leaf=25, random_state=42),
    "random_forest": RandomForestClassifier(
        n_estimators=300, max_depth=10, min_samples_leaf=8, random_state=42, n_jobs=-1
    ),
}

results = {}
roc_curves = {}

for name, model in models.items():
    if name == "logistic_regression":
        model.fit(X_train_s, y_train)
        proba = model.predict_proba(X_test_s)[:, 1]
        preds = model.predict(X_test_s)
    else:
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)[:, 1]
        preds = model.predict(X_test)

    fpr, tpr, _ = roc_curve(y_test, proba)
    # Downsample ROC curve to ~40 points for lightweight JSON/chart
    idx = np.linspace(0, len(fpr) - 1, min(40, len(fpr))).astype(int)
    roc_curves[name] = {"fpr": fpr[idx].round(4).tolist(), "tpr": tpr[idx].round(4).tolist()}

    cm = confusion_matrix(y_test, preds)
    results[name] = {
        "accuracy": round(float(accuracy_score(y_test, preds)), 4),
        "precision": round(float(precision_score(y_test, preds)), 4),
        "recall": round(float(recall_score(y_test, preds)), 4),
        "f1_score": round(float(f1_score(y_test, preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
        "confusion_matrix": {
            "true_negative": int(cm[0][0]), "false_positive": int(cm[0][1]),
            "false_negative": int(cm[1][0]), "true_positive": int(cm[1][1]),
        },
    }

# ---------------------------------------------------------------------------
# 4. FEATURE IMPORTANCE (Random Forest)
# ---------------------------------------------------------------------------
rf_model = models["random_forest"]
importances = sorted(
    zip(feature_names, rf_model.feature_importances_.round(4).tolist()),
    key=lambda x: -x[1]
)[:10]

# ---------------------------------------------------------------------------
# 5. LOGISTIC REGRESSION COEFFICIENTS (for a lightweight client-side predictor)
# ---------------------------------------------------------------------------
lr_model = models["logistic_regression"]
lr_coefs = dict(zip(feature_names, lr_model.coef_[0].round(5).tolist()))
lr_intercept = round(float(lr_model.intercept_[0]), 5)
scaler_means = dict(zip(feature_names, scaler.mean_.round(5).tolist()))
scaler_scales = dict(zip(feature_names, scaler.scale_.round(5).tolist()))

# ---------------------------------------------------------------------------
# 6. DATASET SUMMARY STATS
# ---------------------------------------------------------------------------
dataset_summary = {
    "total_records": int(len(df)),
    "training_records": int(len(X_train)),
    "test_records": int(len(X_test)),
    "num_features_raw": 15,
    "num_features_engineered": len(feature_names),
    "class_balance": {
        "creditworthy": int(df["creditworthy"].sum()),
        "not_creditworthy": int(len(df) - df["creditworthy"].sum()),
    },
}

export = {
    "dataset_summary": dataset_summary,
    "model_results": results,
    "roc_curves": roc_curves,
    "feature_importance": importances,
    "logistic_regression": {
        "coefficients": lr_coefs,
        "intercept": lr_intercept,
        "scaler_means": scaler_means,
        "scaler_scales": scaler_scales,
        "feature_order": feature_names,
    },
}

with open("/home/claude/credora_results.json", "w") as f:
    json.dump(export, f, indent=2)

print(json.dumps({"model_results": results, "dataset_summary": dataset_summary}, indent=2))
print("\nTop features:", importances[:5])
