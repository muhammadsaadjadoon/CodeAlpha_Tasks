# INFLECT RAVDESS Synthetic Acoustic Ensemble

Version: 1.0.0

## Training data
- 1,440 unique RAVDESS speech clips from 24 actors.
- Speaker-disjoint split: actors 01–16 train, 17–20 validation, 21–24 test.
- Calm is harmonized into Neutral for the seven-emotion INFLECT taxonomy.
- Three label-preserving synthetic augmentation views per training clip.

## Model
Two calibrated RBF-SVM acoustic experts over standardized PCA projections of a 1,606-dimensional feature representation. The representation combines log-Mel distribution statistics, delta dynamics, temporal pooling, energy, zero-crossing, crest and waveform statistics. The runtime is NumPy/Torch-based and does not require scikit-learn.

## Held-out evaluation
- Validation accuracy: 0.5000
- Validation Macro-F1: 0.4659
- Validation UAR: 0.4866
- Test accuracy: 0.4375
- Test Macro-F1: 0.4187
- Test UAR: 0.4256

## Responsible use
This model estimates vocal emotion patterns; it does not read thoughts, establish intent, diagnose health conditions, or provide a universal measure of a person’s emotional state. RAVDESS is acted and recorded in controlled conditions, so real-world performance may differ.
