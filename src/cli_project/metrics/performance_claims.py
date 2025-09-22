"""
DOCTYPE: Performance Claims metric for self-reported results.
This module defines PerformanceClaimsMetric, which scans the README/model card/
docs for author-reported metrics (e.g., accuracy, F1, BLEU, ROUGE, mAP,
precision/recall). It normalizes numeric values into [0,1] (percentages mapped
to 0–1) and returns their average; if no claims are found, the score is 0.0.
Because these are self-reported, this metric is lightly weighted elsewhere. The
metric also includes the extracted claims for transparency.
"""

from __future__ import annotations
from pathlib import Path
import re, time

NUM = re.compile(r"(accuracy|acc|f1|bleu|rouge|map|mAP|precision|recall)\s*[:=]\s*([0-9]*\.?[0-9]+)", re.I)

def _read(p: Path) -> str:
    try: return p.read_text(encoding="utf-8", errors="ignore")
    except Exception: return ""

def evaluate(repo: Path) -> tuple[float, int]:
    t0 = time.time()
    blob = ""
    for name in ("README.md","MODEL_CARD.md","report.md","docs/results.md"):
        p = repo / name
        if p.exists(): blob += _read(p) + "\n"
    vals = []
    for m in NUM.finditer(blob):
        v = float(m.group(2))
        if v <= 1.0: vals.append(v)
        elif v <= 100.0: vals.append(v/100.0)
    score = sum(vals)/len(vals) if vals else 0.0
    return score, int((time.time() - t0) * 1000)
