from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
import numpy as np
import torch
from app.config import settings
from app.ml.labels import AROUSAL, LABELS, VALENCE
from app.ml.champion import InflectChampion


class ModelUnavailableError(RuntimeError):
    pass


@dataclass
class Prediction:
    primary_emotion: str
    confidence: float
    probabilities: dict[str, float]
    valence: float
    arousal: float
    model_version: str


def normalize_label(value: str) -> str:
    label = value.strip().lower().replace("_", " ").replace("-", " ")
    aliases = {
        "ang": "angry",
        "anger": "angry",
        "angry": "angry",
        "dis": "disgust",
        "disgusted": "disgust",
        "disgust": "disgust",
        "fea": "fear",
        "fearful": "fear",
        "fear": "fear",
        "hap": "happy",
        "happiness": "happy",
        "happy": "happy",
        "neu": "neutral",
        "neutrality": "neutral",
        "neutral": "neutral",
        "calm": "neutral",
        "calmness": "neutral",
        "sadness": "sad",
        "sad": "sad",
        "sur": "surprise",
        "surprised": "surprise",
        "surprise": "surprise",
        "excited": "happy",
        "frustrated": "angry",
    }
    return aliases.get(label, label)


class EmotionInferenceService:
    """Loads a trained local champion first and an optional research baseline second."""

    def __init__(self) -> None:
        self.model = None
        self.extractor = None
        self.local_champion: InflectChampion | None = None
        self.device = "cpu"
        self.version = "Not loaded"
        self.source = "none"
        self.state = "available" if settings.allow_remote_baseline else "unavailable"
        self.message = "A trained model will be prepared on the first analysis."
        self._load_lock = Lock()

    def _resolve_device(self) -> str:
        requested = settings.model_device
        if requested == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        if requested.startswith("cuda") and not torch.cuda.is_available():
            return "cpu"
        return requested

    def _load_from(self, source: str | Path, source_name: str) -> None:
        from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

        self.state = "loading"
        self.message = "Preparing the speech emotion model…"
        self.device = self._resolve_device()
        self.extractor = AutoFeatureExtractor.from_pretrained(source)
        self.model = AutoModelForAudioClassification.from_pretrained(source).to(self.device).eval()
        self.version = str(source)
        self.source = source_name
        self.state = "ready"
        self.message = "Speech emotion model ready."

    def load(self, allow_remote: bool = False) -> None:
        if self.local_champion is not None or (self.model is not None and self.extractor is not None):
            return
        with self._load_lock:
            if self.local_champion is not None or (self.model is not None and self.extractor is not None):
                return
            configured_dir = Path(settings.model_dir)
            backend_dir = Path(__file__).resolve().parents[2]
            model_dir = configured_dir if configured_dir.is_absolute() else (backend_dir / configured_dir).resolve()
            try:
                portable_files = [
                    model_dir / "model_config.json",
                    model_dir / "svc_a_preprocess.npz",
                    model_dir / "svc_a_svm.npz",
                    model_dir / "svc_b_preprocess.npz",
                    model_dir / "svc_b_svm.npz",
                ]
                if model_dir.exists() and all(path.exists() for path in portable_files):
                    self.state = "loading"
                    self.message = "Preparing the INFLECT acoustic ensemble…"
                    self.local_champion = InflectChampion(model_dir)
                    self.version = f"INFLECT {self.local_champion.version}"
                    self.source = "local trained champion"
                    self.device = "cpu"
                    self.state = "ready"
                    self.message = "INFLECT trained acoustic ensemble ready."
                    return
                if model_dir.exists() and (model_dir / "config.json").exists():
                    self._load_from(model_dir, "local transformer champion")
                    return
                if allow_remote and settings.allow_remote_baseline:
                    self._load_from(settings.remote_baseline_model, "remote research baseline")
                    return
                self.state = "available" if settings.allow_remote_baseline else "unavailable"
                self.message = (
                    "A baseline model is available and will be downloaded on the first analysis."
                    if settings.allow_remote_baseline
                    else "No trained model is installed. Export a champion model to models/champion."
                )
            except Exception as exc:
                self.model = None
                self.extractor = None
                self.state = "error"
                self.message = f"Model preparation failed: {exc}"

    def status(self) -> dict[str, str | bool]:
        return {
            "ready": self.local_champion is not None or (self.model is not None and self.extractor is not None),
            "state": self.state,
            "model_version": self.version,
            "source": self.source,
            "device": self.device,
            "message": self.message,
        }

    @torch.inference_mode()
    def predict(self, signal: np.ndarray, sample_rate: int) -> Prediction:
        if self.local_champion is None and (self.model is None or self.extractor is None):
            self.load(allow_remote=True)

        if self.local_champion is not None:
            if sample_rate != 16000:
                raise ModelUnavailableError("The local champion expects a 16 kHz normalized signal.")
            output = self.local_champion.predict(signal)
            mapped = {
                label: float(output.probabilities[index])
                for index, label in enumerate(self.local_champion.labels)
            }
            mapped = {label: mapped.get(label, 0.0) for label in LABELS}
            total = sum(mapped.values())
            mapped = {label: value / max(total, 1e-8) for label, value in mapped.items()}
            primary = max(mapped, key=mapped.get)
            valence = sum(mapped.get(label, 0.0) * VALENCE.get(label, 0.0) for label in mapped)
            arousal = sum(mapped.get(label, 0.0) * AROUSAL.get(label, 0.0) for label in mapped)
            return Prediction(primary, mapped[primary], mapped, valence, arousal, self.version)

        if self.model is None or self.extractor is None:
            raise ModelUnavailableError(
                self.message or "The emotion model is unavailable. Train or copy the champion model into models/champion."
            )

        batch = self.extractor(signal, sampling_rate=sample_rate, return_tensors="pt", padding=True)
        batch = {key: value.to(self.device) for key, value in batch.items()}
        logits = self.model(**batch).logits[0]
        probs = torch.softmax(logits, dim=-1).detach().cpu().numpy()

        raw_id2label = getattr(self.model.config, "id2label", {}) or {}
        mapped: dict[str, float] = {label: 0.0 for label in LABELS}
        for index, probability in enumerate(probs):
            raw_label = raw_id2label.get(index, raw_id2label.get(str(index), LABELS[index] if index < len(LABELS) else str(index)))
            label = normalize_label(str(raw_label))
            if label in mapped:
                mapped[label] += float(probability)

        total = sum(mapped.values())
        if total <= 0:
            fallback_count = min(len(probs), len(LABELS))
            mapped = {label: (float(probs[i]) if i < fallback_count else 0.0) for i, label in enumerate(LABELS)}
            total = sum(mapped.values())
        mapped = {label: value / max(total, 1e-8) for label, value in mapped.items()}

        primary = max(mapped, key=mapped.get)
        valence = sum(mapped.get(label, 0.0) * VALENCE.get(label, 0.0) for label in mapped)
        arousal = sum(mapped.get(label, 0.0) * AROUSAL.get(label, 0.0) for label in mapped)
        return Prediction(primary, mapped[primary], mapped, valence, arousal, self.version)


inference_service = EmotionInferenceService()
