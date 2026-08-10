# Professional Training Strategy

## Datasets

- **MNIST**: digit specialist.
- **EMNIST Balanced**: balanced benchmark across merged character classes.
- **EMNIST ByClass**: main 62-class model: 10 digits + 26 uppercase + 26 lowercase.

The ByClass split is imbalanced, so WriteLens computes class weights for the training loss.

## CNN

`WriteLensCNN` uses three convolutional blocks, BatchNorm, GELU, pooling, dropout, adaptive pooling, and a linear classifier.

Training includes deterministic seeds, stratified validation splitting, label smoothing, class-weighted cross entropy, AdamW, OneCycleLR, CUDA mixed precision, gradient clipping, early stopping on validation Macro F1, held-out test metrics, confusion matrices, classification reports, TorchScript export, and JSON metadata.

## Champion policy

- `Digits` mode → MNIST specialist.
- `Characters` and `Auto` → EMNIST ByClass.
- EMNIST Balanced remains a benchmark/comparison checkpoint.

The UI reports a model as ready only when the real TorchScript checkpoint and metadata files exist. No fake trained weights are shipped.

## Word extension

The CRNN path combines a CNN visual encoder, bidirectional LSTM, and CTC loss for future word/line datasets.
