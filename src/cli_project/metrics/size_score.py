"""
DOCTYPE: SizeScoreMetric for model deployment suitability.

This metric estimates model size compatibility across four device types
(Raspberry Pi, Jetson Nano, Desktop PC, AWS Server) using size metadata
from Hugging Face (`size_mb`).

Each device has a defined size range; models score 1.0 if they fit, 0.0 otherwise.
Returns a score dictionary and latency in milliseconds.
"""

import time
from cli_project.metrics.base import Metric, MetricResult
from typing import Any

DEVICE_THRESHOLDS = {
    "raspberry_pi": (50, 200),
    "jetson_nano": (200, 800),
    "desktop_pc": (500, 2000),
    "aws_server": (1000, 5000),
}

class SizeScoreMetric(Metric):
    """
    Computes per-device size scores for model reusability,
    and reports latency of score computation.
    """
    def name(self) -> str:
        return "size_score"

    def compute(self, metadata: dict[str, Any]) -> MetricResult:
        t0 = time.time()
        size_mb = metadata["hf_metadata"].get("size_mb", 0)
        #print(f"[DEBUG] Model size: {size_mb} MB")  # <-- ADD THIS LINE
        scores = {}


        for device, (min_mb, max_mb) in DEVICE_THRESHOLDS.items():
            if size_mb <= min_mb:
                score = 1.0
            elif size_mb >= max_mb:
                score = 0.0
            else:
                score = 1.0 - (size_mb - min_mb) / (max_mb - min_mb)
        
            scores[device] = round(score, 3)
        latency = int((time.time() - t0) * 1000)
        return MetricResult(
            name=self.name,
            value=scores,
            details={"no": "details"},
            latency_ms=latency,
        )


