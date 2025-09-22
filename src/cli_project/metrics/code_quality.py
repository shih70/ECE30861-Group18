"""
DOCTYPE: Code Quality metric for maintainability hygiene.
This module defines CodeQualityMetric, which evaluates five lightweight quality
signals and sums them into a [0,1] score (+0.20 each):
(1) linter/config present, (2) type hints detected, (3) tests present,
(4) CI workflows present, (5) any docstrings present (module/class/function).
Signals are derived from repository structure and AST parsing. The metric
includes a per-flag breakdown to support quick remediation.
"""

from __future__ import annotations
from pathlib import Path
import ast, time

LINTER_FILES = [".flake8",".ruff.toml",".pylintrc","setup.cfg","pyproject.toml"]

def _txt(p: Path) -> str:
    try: return p.read_text(encoding="utf-8", errors="ignore")
    except Exception: return ""

def _has_linter(repo: Path) -> bool:
    return any((repo/f).exists() for f in LINTER_FILES)

def _has_type_hints(repo: Path) -> bool:
    for py in repo.rglob("*.py"):
        try:
            mod = ast.parse(_txt(py))
        except Exception:
            continue
        for node in ast.walk(mod):
            if isinstance(node,(ast.AnnAssign, ast.arg)) and getattr(node,"annotation",None): return True
            if isinstance(node, ast.FunctionDef) and node.returns: return True
    return False

def _has_tests(repo: Path) -> bool:
    return any((repo/n).exists() for n in ("tests","test","pytest.ini"))

def _has_ci(repo: Path) -> bool:
    wf = repo / ".github" / "workflows"
    return wf.exists() and any(wf.glob("*.yml"))

def _has_any_docstring(repo: Path) -> bool:
    for py in repo.rglob("*.py"):
        try:
            mod = ast.parse(_txt(py))
        except Exception:
            continue
        for node in (n for n in ast.walk(mod) if isinstance(n,(ast.Module,ast.ClassDef,ast.FunctionDef))):
            if ast.get_docstring(node): return True
    return False

def evaluate(repo: Path) -> tuple[float, int]:
    t0 = time.time()
    flags = {
        "linter": _has_linter(repo),
        "type_hints": _has_type_hints(repo),
        "tests": _has_tests(repo),
        "ci": _has_ci(repo),
        "docstrings": _has_any_docstring(repo),  # binary presence (rubric)
    }
    score = min(1.0, sum(flags.values()) * 0.20)
    return score, int((time.time() - t0) * 1000)
