"""
DOCTYPE: Size metric for artifact footprint across a cohort.
This module defines SizeMetric, which estimates the model/repo footprint and
normalizes it within [0,1] using cohort min–max scaling: the smallest artifact
scores 1.0 and the largest scores 0.0. Bytes may be inferred from HF metadata
(e.g., safetensors parameter count ≈ params*4) or from local repo file sizes.
If cohort bounds (min/max) are not provided, the metric returns a neutral 0.5.
The metric also includes details showing the estimated bytes and the bounds.
"""


from __future__ import annotations
from pathlib import Path
import json, os, time

# Provide cohort bounds via env or a json file.
#   ENV:  SIZE_MIN_BYTES, SIZE_MAX_BYTES
#   FILE: SIZE_BOUNDS_JSON=/abs/path/to/size_bounds.json  -> {"min": ..., "max": ...}

IGNORE = {".git",".venv","__pycache__",".mypy_cache",".pytest_cache","node_modules","build","dist"}

def _repo_bytes(repo: Path) -> int:
    total = 0
    for p in repo.rglob("*"):
        if any(part in IGNORE for part in p.parts): continue
        if p.is_file():
            try: total += p.stat().st_size
            except OSError: pass
    return total

def _hf_bytes(repo: Path) -> int | None:
    j = repo / "hf_api.json"
    if not j.exists(): return None
    try:
        hf = json.loads(j.read_text(encoding="utf-8"))
        params = hf.get("safetensors", {}).get("parameters", {}).get("F32")
        if isinstance(params, (int, float)):
            return int(params) * 4  # ~ FP32 bytes
    except Exception:
        pass
    return None

def _load_bounds() -> tuple[float, float] | None:
    if os.getenv("SIZE_MIN_BYTES") and os.getenv("SIZE_MAX_BYTES"):
        return float(os.getenv("SIZE_MIN_BYTES")), float(os.getenv("SIZE_MAX_BYTES"))
    b = os.getenv("SIZE_BOUNDS_JSON")
    if b and Path(b).exists():
        try:
            js = json.loads(Path(b).read_text(encoding="utf-8"))
            return float(js["min"]), float(js["max"])
        except Exception:
            return None
    return None

def evaluate(repo: Path) -> tuple[float, int]:
    t0 = time.time()
    size_b = _hf_bytes(repo)
    if size_b is None:
        size_b = _repo_bytes(repo)

    bounds = _load_bounds()
    if not bounds or bounds[1] <= bounds[0]:
        # rubric requires min–max across a set; if the set bounds are unknown,
        # return neutral 0.5 instead of a made-up heuristic.
        return 0.5, int((time.time() - t0) * 1000)

    mn, mx = bounds
    x = max(mn, min(mx, float(size_b)))
    t = (x - mn) / (mx - mn)   # largest -> 1
    score = 1.0 - t            # invert so smallest -> 1
    return round(score, 6), int((time.time() - t0) * 1000)
