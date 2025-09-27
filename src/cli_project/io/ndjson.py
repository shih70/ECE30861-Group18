import json
from typing import Any
from cli_project.core.entities import HFModel

class NDJSONEncoder:
    """Utility to convert HFModel objects (with results) into NDJSON lines."""

    @staticmethod
    def encode(model: HFModel) -> str:
        """Return one NDJSON line for a model + its metric results."""
        record: dict[str, Any] = {
            "name": model.name,
            "category": model.model_url.category,
        }

        for r in model.metric_scores.values():
            record[r.name] = r.value
            record[f"{r.name}_latency"] = r.latency_ms

        if "net_score" not in record and model.metric_scores:
            vals = [r.value for r in model.metric_scores.values() if isinstance(r.value, (int, float))]
            record["net_score"] = round(sum(vals) / len(vals), 2) if vals else 0.0
            record["net_score_latency"] = sum(r.latency_ms for r in model.metric_scores.values())

        return json.dumps(record)

    @staticmethod
    def encode_all(models: list[HFModel]) -> str:
        """Return full NDJSON (one line per model)."""
        return "\n".join(NDJSONEncoder.encode(m) for m in models)

    @staticmethod
    def print_records(models: list[HFModel]) -> None:
        print(NDJSONEncoder.encode_all(models))
