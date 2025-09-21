from __future__ import annotations
import json
from typing import Any
from cli_project.urls.base import HFModelURL


class NDJSONEncoder:
    """Utility to convert HFModelURL objects into NDJSON lines."""

    @staticmethod
    def encode(model: HFModelURL) -> str:
        """Return one NDJSON line (JSON object string)."""
        record: dict[str, Any] = model.to_record()
        return json.dumps(record)

    @staticmethod
    def encode_all(models: list[HFModelURL]) -> str:
        """Return full NDJSON (one line per model)."""
        return "\n".join(NDJSONEncoder.encode(m) for m in models)
    
    @staticmethod
    def print_records(models: list[HFModelURL]) -> None:
        """ Print full NDJSON in stdout """
        print(NDJSONEncoder.encode_all(models))
