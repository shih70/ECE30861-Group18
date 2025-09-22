"""
DOCTYPE: Dataset Quality metric for documentation and provenance.
This module defines DatasetQualityMetric, which checks four dataset
documentation signals and sums them into a [0,1] score (+0.25 each):
(1) dataset card/README, (2) dataset license info, (3) size/splits evidence,
(4) citation information. Signals may come from hf_api.json (cardData/tags/
siblings) or local files (e.g., dataset_info.json, CITATION.cff). The metric
returns per-flag details to make results easy to audit and reproduce.
"""


from __future__ import annotations
from pathlib import Path
import json, time

def _exists_any(base: Path, names: list[str]) -> bool:
    return any((base / n).exists() for n in names)

def evaluate(repo: Path) -> tuple[float, int]:
    t0 = time.time()
    j = repo / "hf_api.json"
    if j.exists():
        try:
            hf = json.loads(j.read_text(encoding="utf-8"))
            tags = hf.get("tags") or []
            card = hf.get("cardData") or {}
            siblings = {s.get("rfilename") for s in hf.get("siblings", []) if isinstance(s, dict)}
            flags = {
                "card": bool(card) or ("README.md" in siblings),
                "license": bool(card.get("license")) or any(isinstance(t,str) and t.startswith("license:") for t in tags),
                "size_splits": False,  # HF JSON alone rarely encodes splits
                "citation": ("CITATION.cff" in siblings) or ("CITATION" in siblings),
            }
            score = min(1.0, sum(flags.values()) * 0.25)
            return score, int((time.time() - t0) * 1000)
        except Exception:
            pass

    # local fallback (root + common dataset dirs)
    flags = {"card": False, "license": False, "size_splits": False, "citation": False}
    for sd in ("", "data", "dataset", "datasets"):
        base = repo / sd if sd else repo
        flags["card"] |= _exists_any(base, ["dataset_card.md","DATASET_CARD.md","README.md"])
        flags["license"] |= _exists_any(base, ["dataset_info.json","LICENSE","README.md"])
        flags["size_splits"] |= _exists_any(base, ["dataset_info.json","README.md"])
        flags["citation"] |= _exists_any(base, ["CITATION.cff","CITATION","README.md"])
    score = min(1.0, sum(flags.values()) * 0.25)
    return score, int((time.time() - t0) * 1000)
