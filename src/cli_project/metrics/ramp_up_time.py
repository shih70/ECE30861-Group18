"""
DOCTYPE: LLM-driven ramp-up time metric (deterministic, cached).
This module defines RampUpTimeMetric, which uses an injected LLM client to read
model/repo documentation (README, install, quickstart, config hints) and rate
ramp-up readiness via a strict JSON rubric. It combines subscores into a single
[0,1] score, caches results by input hash, and returns details (subscores,
justification, cache info). Deterministic settings (temperature=0) are used for
reproducibility; a fake client can be injected in tests.
"""

from __future__ import annotations

import hashlib
import json
import os
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

from src.entities.base import EntitiesBundle
from src.metrics.base import Metric, MetricResult, clamp01
from src.metrics.registry import register


# -------------------------
# Provider-agnostic client
# -------------------------

class LLMClient(Protocol):
    """
    Minimal JSON-only completion protocol.

    Implementations MUST:
      - Return a JSON string matching the expected schema.
      - Be deterministic (temperature=0).
      - Enforce a sensible timeout.

    Example signature for an OpenAI-like client:
      def complete_json(self, *, system: str, user: str, model: str,
                        temperature: float, max_output_tokens: int,
                        timeout_s: int) -> str: ...
    """
    def complete_json(
        self,
        *,
        system: str,
        user: str,
        model: str,
        temperature: float,
        max_output_tokens: int,
        timeout_s: int,
    ) -> str:
        ...


# -------------------------
# Metric implementation
# -------------------------

@dataclass
class RampUpTimeMetric(Metric):
    """LLM-scored ramp-up time based on documentation quality."""

    # LLM settings (tune in config/tests as needed)
    model_name: str = "gpt-4.1-mini"         # placeholder; your client decides
    temperature: float = 0.0                 # determinism for grading
    max_output_tokens: int = 300
    timeout_s: int = 30

    # Subscore weights (sum to 1.0)
    W_DOC: float = 0.25
    W_INSTALL: float = 0.20
    W_QUICK: float = 0.25
    W_CONFIG: float = 0.15
    W_TROUBLE: float = 0.15

    # Optional DI: pass a real/fake client at construction; None means disabled.
    client: Optional[LLMClient] = None

    # Cache directory
    cache_dir: Path = Path(".cache") / "ramp_llm"

    @property
    def name(self) -> str:
        return "ramp_up_time"

    # ---------- public entry ----------

    def compute(self, entities: EntitiesBundle) -> MetricResult:
        # 1) Gather text inputs from entities (adapters should fill these keys in .raw)
        doc = self._compose_input_doc(entities)
        if not doc.strip():
            return MetricResult(
                name=self.name,
                value=0.0,
                details={"reason": "no_docs_available"},
                latency_ms=0,
            )

        # 2) Cache lookup (content hash)
        content_hash = hashlib.sha256(doc.encode("utf-8")).hexdigest()
        cache_hit, cached = self._try_read_cache(content_hash)
        if cache_hit and cached is not None:
            score, details = self._score_from_llm_json(cached, content_hash, cached=True)
            return MetricResult(name=self.name, value=score, details=details, latency_ms=0)

        # 3) Call LLM (if client is not provided, fail gracefully)
        if self.client is None:
            return MetricResult(
                name=self.name,
                value=0.0,
                details={
                    "reason": "llm_client_not_configured",
                    "input_hash": content_hash,
                },
                latency_ms=0,
            )

        system_prompt, user_prompt = self._build_prompts(doc)
        try:
            raw_json = self.client.complete_json(
                system=system_prompt,
                user=user_prompt,
                model=self.model_name,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
                timeout_s=self.timeout_s,
            )
        except Exception as e:
            return MetricResult(
                name=self.name,
                value=0.0,
                details={"reason": "llm_call_failed", "error": str(e)[:300]},
                latency_ms=0,
            )

        # 4) Parse + clamp + aggregate + cache
        score, details = self._score_from_llm_json(raw_json, content_hash, cached=False)
        self._write_cache(content_hash, raw_json)
        return MetricResult(name=self.name, value=score, details=details, latency_ms=0)

    # ---------- helpers: inputs ----------

    def _compose_input_doc(self, entities: EntitiesBundle) -> str:
        """Collect relevant doc sections from model/repo raw dicts with safe defaults."""
        def grab(raw: Optional[Dict[str, Any]], key: str) -> str:
            v = (raw or {}).get(key)
            if isinstance(v, str):
                return v
            if isinstance(v, list):
                return "\n".join(str(x) for x in v if x)
            return ""
        mraw: Dict[str, Any] | None = getattr(entities.model, "raw", None)
        rraw: Dict[str, Any] | None = getattr(entities.repo, "raw", None)

        parts = []
        # Prefer explicit readme_text if present; else fall back to heuristic fields
        parts.append("# README (model)\n" + grab(mraw, "readme_text"))
        parts.append("# README (repo)\n" + grab(rraw, "readme_text"))

        # Common sections (either source may supply)
        parts.append("# Quickstart\n" + (grab(mraw, "quickstart") or grab(rraw, "quickstart")))
        parts.append("# Install\n" + (grab(mraw, "install_cmds") or grab(rraw, "install_cmds")))
        parts.append("# Usage\n" + (grab(mraw, "usage_snippets") or grab(rraw, "usage_snippets")))

        # Config hints (filenames or snippets can help)
        files_joined = "\n".join(
            str(x).lower() for x in (mraw or {}).get("files", []) + (rraw or {}).get("files", [])
            if isinstance(x, str)
        )
        parts.append("# Config files\n" + files_joined)

        # Light trimming and length limit (prevent huge prompts)
        doc = "\n\n".join(p for p in parts if p.strip())
        if len(doc) > 200_000:  # ~200KB text safety cap
            doc = doc[:200_000]
        return doc

    def _build_prompts(self, doc: str) -> tuple[str, str]:
        """Return (system, user) prompts for deterministic JSON scoring."""
        system = (
            "You are a strict, deterministic software engineering rater. "
            "Rate ramp-up readiness based ONLY on the provided text. "
            "Output STRICT JSON matching the schema, with numbers in [0,1]. "
            "No explanations outside JSON."
        )
        user = textwrap.dedent(f"""
        Read the documentation excerpts below and rate a model’s ramp-up time.

        Return ONLY this JSON object (no extra text):
        {{
          "doc_completeness": 0.0-1.0,
          "installability": 0.0-1.0,
          "quickstart": 0.0-1.0,
          "config_clarity": 0.0-1.0,
          "troubleshooting": 0.0-1.0,
          "justification": "1-4 short bullet points"
        }}

        Guidance:
        - doc_completeness: headings, structure, prerequisites, links.
        - installability: clear pip/conda commands, deps, env notes.
        - quickstart: copy-paste example likely to run.
        - config_clarity: presence and explanation of config files/params.
        - troubleshooting: FAQs, known issues, error hints.

        Documentation:
        {doc}
        """).strip()
        return system, user

    # ---------- helpers: cache ----------

    def _cache_path(self, content_hash: str) -> Path:
        return self.cache_dir / f"{content_hash}.json"

    def _try_read_cache(self, content_hash: str) -> tuple[bool, Optional[str]]:
        try:
            path = self._cache_path(content_hash)
            if path.exists():
                return True, path.read_text(encoding="utf-8")
            return False, None
        except Exception:
            return False, None

    def _write_cache(self, content_hash: str, payload: str) -> None:
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache_path(content_hash).write_text(payload, encoding="utf-8")
        except Exception:
            # Cache failures are non-fatal
            pass

    # ---------- helpers: scoring ----------

    def _score_from_llm_json(self, raw_json: str, content_hash: str, *, cached: bool) -> tuple[float, Dict[str, Any]]:
        """
        Parse the LLM JSON, clamp sub-scores, compute weighted aggregate.
        Returns (score, details).
        """
        try:
            data = json.loads(raw_json)
        except Exception as e:
            return 0.0, {
                "reason": "llm_json_parse_error",
                "error": str(e)[:200],
                "input_hash": content_hash,
                "cached": cached,
                "llm_model": self.model_name,
            }

        # Extract & clamp each expected subscore
        doc_c = clamp01(_to_float(data.get("doc_completeness", 0.0)))
        inst  = clamp01(_to_float(data.get("installability", 0.0)))
        quick = clamp01(_to_float(data.get("quickstart", 0.0)))
        conf  = clamp01(_to_float(data.get("config_clarity", 0.0)))
        trbl  = clamp01(_to_float(data.get("troubleshooting", 0.0)))

        # Weighted sum
        score = clamp01(
            self.W_DOC * doc_c +
            self.W_INSTALL * inst +
            self.W_QUICK * quick +
            self.W_CONFIG * conf +
            self.W_TROUBLE * trbl
        )

        details: Dict[str, Any] = {
            "doc_completeness": doc_c,
            "installability": inst,
            "quickstart": quick,
            "config_clarity": conf,
            "troubleshooting": trbl,
            "justification": (data.get("justification") or "")[:500],
            "llm_model": self.model_name,
            "cached": cached,
            "input_hash": content_hash,
        }
        return score, details


def _to_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0


# Auto-register metric on import
register(RampUpTimeMetric())
