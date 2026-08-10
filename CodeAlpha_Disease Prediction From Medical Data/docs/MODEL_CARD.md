# HeartTrack Model Card

## Purpose

The HeartTrack model estimates the probability of recorded heart-disease presence from 13 structured features. It supports the application's educational machine-learning workflow and is not a clinical decision-support device.

## Candidate Models

The training pipeline compares:

- Logistic Regression
- Support Vector Machine
- Random Forest
- XGBoost

Model selection uses five-fold cross-validated ROC-AUC on the training partition.

## Current Selected Model

**SVM + sigmoid calibration**

The included artifact was selected by cross-validated ROC-AUC and subsequently calibrated for probability output.

## Data Split

- Total records: 920
- Training records: 736
- Holdout records: 184
- Holdout fraction: 20%
- Stratified split: yes
- Random state: 42

## Included Holdout Metrics

| Metric | Value |
|---|---:|
| ROC-AUC | 0.8951 |
| Accuracy | 0.7826 |
| Balanced accuracy | 0.7752 |
| Precision | 0.7818 |
| Recall | 0.8431 |
| F1 score | 0.8113 |
| Brier score | 0.1343 |

## Model Selection Results

| Model | Cross-validated ROC-AUC | Holdout ROC-AUC |
|---|---:|---:|
| Logistic Regression | 0.8791 | 0.8834 |
| SVM | 0.8807 | 0.8955 |
| Random Forest | 0.8745 | 0.9078 |
| XGBoost | 0.8750 | 0.9015 |

The selected model is determined by cross-validation performance rather than by choosing the best holdout score. This preserves the holdout set for final evaluation.

## Prediction Threshold

The included artifact uses a probability threshold of `0.5` for binary classification.

The application's Low, Moderate, High, and Very High labels are presentation bands for the model probability. They are not clinical risk categories.

## Local Feature Influence

For each submitted feature, the model service substitutes a reference value and recalculates probability. The difference from the original estimate is used to rank a small set of local influences.

This is a simple counterfactual comparison for interface explanation. It should not be interpreted as causal evidence or a formal clinical explanation.

## Limitations

- The model has not been clinically validated.
- The underlying UCI data is historical and contains missing values.
- Dataset composition may not represent current or diverse clinical populations.
- Probability calibration does not guarantee clinical calibration in a new population.
- Predictions should not be used for diagnosis, treatment, triage, or emergency decisions.
