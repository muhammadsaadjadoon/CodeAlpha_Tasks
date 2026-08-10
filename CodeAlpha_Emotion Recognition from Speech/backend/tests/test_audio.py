import numpy as np
import soundfile as sf
from app.services.audio import load_and_normalize


def test_audio_normalization(tmp_path):
    path = tmp_path / "sample.wav"
    sr = 16000
    signal = np.sin(2 * np.pi * 220 * np.arange(sr) / sr).astype("float32")
    sf.write(path, signal, sr)
    normalized, out_sr, duration = load_and_normalize(path)
    assert out_sr == 16000
    assert 0.99 <= duration <= 1.01
    assert normalized.dtype == np.float32
