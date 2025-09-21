from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union, Any
from cli_project.urls.base import HFModelURL
from cli_project.metrics.base import Metrics
from urllib.parse import urlparse


@dataclass
class HFModel():
    model_url: HFModelURL
    metrics: Metrics = field(default_factory=Metrics)

    def __init__(self, model_url: HFModelURL,
                 metrics: Metrics | None = None):
        self.model_url = model_url
        self.metrics = metrics or Metrics()

    ## Helper function
    def extract_model_name(self) -> str:
        """Extract the short model name from the HF URL."""
        parts: list[str] = urlparse(self.model_url.url).path.strip("/").split("/")
        if "tree" in parts:
            idx = parts.index("tree")
            if idx > 0:
                return parts[idx - 1]
        return parts[-1] if parts else self.model_url.url

    def to_record(self) -> dict[str, Any]:
        """Return NDJSON-ready dict (with metrics only)."""
        return {
            "name": self.extract_model_name(),
            "category": "MODEL",
            **self.metrics.to_dict(),
        }
