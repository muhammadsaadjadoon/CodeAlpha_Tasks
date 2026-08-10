import argparse
import json

from app.model_service import get_model_service
from app.schemas import HeartAssessment


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one HeartTrack prediction from the command line.")
    parser.add_argument("--json", required=True, help="JSON object containing the 13 model inputs")
    args = parser.parse_args()
    payload = HeartAssessment.model_validate(json.loads(args.json))
    print(get_model_service().predict(payload).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
