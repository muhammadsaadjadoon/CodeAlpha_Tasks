import json
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"


def main() -> None:
    path = ARTIFACT_DIR / "metrics.json"
    if not path.exists():
        raise SystemExit("metrics.json not found. Train the models first.")
    report = json.loads(path.read_text(encoding="utf-8"))
    print(f"Selected: {report['selected_model']}")
    print("\nModel comparison:")
    for name, info in report["models"].items():
        holdout = info["holdout"]
        print(
            f"- {name:20s} CV AUC={info['cv_roc_auc']:.4f} | "
            f"Holdout AUC={holdout['roc_auc']:.4f} | F1={holdout['f1']:.4f} | Recall={holdout['recall']:.4f}"
        )
    calibrated = report["calibrated_holdout"]
    print(
        f"\nCalibrated selected model: AUC={calibrated['roc_auc']:.4f}, "
        f"Accuracy={calibrated['accuracy']:.4f}, F1={calibrated['f1']:.4f}, Brier={calibrated['brier']:.4f}"
    )


if __name__ == "__main__":
    main()
