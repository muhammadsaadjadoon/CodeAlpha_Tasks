from pathlib import Path

import numpy as np

from app.ml.champion import InflectChampion


def test_bundled_champion_returns_calibrated_distribution():
    model_dir = Path(__file__).resolve().parents[2] / "models" / "champion"
    model = InflectChampion(model_dir)
    sample_rate = 16_000
    time = np.arange(sample_rate * 2, dtype=np.float32) / sample_rate
    signal = (0.18 * np.sin(2 * np.pi * 220 * time)).astype(np.float32)
    output = model.predict(signal)

    assert output.probabilities.shape == (7,)
    assert np.isfinite(output.probabilities).all()
    assert np.all(output.probabilities >= 0)
    assert np.isclose(output.probabilities.sum(), 1.0, atol=1e-5)
    assert output.segments_analyzed == 1
