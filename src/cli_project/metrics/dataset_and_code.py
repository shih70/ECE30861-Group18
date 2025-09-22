"""
DOCTYPE: Dataset & Code availability metric (reproducibility & usability).
This module defines DatasetAndCodeMetric, which checks whether a model clearly
documents its training/benchmark datasets and provides runnable code (examples,
scripts, or notebooks). It aggregates two boolean sub-signals—dataset presence
and code presence—into a single score in [0,1] with equal weights (0.5 each).
It pulls evidence from EntitiesBundle (model/repo/dataset raw fields, file
lists, and README text harvested by adapters) and returns explanatory details.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from modelscore.entities.base import EntitiesBundle
from modelscore.metrics.base import Metric, MetricResult, clamp01
from modelscore.metrics.registry import register


# -----------------------
# Small heuristic helpers
# -----------------------

_DATASET_KEYWORDS = [
    r"\bdataset\b", r"\bdatasets\b",
    r"\btraining data\b", r"\btrain(?:ed)? on\b",
    r"\bevaluation data\b", r"\bbenchmark(?:s)?\b",
    r"\bdata source\b", r"\bcorpus\b",
]

_CODE_KEYWORDS = [
    r"\bexample(?:s)?\b", r"\busage\b", r"\bquickstart\b",
    r"\bhow to run\b", r"\brun the model\b",
    r"\btrain(?:ing)? script\b", r"\beval(?:uation)? script\b",
    r"\bnotebook\b", r"\bcolab\b",
]

_COMMON_CODE_FILES = {
    "train.py", "training.py", "finetune.py", "evaluate.py", "eval.py",
    "inference.py", "predict.py", "demo.py",
}
_COMMON_CODE_DIRS = {"examples", "scripts", "notebooks", "demo", "demos"}


def _truthy(raw: Optional[Dict[str, Any]], *keys: str) -> bool:
    """True if any key exists and is truthy (bool True or non-empty str/list/dict)."""
    if not raw:
        return False
    for k in keys:
        v = raw.get(k)
        if isinstance(v, bool) and v:
            return True
        if isinstance(v, (str, list, tuple, dict)) and len(v) > 0:
            return True
    return False


def _contains_keywords(text: str, patterns: Iterable[str]) -> bool:
    if not text:
        return False
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True
    return False


def _file_signals(file_list: Iterable[str] | None) -> Dict[str, bool]:
    """Look for common code files/dirs that imply runnable examples."""
    found_files = False
    found_dirs = False
    if file_list:
        lowered = [str(f).lower() for f in file_list if isinstance(f, str)]
        for f in lowered:
            base = f.split("/")[-1]
            if base in _COMMON_CODE_FILES:
                found_files = True
            parts = f.split("/")
            if any(part in _COMMON_CODE_DIRS for part in parts):
                found_dirs = True
            if found_files and found_dirs:
                break
    return {"example_files": found_files, "example_dirs": found_dirs}


# -----------------------
# Metric implementation
# -----------------------

@dataclass
class DatasetAndCodeMetric(Metric):
    """Binary-evidence metric: dataset mentioned + code available → higher score."""

    W_DATASET: float = 0.5
    W_CODE: float = 0.5

    @property
    def name(self) -> str:
        return "dataset_and_code_score"

    def compute(self, entities: EntitiesBundle) -> MetricResult:
        mraw: Dict[str, Any] | None = getattr(entities.model, "raw", None)
        rraw: Dict[str, Any] | None = getattr(entities.repo, "raw", None)
        draw: Dict[str, Any] | None = getattr(entities.dataset, "raw", None)

        # -----------------
        # Dataset evidence
        # -----------------
        # 1) An actual DatasetEntity exists
        has_dataset_entity = entities.dataset is not None

        # 2) Explicit adapter flags
        has_dataset_flags = (
            _truthy(mraw, "has_dataset_section", "dataset_names", "dataset_links") or
            _truthy(rraw, "has_dataset_section", "dataset_names", "dataset_links") or
            _truthy(draw, "name")  # dataset card has a name
        )

        # 3) README text mentions
        readme_text = ((mraw or {}).get("readme_text") or "") + "\n" + ((rraw or {}).get("readme_text") or "")
        mentions_dataset = _contains_keywords(readme_text, _DATASET_KEYWORDS)

        dataset_present = bool(has_dataset_entity or has_dataset_flags or mentions_dataset)

        # -------------
        # Code evidence
        # -------------
        # 1) Explicit adapter flags
        has_code_flags = (
            _truthy(mraw, "has_examples", "has_usage_snippet") or
            _truthy(rraw, "has_examples", "has_usage_snippet")
        )

        # 2) Files & directories that indicate runnable code
        model_files = (mraw or {}).get("files") or []
        repo_files = (rraw or {}).get("files") or []
        file_sig_m = _file_signals(model_files)
        file_sig_r = _file_signals(repo_files)

        # 3) README text mentions “examples/usage/quickstart/train/eval/notebook…”
        mentions_code = _contains_keywords(readme_text, _CODE_KEYWORDS)

        code_present = bool(
            has_code_flags or
            file_sig_m["example_files"] or file_sig_m["example_dirs"] or
            file_sig_r["example_files"] or file_sig_r["example_dirs"] or
            mentions_code
        )

        # -----------------
        # Aggregate score
        # -----------------
        score = clamp01(
            self.W_DATASET * (1.0 if dataset_present else 0.0) +
            self.W_CODE    * (1.0 if code_present else 0.0)
        )

        details: Dict[str, Any] = {
            "dataset_present": dataset_present,
            "signals": {
                "has_dataset_entity": has_dataset_entity,
                "has_dataset_flags": has_dataset_flags,
                "mentions_dataset": mentions_dataset,
            },
            "code_present": code_present,
            "code_signals": {
                "has_code_flags": has_code_flags,
                "file_signals_model": file_sig_m,
                "file_signals_repo": file_sig_r,
                "mentions_code": mentions_code,
            },
        }

        return MetricResult(
            name=self.name,
            value=score,
            details=details,
            latency_ms=0,  # runner fills in
        )


# Register on import
register(DatasetAndCodeMetric())
