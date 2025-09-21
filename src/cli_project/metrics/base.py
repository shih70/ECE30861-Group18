from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Metrics:
    """All required scoring fields for a model (stubbed defaults)."""

    net_score: float = 0.0
    net_score_latency: int = 0

    ramp_up_time: float = 0.0
    ramp_up_time_latency: int = 0

    bus_factor: float = 0.0
    bus_factor_latency: int = 0

    performance_claims: float = 0.0
    performance_claims_latency: int = 0

    license: float = 0.0
    license_latency: int = 0

    size_score: Dict[str, float] = field(
        default_factory=lambda: {
            "raspberry_pi": 0.0,
            "jetson_nano": 0.0,
            "desktop_pc": 0.0,
            "aws_server": 0.0,
        }
    )
    size_score_latency: int = 0

    dataset_and_code_score: float = 0.0
    dataset_and_code_score_latency: int = 0

    dataset_quality: float = 0.0
    dataset_quality_latency: int = 0

    code_quality: float = 0.0
    code_quality_latency: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "net_score": self.net_score,
            "net_score_latency": self.net_score_latency,
            "ramp_up_time": self.ramp_up_time,
            "ramp_up_time_latency": self.ramp_up_time_latency,
            "bus_factor": self.bus_factor,
            "bus_factor_latency": self.bus_factor_latency,
            "performance_claims": self.performance_claims,
            "performance_claims_latency": self.performance_claims_latency,
            "license": self.license,
            "license_latency": self.license_latency,
            "size_score": self.size_score,
            "size_score_latency": self.size_score_latency,
            "dataset_and_code_score": self.dataset_and_code_score,
            "dataset_and_code_score_latency": self.dataset_and_code_score_latency,
            "dataset_quality": self.dataset_quality,
            "dataset_quality_latency": self.dataset_quality_latency,
            "code_quality": self.code_quality,
            "code_quality_latency": self.code_quality_latency,
        }
