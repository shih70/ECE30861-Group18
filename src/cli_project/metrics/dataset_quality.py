"""
DOCTYPE: Dataset quality metric for Hugging Face models.
This module defines DatasetQualityMetric, which estimates the presence
and richness of associated datasets in a model repository. If one or
more datasets are declared in the metadata, it returns 1.0; else 0.0.
"""

from typing import Any
import time
from cli_project.core.entities import HFModel


class DatasetQualityMetric:
    def name(self) -> str:
        return "dataset_quality"

    def compute(self, model: HFModel) -> float:
        try:
            datasets = model.metadata.get("datasets", [])
            if isinstance(datasets, list) and len(datasets) > 0:
                return 1.0
        except Exception as e:
            print(f"[ERROR] DatasetQualityMetric.compute failed: {e}")
        return 0.0

    def score(self, model: HFModel) -> float:
        return self.compute(model)

    def score_latency(self, model: HFModel) -> dict[str, Any]:
        start = time.perf_counter()
        self.compute(model)
        end = time.perf_counter()
        return {"latency_ms": (end - start) * 1000}
