# Dataset Notes

## Source

HeartTrack uses the processed UCI Heart Disease cohorts included in the repository:

| Cohort | Records |
|---|---:|
| Cleveland | 303 |
| Hungarian | 294 |
| VA Long Beach | 200 |
| Switzerland | 123 |
| **Total** | **920** |

The source files are stored under `backend/data/raw/`. The combined processed file is written to `backend/data/processed/hearttrack_uci_combined.csv`.

Original dataset reference: UCI Machine Learning Repository — Heart Disease.

## Target

The original disease severity values are converted into a binary target:

- `0` — no recorded heart disease
- `1` — recorded heart disease

The source cohort is retained for reporting but is not used as a predictive feature.

## Predictive Features

| Feature | Description |
|---|---|
| `age` | Age |
| `sex` | Sex |
| `cp` | Chest pain type |
| `trestbps` | Resting blood pressure |
| `chol` | Serum cholesterol |
| `fbs` | Fasting blood sugar indicator |
| `restecg` | Resting ECG result |
| `thalach` | Maximum heart rate achieved |
| `exang` | Exercise-induced angina |
| `oldpeak` | ST depression |
| `slope` | ST-segment slope |
| `ca` | Number of major vessels |
| `thal` | Thalassemia category |

## Missing Values

The historical cohorts contain missing values. Numeric features are imputed with the median inside the scikit-learn training pipeline. Zero values in selected clinical measurements are treated as missing before training where appropriate.

## Limitations

- The records are historical.
- Missingness differs substantially across features and cohorts.
- The dataset does not represent every population or clinical setting.
- A model trained on these records must not be interpreted as a clinically validated risk score.
