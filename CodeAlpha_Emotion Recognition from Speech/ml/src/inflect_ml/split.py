import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


def speaker_disjoint_split(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    first = GroupShuffleSplit(n_splits=1, test_size=.2, random_state=seed)
    train_idx, hold_idx = next(first.split(df, groups=df.speaker_id))
    train = df.iloc[train_idx].copy()
    hold = df.iloc[hold_idx].copy()
    second = GroupShuffleSplit(n_splits=1, test_size=.5, random_state=seed)
    val_idx, test_idx = next(second.split(hold, groups=hold.speaker_id))
    val = hold.iloc[val_idx].copy()
    test = hold.iloc[test_idx].copy()
    train["split"] = "train"
    val["split"] = "validation"
    test["split"] = "test"
    return pd.concat([train, val, test]).sample(frac=1, random_state=seed).reset_index(drop=True)
