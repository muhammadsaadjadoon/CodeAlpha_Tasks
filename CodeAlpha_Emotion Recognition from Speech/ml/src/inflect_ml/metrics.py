import numpy as np
from sklearn.metrics import accuracy_score, f1_score, recall_score


def classification_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "macro_f1": f1_score(labels, preds, average="macro", zero_division=0),
        "uar": recall_score(labels, preds, average="macro", zero_division=0),
    }
