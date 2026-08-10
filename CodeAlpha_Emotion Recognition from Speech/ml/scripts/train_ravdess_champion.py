from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torchaudio
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, log_loss, recall_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

LABELS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
LABEL_TO_ID = {label: index for index, label in enumerate(LABELS)}
RAVDESS_LABELS = {
    "01": "neutral",
    "02": "neutral",  # calm is harmonized into INFLECT's neutral class
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fear",
    "07": "disgust",
    "08": "surprise",
}
SAMPLE_RATE = 16_000
CLIP_SECONDS = 4.0
CLIP_SAMPLES = int(SAMPLE_RATE * CLIP_SECONDS)
SEED = 20_260_804


@dataclass(frozen=True)
class Record:
    path: Path
    relative_path: str
    actor_id: int
    label: str
    split: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the portable INFLECT RAVDESS champion.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--ravdess-root", type=Path, help="Extracted RAVDESS folder containing Actor_01 ... Actor_24.")
    source.add_argument("--archive", type=Path, help="Kaggle RAVDESS ZIP archive.")
    parser.add_argument("--output", type=Path, default=Path("models/champion"))
    parser.add_argument("--manifest-dir", type=Path, default=Path("data/manifests"))
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def locate_actor_root(root: Path) -> Path:
    candidates = [root]
    candidates.extend(path for path in root.rglob("Actor_01") if path.is_dir())
    for candidate in candidates:
        base = candidate.parent if candidate.name == "Actor_01" else candidate
        if all((base / f"Actor_{actor:02d}").is_dir() for actor in range(1, 25)):
            return base
    raise FileNotFoundError("Could not find a complete Actor_01 ... Actor_24 RAVDESS speech directory.")


def scan_records(root: Path) -> list[Record]:
    actor_root = locate_actor_root(root)
    records: list[Record] = []
    seen: set[tuple[int, str]] = set()
    for actor in range(1, 25):
        actor_dir = actor_root / f"Actor_{actor:02d}"
        split = "train" if actor <= 16 else "validation" if actor <= 20 else "test"
        for path in sorted(actor_dir.glob("*.wav")):
            parts = path.stem.split("-")
            if len(parts) < 7 or parts[2] not in RAVDESS_LABELS:
                continue
            key = (actor, path.name)
            if key in seen:
                continue
            seen.add(key)
            records.append(
                Record(
                    path=path,
                    relative_path=f"Actor_{actor:02d}/{path.name}",
                    actor_id=actor,
                    label=RAVDESS_LABELS[parts[2]],
                    split=split,
                )
            )
    if len(records) != 1440:
        raise RuntimeError(f"Expected 1,440 unique RAVDESS speech clips; found {len(records)}.")
    return records


def load_waveform(path: Path) -> torch.Tensor:
    waveform, sample_rate = torchaudio.load(str(path))
    waveform = waveform.mean(dim=0)
    if sample_rate != SAMPLE_RATE:
        waveform = torchaudio.functional.resample(waveform, sample_rate, SAMPLE_RATE)

    threshold = max(float(waveform.abs().max()) * 0.02, 1e-4)
    active = torch.where(waveform.abs() > threshold)[0]
    if active.numel() > 0:
        margin = SAMPLE_RATE // 10
        start = max(0, int(active[0]) - margin)
        end = min(waveform.numel(), int(active[-1]) + margin)
        waveform = waveform[start:end]

    if waveform.numel() > CLIP_SAMPLES:
        start = (waveform.numel() - CLIP_SAMPLES) // 2
        waveform = waveform[start : start + CLIP_SAMPLES]
    elif waveform.numel() < CLIP_SAMPLES:
        missing = CLIP_SAMPLES - waveform.numel()
        waveform = torch.nn.functional.pad(waveform, (missing // 2, missing - missing // 2))

    waveform = waveform / waveform.abs().max().clamp_min(1e-6)
    return waveform.to(torch.float16)


def colored_noise_like(waveforms: torch.Tensor) -> torch.Tensor:
    noise = torch.randn_like(waveforms)
    return torch.nn.functional.avg_pool1d(noise[:, None, :], kernel_size=7, stride=1, padding=3)[:, 0]


def normalize_batch(waveforms: torch.Tensor) -> torch.Tensor:
    return waveforms / waveforms.abs().amax(dim=-1, keepdim=True).clamp_min(1e-5)


def augment_batch(
    waveforms: torch.Tensor,
    labels: torch.Tensor,
    variant: int,
    source_waveforms: torch.Tensor,
    source_labels: torch.Tensor,
) -> torch.Tensor:
    output = waveforms.float().clone()
    batch_size, sample_count = output.shape
    output *= torch.empty(batch_size, 1).uniform_(0.65 if variant == 3 else 0.78, 1.30)
    output += torch.empty(batch_size, 1).uniform_(-0.004, 0.004)

    max_shift = {1: 1600, 2: 3200, 3: 4800}[variant]
    for index, shift in enumerate(torch.randint(-max_shift, max_shift + 1, (batch_size,)).tolist()):
        output[index] = torch.roll(output[index], shift)

    if variant == 1:
        noise = colored_noise_like(output)
        signal_rms = output.pow(2).mean(-1, keepdim=True).sqrt().clamp_min(1e-5)
        noise_rms = noise.pow(2).mean(-1, keepdim=True).sqrt().clamp_min(1e-5)
        snr = torch.empty(batch_size, 1).uniform_(20, 32)
        output += noise / noise_rms * signal_rms / (10 ** (snr / 20))

    elif variant == 2:
        wet = (
            output
            + torch.empty(batch_size, 1).uniform_(0.08, 0.20) * torch.roll(output, 480, dims=1)
            + torch.empty(batch_size, 1).uniform_(0.03, 0.10) * torch.roll(output, 1120, dims=1)
        )
        smooth = torch.nn.functional.avg_pool1d(wet[:, None, :], kernel_size=5, stride=1, padding=2)[:, 0]
        mix = torch.empty(batch_size, 1).uniform_(0.08, 0.24)
        output = (1 - mix) * output + mix * smooth
        noise = colored_noise_like(output)
        signal_rms = output.pow(2).mean(-1, keepdim=True).sqrt().clamp_min(1e-5)
        noise_rms = noise.pow(2).mean(-1, keepdim=True).sqrt().clamp_min(1e-5)
        snr = torch.empty(batch_size, 1).uniform_(18, 28)
        output += noise / noise_rms * signal_rms / (10 ** (snr / 20))

    else:
        partner_indices: list[int] = []
        for label in labels.tolist():
            candidates = torch.where(source_labels == label)[0]
            partner_indices.append(int(candidates[torch.randint(0, len(candidates), (1,))]))
        partner = source_waveforms[torch.tensor(partner_indices)].float()
        alpha = torch.empty(batch_size, 1).uniform_(0.08, 0.22)
        output = (1 - alpha) * output + alpha * partner

        pre_emphasized = torch.cat([output[:, :1], output[:, 1:] - 0.94 * output[:, :-1]], dim=1)
        smoothed = torch.nn.functional.avg_pool1d(output[:, None, :], kernel_size=5, stride=1, padding=2)[:, 0]
        selector = torch.rand(batch_size, 1)
        output = torch.where(selector < 0.5, 0.85 * output + 0.15 * pre_emphasized, 0.80 * output + 0.20 * smoothed)
        for index in range(batch_size):
            if random.random() < 0.65:
                width = random.randint(320, 1600)
                start = random.randint(0, sample_count - width)
                output[index, start : start + width] *= random.uniform(0.0, 0.35)

        noise = colored_noise_like(output)
        signal_rms = output.pow(2).mean(-1, keepdim=True).sqrt().clamp_min(1e-5)
        noise_rms = noise.pow(2).mean(-1, keepdim=True).sqrt().clamp_min(1e-5)
        snr = torch.empty(batch_size, 1).uniform_(16, 26)
        output += noise / noise_rms * signal_rms / (10 ** (snr / 20))

    return normalize_batch(output).clamp(-1, 1)


class FeatureExtractor:
    def __init__(self) -> None:
        self.mel = torchaudio.transforms.MelSpectrogram(
            sample_rate=SAMPLE_RATE,
            n_fft=512,
            win_length=400,
            hop_length=320,
            n_mels=64,
            f_min=20,
            f_max=7600,
            power=2.0,
        )
        self.to_db = torchaudio.transforms.AmplitudeToDB(stype="power", top_db=80)

    @torch.inference_mode()
    def __call__(self, waveforms: torch.Tensor) -> torch.Tensor:
        mel_db = self.to_db(self.mel(waveforms.float())).clamp(-80, 0) / 80.0
        delta = torchaudio.functional.compute_deltas(mel_db)
        delta_two = torchaudio.functional.compute_deltas(delta)
        statistics = [
            mel_db.mean(-1), mel_db.std(-1), mel_db.amax(-1), mel_db.amin(-1),
            torch.quantile(mel_db, 0.10, dim=-1), torch.quantile(mel_db, 0.25, dim=-1),
            torch.quantile(mel_db, 0.50, dim=-1), torch.quantile(mel_db, 0.75, dim=-1),
            torch.quantile(mel_db, 0.90, dim=-1), delta.mean(-1), delta.std(-1),
            delta_two.mean(-1), delta_two.std(-1),
        ]
        temporal_pool = torch.nn.functional.adaptive_avg_pool1d(mel_db, 8).flatten(1)
        delta_pool = torch.nn.functional.adaptive_avg_pool1d(delta, 4).flatten(1)
        root_mean_square = waveforms.float().pow(2).mean(-1, keepdim=True).sqrt()
        zero_crossing = ((waveforms[:, 1:] * waveforms[:, :-1]) < 0).float().mean(-1, keepdim=True)
        peak = waveforms.abs().amax(-1, keepdim=True)
        mean = waveforms.float().mean(-1, keepdim=True)
        standard_deviation = waveforms.float().std(-1, keepdim=True)
        crest_factor = peak / (root_mean_square + 1e-6)
        return torch.cat(
            statistics + [temporal_pool, delta_pool, root_mean_square, zero_crossing, peak, mean, standard_deviation, crest_factor],
            dim=1,
        )


def build_feature_set(
    indices: np.ndarray,
    waveforms: torch.Tensor,
    labels: torch.Tensor,
    extractor: FeatureExtractor,
    variant: int = 0,
    batch_size: int = 64,
) -> tuple[np.ndarray, np.ndarray]:
    features: list[torch.Tensor] = []
    targets: list[torch.Tensor] = []
    source_indices = torch.as_tensor(indices, dtype=torch.long)
    source_waveforms = waveforms[source_indices]
    source_labels = labels[source_indices]
    for start in range(0, len(indices), batch_size):
        batch_indices = torch.as_tensor(indices[start : start + batch_size], dtype=torch.long)
        batch = waveforms[batch_indices]
        target = labels[batch_indices]
        if variant:
            batch = augment_batch(batch, target, variant, source_waveforms, source_labels)
        features.append(extractor(batch).cpu())
        targets.append(target.cpu())
    return torch.cat(features).numpy().astype(np.float32), torch.cat(targets).numpy().astype(np.int64)


def export_svc(name: str, scaler: StandardScaler, pca: PCA, model: SVC, output: Path) -> None:
    np.savez_compressed(
        output / f"{name}_preprocess.npz",
        scaler_mean=scaler.mean_.astype(np.float32),
        scaler_scale=scaler.scale_.astype(np.float32),
        pca_mean=pca.mean_.astype(np.float32),
        pca_components=pca.components_.astype(np.float32),
    )
    np.savez_compressed(
        output / f"{name}_svm.npz",
        support_vectors=model.support_vectors_.astype(np.float32),
        dual_coef=model.dual_coef_.astype(np.float32),
        intercept=model.intercept_.astype(np.float32),
        n_support=model.n_support_.astype(np.int32),
        probA=model.probA_.astype(np.float32),
        probB=model.probB_.astype(np.float32),
        classes=model.classes_.astype(np.int32),
        gamma=np.asarray([model._gamma], dtype=np.float32),
    )


def calculate_metrics(targets: np.ndarray, probabilities: np.ndarray) -> dict:
    predictions = probabilities.argmax(axis=1)
    return {
        "accuracy": float(accuracy_score(targets, predictions)),
        "macro_f1": float(f1_score(targets, predictions, average="macro")),
        "uar": float(recall_score(targets, predictions, average="macro")),
        "nll": float(log_loss(targets, probabilities, labels=np.arange(len(LABELS)))),
        "classification_report": classification_report(
            targets, predictions, target_names=LABELS, output_dict=True, zero_division=0
        ),
        "confusion_matrix": confusion_matrix(targets, predictions).tolist(),
    }


def write_manifests(records: list[Record], manifest_dir: Path, seed: int) -> None:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    source_fields = ["relative_path", "actor_id", "label", "split", "source", "source_sha1"]
    with (manifest_dir / "ravdess_actor_split.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=source_fields)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "relative_path": record.relative_path,
                    "actor_id": f"{record.actor_id:02d}",
                    "label": record.label,
                    "split": record.split,
                    "source": "RAVDESS",
                    "source_sha1": hashlib.sha1(record.path.read_bytes()).hexdigest(),
                }
            )

    recipes = {
        1: "gain_shift_colored_noise",
        2: "room_echo_smoothing_noise",
        3: "same_emotion_blend_spectral_tilt_dropout",
    }
    synthetic_fields = ["synthetic_id", "source_relative_path", "actor_id", "label", "split", "variant", "recipe", "seed"]
    with (manifest_dir / "synthetic_augmentation_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=synthetic_fields)
        writer.writeheader()
        for record in records:
            if record.split != "train":
                continue
            for variant, recipe in recipes.items():
                writer.writerow(
                    {
                        "synthetic_id": f"{record.actor_id:02d}_{record.path.stem}_aug{variant}",
                        "source_relative_path": record.relative_path,
                        "actor_id": f"{record.actor_id:02d}",
                        "label": record.label,
                        "split": "train",
                        "variant": variant,
                        "recipe": recipe,
                        "seed": seed + variant,
                    }
                )


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(max(1, min(8, torch.get_num_threads())))

    with tempfile.TemporaryDirectory(prefix="inflect-ravdess-") as temporary_directory:
        if args.archive:
            with zipfile.ZipFile(args.archive) as archive:
                archive.extractall(temporary_directory)
            data_root = Path(temporary_directory)
        else:
            data_root = args.ravdess_root

        records = scan_records(data_root)
        write_manifests(records, args.manifest_dir, args.seed)
        waveforms = torch.stack([load_waveform(record.path) for record in records])
        labels = torch.tensor([LABEL_TO_ID[record.label] for record in records], dtype=torch.long)
        actors = np.asarray([record.actor_id for record in records])

        train_indices = np.where(actors <= 16)[0]
        validation_indices = np.where((actors >= 17) & (actors <= 20))[0]
        test_indices = np.where(actors >= 21)[0]
        extractor = FeatureExtractor()

        train_features: list[np.ndarray] = []
        train_targets: list[np.ndarray] = []
        for variant in range(4):
            features, targets = build_feature_set(train_indices, waveforms, labels, extractor, variant)
            train_features.append(features)
            train_targets.append(targets)
        x_train = np.concatenate(train_features)
        y_train = np.concatenate(train_targets)
        x_validation, y_validation = build_feature_set(validation_indices, waveforms, labels, extractor)
        x_test, y_test = build_feature_set(test_indices, waveforms, labels, extractor)

        args.output.mkdir(parents=True, exist_ok=True)
        configs = [("svc_a", 256, 2.0), ("svc_b", 384, 5.0)]
        validation_probabilities: list[np.ndarray] = []
        test_probabilities: list[np.ndarray] = []

        for name, components, regularization in configs:
            scaler = StandardScaler()
            standardized_train = scaler.fit_transform(x_train).astype(np.float32)
            standardized_validation = scaler.transform(x_validation).astype(np.float32)
            standardized_test = scaler.transform(x_test).astype(np.float32)
            pca = PCA(n_components=components, svd_solver="randomized", random_state=args.seed)
            projected_train = pca.fit_transform(standardized_train).astype(np.float32)
            projected_validation = pca.transform(standardized_validation).astype(np.float32)
            projected_test = pca.transform(standardized_test).astype(np.float32)
            model = SVC(
                C=regularization,
                kernel="rbf",
                gamma="scale",
                class_weight="balanced",
                probability=True,
                decision_function_shape="ovr",
                cache_size=2500,
                random_state=args.seed,
            )
            model.fit(projected_train, y_train)
            validation_probabilities.append(model.predict_proba(projected_validation))
            test_probabilities.append(model.predict_proba(projected_test))
            export_svc(name, scaler, pca, model, args.output)

        best_weight = 0.5
        best_f1 = -1.0
        for candidate in np.linspace(0, 1, 101):
            probabilities = candidate * validation_probabilities[0] + (1 - candidate) * validation_probabilities[1]
            score = f1_score(y_validation, probabilities.argmax(axis=1), average="macro")
            if score > best_f1:
                best_f1 = score
                best_weight = float(candidate)

        validation_ensemble = best_weight * validation_probabilities[0] + (1 - best_weight) * validation_probabilities[1]
        test_ensemble = best_weight * test_probabilities[0] + (1 - best_weight) * test_probabilities[1]
        best_temperature = 1.0
        best_nll = float("inf")
        for temperature in np.linspace(0.65, 1.75, 111):
            logits = np.log(np.clip(validation_ensemble, 1e-8, 1.0)) / temperature
            logits -= logits.max(axis=1, keepdims=True)
            calibrated = np.exp(logits)
            calibrated /= calibrated.sum(axis=1, keepdims=True)
            candidate_nll = log_loss(y_validation, calibrated, labels=np.arange(len(LABELS)))
            if candidate_nll < best_nll:
                best_nll = candidate_nll
                best_temperature = float(temperature)

        def calibrate(probabilities: np.ndarray) -> np.ndarray:
            logits = np.log(np.clip(probabilities, 1e-8, 1.0)) / best_temperature
            logits -= logits.max(axis=1, keepdims=True)
            result = np.exp(logits)
            return result / result.sum(axis=1, keepdims=True)

        validation_ensemble = calibrate(validation_ensemble)
        test_ensemble = calibrate(test_ensemble)
        validation_metrics = calculate_metrics(y_validation, validation_ensemble)
        test_metrics = calculate_metrics(y_test, test_ensemble)

        metadata = {
            "name": "INFLECT RAVDESS Synthetic Acoustic Ensemble",
            "version": "1.0.0",
            "labels": LABELS,
            "sample_rate": SAMPLE_RATE,
            "clip_seconds": CLIP_SECONDS,
            "feature_dim": int(x_train.shape[1]),
            "ensemble_weight_svc_a": best_weight,
            "ensemble_weight_svc_b": 1.0 - best_weight,
            "temperature": best_temperature,
            "dataset": {
                "source": "RAVDESS speech-only archive",
                "unique_clips": len(records),
                "train_originals": len(train_indices),
                "validation_originals": len(validation_indices),
                "test_originals": len(test_indices),
                "synthetic_variants_per_train_clip": 3,
                "effective_training_examples": len(y_train),
                "speaker_disjoint": True,
                "train_actors": "01-16",
                "validation_actors": "17-20",
                "test_actors": "21-24",
                "calm_mapped_to": "neutral",
            },
            "augmentation": [
                "gain variation",
                "time shift",
                "colored noise with randomized SNR",
                "multi-tap room echo",
                "spectral smoothing and pre-emphasis",
                "same-emotion voice blending",
                "short temporal dropout",
            ],
            "models": [
                {"name": "svc_a", "pca": 256, "C": 2.0},
                {"name": "svc_b", "pca": 384, "C": 5.0},
            ],
            "metrics": {"validation": validation_metrics, "test": test_metrics},
            "limitations": "RAVDESS contains acted English speech in controlled conditions. This model is not a clinical or universal emotion measurement tool.",
        }
        (args.output / "model_config.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        (args.output / "metrics.json").write_text(
            json.dumps({"validation": validation_metrics, "test": test_metrics}, indent=2), encoding="utf-8"
        )

        matrix = np.asarray(test_metrics["confusion_matrix"])
        figure, axis = plt.subplots(figsize=(8, 7))
        axis.imshow(matrix)
        axis.set_xticks(range(len(LABELS)), labels=[label.title() for label in LABELS], rotation=35, ha="right")
        axis.set_yticks(range(len(LABELS)), labels=[label.title() for label in LABELS])
        axis.set_xlabel("Predicted emotion")
        axis.set_ylabel("True emotion")
        axis.set_title("INFLECT held-out RAVDESS test confusion matrix")
        for row in range(matrix.shape[0]):
            for column in range(matrix.shape[1]):
                axis.text(column, row, str(matrix[row, column]), ha="center", va="center")
        figure.tight_layout()
        figure.savefig(args.output / "confusion_matrix.png", dpi=180)
        plt.close(figure)

        print(json.dumps({"validation": validation_metrics, "test": test_metrics}, indent=2))
        print(f"Portable champion exported to {args.output.resolve()}")


if __name__ == "__main__":
    main()
