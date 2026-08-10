from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torchaudio


@dataclass(frozen=True)
class ChampionOutput:
    probabilities: np.ndarray
    segments_analyzed: int


class PortableSVC:
    """Version-independent RBF-SVC runtime exported from scikit-learn.

    The model is stored as plain NumPy arrays, so production inference does not
    depend on scikit-learn or Python pickle compatibility.
    """

    def __init__(self, preprocess_path: Path, svm_path: Path) -> None:
        with np.load(preprocess_path) as pre:
            self.scaler_mean = pre["scaler_mean"].astype(np.float32)
            self.scaler_scale = pre["scaler_scale"].astype(np.float32)
            self.pca_mean = pre["pca_mean"].astype(np.float32)
            self.pca_components = pre["pca_components"].astype(np.float32)

        with np.load(svm_path) as model:
            self.support_vectors = model["support_vectors"].astype(np.float32)
            self.dual_coef = model["dual_coef"].astype(np.float32)
            self.intercept = model["intercept"].astype(np.float32)
            self.n_support = model["n_support"].astype(np.int32)
            self.prob_a = model["probA"].astype(np.float32)
            self.prob_b = model["probB"].astype(np.float32)
            self.classes = model["classes"].astype(np.int32)
            self.gamma = float(model["gamma"][0])

        self.starts = np.concatenate(
            [np.array([0], dtype=np.int32), np.cumsum(self.n_support, dtype=np.int32)[:-1]]
        )

    def transform(self, features: np.ndarray) -> np.ndarray:
        standardized = (features - self.scaler_mean) / np.maximum(self.scaler_scale, 1e-8)
        return (standardized - self.pca_mean) @ self.pca_components.T

    @staticmethod
    def _sigmoid(decision: float, prob_a: float, prob_b: float) -> float:
        value = decision * prob_a + prob_b
        if value >= 0:
            exp_value = np.exp(-value)
            return float(exp_value / (1.0 + exp_value))
        exp_value = np.exp(value)
        return float(1.0 / (1.0 + exp_value))

    @staticmethod
    def _multiclass_probability(pairwise: np.ndarray) -> np.ndarray:
        """Wu-Lin-Weng pairwise coupling used by LIBSVM."""
        class_count = pairwise.shape[0]
        probabilities = np.full(class_count, 1.0 / class_count, dtype=np.float64)
        q_matrix = np.zeros((class_count, class_count), dtype=np.float64)

        for row in range(class_count):
            for column in range(row):
                q_matrix[row, row] += pairwise[column, row] ** 2
                q_matrix[row, column] = q_matrix[column, row]
            for column in range(row + 1, class_count):
                q_matrix[row, row] += pairwise[column, row] ** 2
                q_matrix[row, column] = -pairwise[column, row] * pairwise[row, column]

        tolerance = 0.005 / class_count
        max_iterations = max(100, class_count)
        for _ in range(max_iterations):
            q_times_p = q_matrix @ probabilities
            p_q_p = float(probabilities @ q_times_p)
            if np.max(np.abs(q_times_p - p_q_p)) < tolerance:
                break
            for index in range(class_count):
                denominator = q_matrix[index, index]
                if denominator <= 0:
                    continue
                difference = (-q_times_p[index] + p_q_p) / denominator
                probabilities[index] += difference
                scale = 1.0 + difference
                p_q_p = (p_q_p + difference * (difference * denominator + 2.0 * q_times_p[index])) / (
                    scale * scale
                )
                q_times_p = (q_times_p + difference * q_matrix[:, index]) / scale
                probabilities = probabilities / scale

        probabilities = np.clip(probabilities, 1e-12, None)
        return probabilities / probabilities.sum()

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        projected = self.transform(features.astype(np.float32))
        outputs: list[np.ndarray] = []
        class_count = len(self.classes)

        for sample in projected:
            squared_distance = np.sum((self.support_vectors - sample) ** 2, axis=1)
            kernel_values = np.exp(-self.gamma * squared_distance)
            pairwise = np.zeros((class_count, class_count), dtype=np.float64)
            pair_index = 0

            for first_class in range(class_count):
                first_start = int(self.starts[first_class])
                first_count = int(self.n_support[first_class])
                for second_class in range(first_class + 1, class_count):
                    second_start = int(self.starts[second_class])
                    second_count = int(self.n_support[second_class])

                    decision = float(
                        np.dot(
                            self.dual_coef[second_class - 1, first_start : first_start + first_count],
                            kernel_values[first_start : first_start + first_count],
                        )
                        + np.dot(
                            self.dual_coef[first_class, second_start : second_start + second_count],
                            kernel_values[second_start : second_start + second_count],
                        )
                        + self.intercept[pair_index]
                    )
                    first_probability = self._sigmoid(
                        decision,
                        float(self.prob_a[pair_index]),
                        float(self.prob_b[pair_index]),
                    )
                    first_probability = min(max(first_probability, 1e-7), 1.0 - 1e-7)
                    pairwise[first_class, second_class] = first_probability
                    pairwise[second_class, first_class] = 1.0 - first_probability
                    pair_index += 1

            outputs.append(self._multiclass_probability(pairwise))

        return np.stack(outputs).astype(np.float32)


class AcousticFeatureExtractor:
    def __init__(self, sample_rate: int = 16000, clip_seconds: float = 4.0) -> None:
        self.sample_rate = sample_rate
        self.clip_samples = int(sample_rate * clip_seconds)
        self.mel = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=512,
            win_length=400,
            hop_length=320,
            n_mels=64,
            f_min=20,
            f_max=7600,
            power=2.0,
        )
        self.to_db = torchaudio.transforms.AmplitudeToDB(stype="power", top_db=80)

    def _trim(self, waveform: torch.Tensor) -> torch.Tensor:
        if waveform.numel() == 0:
            return waveform
        threshold = max(float(waveform.abs().max()) * 0.02, 1e-4)
        active = torch.where(waveform.abs() > threshold)[0]
        if active.numel() == 0:
            return waveform
        margin = self.sample_rate // 10
        start = max(0, int(active[0]) - margin)
        end = min(waveform.numel(), int(active[-1]) + margin)
        return waveform[start:end]

    def _window_signal(self, signal: np.ndarray) -> torch.Tensor:
        waveform = torch.from_numpy(np.asarray(signal, dtype=np.float32)).flatten()
        waveform = self._trim(waveform)
        if waveform.numel() == 0:
            waveform = torch.zeros(self.clip_samples, dtype=torch.float32)

        peak = waveform.abs().max().clamp_min(1e-6)
        waveform = waveform / peak

        if waveform.numel() <= self.clip_samples:
            missing = self.clip_samples - waveform.numel()
            padded = torch.nn.functional.pad(waveform, (missing // 2, missing - missing // 2))
            return padded.unsqueeze(0)

        max_windows = 5
        possible_starts = np.linspace(0, waveform.numel() - self.clip_samples, num=max_windows)
        starts = sorted({int(round(value)) for value in possible_starts})
        return torch.stack([waveform[start : start + self.clip_samples] for start in starts])

    @torch.inference_mode()
    def extract(self, signal: np.ndarray) -> np.ndarray:
        waveforms = self._window_signal(signal)
        mel_db = self.to_db(self.mel(waveforms)).clamp(-80, 0) / 80.0
        delta = torchaudio.functional.compute_deltas(mel_db)
        delta_two = torchaudio.functional.compute_deltas(delta)

        statistics = [
            mel_db.mean(-1),
            mel_db.std(-1),
            mel_db.amax(-1),
            mel_db.amin(-1),
            torch.quantile(mel_db, 0.10, dim=-1),
            torch.quantile(mel_db, 0.25, dim=-1),
            torch.quantile(mel_db, 0.50, dim=-1),
            torch.quantile(mel_db, 0.75, dim=-1),
            torch.quantile(mel_db, 0.90, dim=-1),
            delta.mean(-1),
            delta.std(-1),
            delta_two.mean(-1),
            delta_two.std(-1),
        ]
        temporal_pool = torch.nn.functional.adaptive_avg_pool1d(mel_db, 8).flatten(1)
        delta_pool = torch.nn.functional.adaptive_avg_pool1d(delta, 4).flatten(1)

        root_mean_square = waveforms.pow(2).mean(-1, keepdim=True).sqrt()
        zero_crossing = ((waveforms[:, 1:] * waveforms[:, :-1]) < 0).float().mean(-1, keepdim=True)
        peak = waveforms.abs().amax(-1, keepdim=True)
        mean = waveforms.mean(-1, keepdim=True)
        standard_deviation = waveforms.std(-1, keepdim=True)
        crest_factor = peak / (root_mean_square + 1e-6)

        features = torch.cat(
            statistics
            + [
                temporal_pool,
                delta_pool,
                root_mean_square,
                zero_crossing,
                peak,
                mean,
                standard_deviation,
                crest_factor,
            ],
            dim=1,
        )
        return features.cpu().numpy().astype(np.float32)


class InflectChampion:
    def __init__(self, model_dir: Path) -> None:
        self.model_dir = model_dir
        self.config = json.loads((model_dir / "model_config.json").read_text(encoding="utf-8"))
        self.labels = list(self.config["labels"])
        self.version = str(self.config["version"])
        self.temperature = float(self.config.get("temperature", 1.0))
        self.weight_a = float(self.config.get("ensemble_weight_svc_a", 0.5))
        self.weight_b = float(self.config.get("ensemble_weight_svc_b", 0.5))
        self.extractor = AcousticFeatureExtractor(
            sample_rate=int(self.config.get("sample_rate", 16000)),
            clip_seconds=float(self.config.get("clip_seconds", 4.0)),
        )
        self.model_a = PortableSVC(model_dir / "svc_a_preprocess.npz", model_dir / "svc_a_svm.npz")
        self.model_b = PortableSVC(model_dir / "svc_b_preprocess.npz", model_dir / "svc_b_svm.npz")

    def predict(self, signal: np.ndarray) -> ChampionOutput:
        features = self.extractor.extract(signal)
        probabilities_a = self.model_a.predict_proba(features)
        probabilities_b = self.model_b.predict_proba(features)
        probabilities = self.weight_a * probabilities_a + self.weight_b * probabilities_b

        logits = np.log(np.clip(probabilities, 1e-8, 1.0)) / max(self.temperature, 1e-6)
        logits -= logits.max(axis=1, keepdims=True)
        calibrated = np.exp(logits)
        calibrated /= calibrated.sum(axis=1, keepdims=True)

        aggregate = calibrated.mean(axis=0)
        aggregate /= aggregate.sum()
        return ChampionOutput(aggregate.astype(np.float32), int(features.shape[0]))
