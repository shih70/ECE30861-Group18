"""
DOCTYPE: Base interfaces and types for scoring metrics.
This module defines the abstract Metric interface that all concrete metrics must
implement (a `name` property and a `compute(EntitiesBundle) -> MetricResult`
method), the `MetricResult` dataclass that standardizes outputs (value, details,
latency_ms), and small helpers to keep metric values valid. Metric values are
floats in [0,1] for most metrics, or a {str -> float} map for `size_score`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional, Union

from core.entities import EntitiesBundle

# ---------------------------------------------------------------------------

MetricValue = Union[float, Mapping[str, float]]


@dataclass(frozen=True, slots=True)
class MetricResult:
    """
    Standard envelope returned by every metric.

    Attributes
    ----------
    name : str
        Short identifier for the metric (e.g., "license", "bus_factor").
    value : MetricValue
        Normalized float in [0,1], or a {str -> float} map for size_score.
    details : dict[str, Any]
        Optional, human/machine-readable context about how the score was computed.
        Keep this small and JSON-serializable.
    latency_ms : int
        Time to compute this metric in milliseconds. The runner typically measures
        and fills this; metrics may leave it as 0.
    """

    name: str
    value: MetricValue
    details: Dict[str, Any]
    latency_ms: int = 0

class Metric(ABC):
    """
    Abstract base class for all metrics.

    Implementors must provide:
      - `name` (property): a stable, Table-1-aligned identifier.
      - `compute(entities)`: returns a MetricResult with `value` normalized
        to [0,1] (or a validated size_score map), and a concise `details` dict.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The metric's stable identifier (e.g., 'license')."""
        raise NotImplementedError

    @abstractmethod
    def compute(self, entities: EntitiesBundle) -> MetricResult:
        """
        Compute this metric for the given entities.

        Notes for implementors:
        - Prefer pure logic: do not mutate `entities`.
        - Return normalized values; consider using the helpers below to clamp/validate.
        - Keep details lightweight and JSON-serializable.
        """
        raise NotImplementedError

# ---------------------------------------------------------------------------
# ----------------------Shared helpers for metrics---------------------------
# ---------------------------------------------------------------------------

def clamp01(x: float) -> float:
    """
    Clamp a float into [0,1]. Use this defensively at metric boundaries.
    """
    if x != x:  # NaN check without importing math
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)

def validate_size_score_map(m: Mapping[str, float]) -> Dict[str, float]:
    """
    Validate and normalize a size_score map ({device -> score in [0,1]}).

    - Ensures keys are strings.
    - Clamps all values to [0,1].
    - Returns a new plain dict (safe to JSON-serialize).
    """
    out: Dict[str, float] = {}
    for k, v in m.items():
        key = str(k)
        try:
            val = float(v)
        except (TypeError, ValueError):
            val = 0.0
        out[key] = clamp01(val)
    return out


__all__ = [
    "Metric",
    "MetricResult",
    "MetricValue",
    "clamp01",
    "validate_size_score_map",
]
