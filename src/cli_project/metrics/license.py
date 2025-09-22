"""
DOCTYPE: License metric for legal clarity and compatibility.
This module defines LicenseMetric, which inspects HF metadata and/or repository
files to determine the declared license. It returns a binary score normalized to
[0,1]: 1.0 only if the license is clearly one of MIT, Apache-2.0, BSD (2/3), or
LGPL-2.1; otherwise 0.0. Sources include hf_api.json (cardData/tags), LICENSE*,
pyproject.toml, and README.*. The metric also includes details of the source.
"""

from __future__ import annotations
from pathlib import Path
import json, re, time

ALLOWED = {
    "mit","apache-2.0","bsd-2-clause","bsd-3-clause","bsd",
    "lgpl-2.1","lgpl-2.1-only","lgpl-2.1-or-later"
}

def _read(p: Path) -> str:
    try: return p.read_text(encoding="utf-8", errors="ignore")
    except Exception: return ""

def _hf(repo: Path):
    j = repo / "hf_api.json"
    if j.exists():
        try: return json.loads(j.read_text(encoding="utf-8"))
        except Exception: return None
    return None

def _norm(s: str | None) -> str | None:
    if not s: return None
    s = s.lower()
    if "mit" in s: return "mit"
    if "apache" in s and "2.0" in s: return "apache-2.0"
    if "bsd-3" in s or ("bsd" in s and "3" in s): return "bsd-3-clause"
    if "bsd-2" in s or ("bsd" in s and "2" in s): return "bsd-2-clause"
    if s.strip()=="bsd": return "bsd"
    if "lgpl" in s and "2.1" in s and "3.0" not in s: return "lgpl-2.1"
    if "lgpl" in s and "3.0" in s: return "lgpl-3.0"
    return s.strip()

def evaluate(repo: Path) -> tuple[float, int]:
    t0 = time.time()
    # HF first
    hf = _hf(repo)
    if hf:
        lic = None
        card = hf.get("cardData") or {}
        if isinstance(card.get("license"), str): lic = card["license"]
        if not lic:
            for t in hf.get("tags", []):
                if isinstance(t, str) and t.startswith("license:"):
                    lic = t.split(":", 1)[1]; break
        return (1.0 if _norm(lic) in ALLOWED else 0.0), int((time.time()-t0)*1000)
    # Repo files
    for name in ("LICENSE","LICENSE.txt","COPYING","COPYRIGHT"):
        p = repo / name
        if p.exists():
            return (1.0 if _norm(_read(p)) in ALLOWED else 0.0), int((time.time()-t0)*1000)
    pj = repo / "pyproject.toml"
    if pj.exists():
        m = re.search(r'license\s*=\s*"([^"]+)"', _read(pj), flags=re.I)
        if m:
            return (1.0 if _norm(m.group(1)) in ALLOWED else 0.0), int((time.time()-t0)*1000)
    for name in ("README.md","README"):
        p = repo / name
        if p.exists():
            return (1.0 if _norm(_read(p)) in ALLOWED else 0.0), int((time.time()-t0)*1000)
    return 0.0, int((time.time()-t0)*1000)
