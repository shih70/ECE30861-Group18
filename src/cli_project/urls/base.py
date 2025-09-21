from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union, Any
from cli_project.metrics.base import Metrics
from urllib.parse import urlparse

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