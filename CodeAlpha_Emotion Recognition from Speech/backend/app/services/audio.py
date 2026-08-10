from pathlib import Path
import librosa
import numpy as np

TARGET_SAMPLE_RATE = 16000
MIN_SECONDS = 0.6
MAX_SECONDS = 30.0


class AudioValidationError(ValueError):
    pass


def load_and_normalize(path: Path) -> tuple[np.ndarray, int, float]:
    try:
        signal, sample_rate = librosa.load(path, sr=None, mono=True)
    except Exception as exc:
        raise AudioValidationError("The audio file could not be decoded. Confirm FFmpeg is installed for compressed formats.") from exc
    if signal.size == 0 or not np.isfinite(signal).all():
        raise AudioValidationError("The audio file contains no usable signal.")
    duration = signal.shape[0] / sample_rate
    if duration < MIN_SECONDS:
        raise AudioValidationError(f"Record at least {MIN_SECONDS:.1f} seconds of speech.")
    if duration > MAX_SECONDS:
        raise AudioValidationError(f"Audio must be {MAX_SECONDS:.0f} seconds or shorter.")
    if sample_rate != TARGET_SAMPLE_RATE:
        signal = librosa.resample(signal, orig_sr=sample_rate, target_sr=TARGET_SAMPLE_RATE)
        sample_rate = TARGET_SAMPLE_RATE
    peak = float(np.max(np.abs(signal)))
    if peak > 0:
        signal = signal / max(peak, 1e-6)
    return signal.astype(np.float32), sample_rate, duration
