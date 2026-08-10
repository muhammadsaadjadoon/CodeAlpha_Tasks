# Training data

The complete INFLECT application already includes its trained local champion under `models/champion`. The source RAVDESS audio is not redistributed inside the final project archive.

For reproducible retraining, place the user-supplied Kaggle RAVDESS archive anywhere on the machine and run:

```powershell
python ml\scripts\train_ravdess_champion.py --archive "E:\path\to\archive.zip" --output models\champion
```

An extracted dataset is also supported:

```powershell
python ml\scripts\train_ravdess_champion.py --ravdess-root data\raw\ravdess --output models\champion
```

The trainer identifies one complete `Actor_01`–`Actor_24` hierarchy, ignores duplicate archive copies, validates the expected 1,440 unique speech clips, creates an actor-disjoint split, and generates synthetic training views transiently.

Included manifests:

- `manifests/ravdess_actor_split.csv` — source clip, actor, label, split, and SHA-1
- `manifests/synthetic_augmentation_manifest.csv` — 2,880 deterministic synthetic training recipes

No evaluation clip is synthetically augmented.
