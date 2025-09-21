"""
DOCTYPE: Bus Factor metric for repository sustainability.
This module defines BusFactorMetric, which inspects the number of unique recent
committers in the repository entity and estimates the project's resilience to
developer loss. It normalizes the committer count into [0,1] by dividing by 10
and capping at 1.0: a repo with ≥10 active committers scores 1.0, while 0
committers scores 0.0. The metric also includes details showing the raw count.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from modelscore.entities.base import EntitiesBundle
from modelscore.metrics.base import Metric, MetricResult, clamp01
from modelscore.metrics.registry import register


@dataclass
class BusFactorMetric(Metric):
    """Assess knowledge distribution in the repo via recent committer count."""

    @property
    def name(self) -> str:
        return "bus_factor"

    def compute(self, entities: EntitiesBundle) -> MetricResult:
        # Get raw number of recent committers from the RepoEntity
        n_committers = 0
        if entities.repo and entities.repo.recent_committers is not None:
            n_committers = entities.repo.recent_committers

        # Normalize: simple linear scale up to 10 contributors
        val = clamp01(n_committers / 10.0)

        details: Dict[str, int] = {"recent_committers": n_committers}

        return MetricResult(
            name=self.name,
            value=val,
            details=details,
            latency_ms=0,  # runner fills this in
        )


# Register on import
register(BusFactorMetric())
