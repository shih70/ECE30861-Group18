from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union, Any


# -------------------
# Base + Subclasses
# -------------------

@dataclass
class UrlItem:
    """Abstract base representation of a URL (category + raw string)."""
    url: str
    category: str


@dataclass
class HFDatasetURL(UrlItem):
    def __init__(self, url: str):
        super().__init__(url, "DATASET")


@dataclass
class CodeRepoURL(UrlItem):
    def __init__(self, url: str):
        super().__init__(url, "CODE")


@dataclass
class HFModelURL(UrlItem):
    datasets: List[HFDatasetURL] = field(default_factory=list)
    code: List[CodeRepoURL] = field(default_factory=list)

    def __init__(self, url: str, 
                 datasets: List[HFDatasetURL] | None = None, 
                 code: List[CodeRepoURL] | None = None):
        super().__init__(url, "MODEL")
        self.datasets = datasets or []
        self.code = code or []

    def to_record(self) -> dict[str, Any]:
        """Return NDJSON-ready dict (stubs for now)."""
        record = {
            "name": self.url,
            "category": self.category,
            "net_score": 0.0,
            "net_score_latency": 0,
            "ramp_up_time": 0.0,
            "ramp_up_time_latency": 0,
            "bus_factor": 0.0,
            "bus_factor_latency": 0,
            "performance_claims": 0.0,
            "performance_claims_latency": 0,
            "license": 0.0,
            "license_latency": 0,
            "size_score": {
                "raspberry_pi": 0.0,
                "jetson_nano": 0.0,
                "desktop_pc": 0.0,
                "aws_server": 0.0,
            },
            "size_score_latency": 0,
            "dataset_and_code_score": 0.0,
            "dataset_and_code_score_latency": 0,
            "dataset_quality": 0.0,
            "dataset_quality_latency": 0,
            "code_quality": 0.0,
            "code_quality_latency": 0,
        }
        if self.datasets:
            record["linked_datasets"] = [d.url for d in self.datasets]
        if self.code:
            record["linked_code"] = [c.url for c in self.code]
        return record


# -------------------
# Classifier
# -------------------

def classify_url(raw: str) -> Union[HFDatasetURL, CodeRepoURL, HFModelURL, UrlItem]:
    """Classify a raw URL string into a typed UrlItem subclass."""
    raw = raw.strip()

    if "huggingface.co/datasets" in raw:
        return HFDatasetURL(raw)
    elif "github.com" in raw:
        return CodeRepoURL(raw)
    elif "huggingface.co" in raw and "/tree/" in raw:
        return HFModelURL(raw)
    else:
        return UrlItem(raw, "UNKNOWN")

def parse_url_file(path: Path) -> List[HFModelURL]:
    """
    Parse a text file of URLs into HFModelURL objects.

    - Datasets and code URLs that appear before a model are linked to that model.
    - Only models are returned in the output list.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    dataset_urls: List[HFDatasetURL] = []
    code_urls: List[CodeRepoURL] = []
    models: List[HFModelURL] = []

    for raw in urls:
        item = classify_url(raw)

        if isinstance(item, HFDatasetURL):
            dataset_urls.append(item)

        elif isinstance(item, CodeRepoURL):
            code_urls.append(item)

        elif isinstance(item, HFModelURL):
            # attach datasets + code to this model
            item.datasets = dataset_urls
            item.code = code_urls
            models.append(item)

            # reset context for the next model
            dataset_urls, code_urls = [], []

        else:
            # ignore or log unknown URLs
            continue

    return models