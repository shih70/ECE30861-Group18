import pytest
from cli_project.metrics.license import LicenseMetric
from cli_project.metrics.bus_factor import BusFactorMetric
from cli_project.metrics.ramp_up_time import RampUpTimeMetric
from cli_project.metrics.performance_claims import PerformanceClaimsMetric
from cli_project.metrics.base import MetricResult


def test_license_metric() -> None:
    metadata = {"license": "apache-2.0"}
    metric = LicenseMetric()
    result = metric.compute(metadata)
    assert isinstance(result, MetricResult)
    assert result.name == "license"
    assert result.value in (0.0, 1.0)
    assert "license" in result.details


def test_bus_factor_metric() -> None:
    metadata = {"recent_committers": 5}
    metric = BusFactorMetric()
    result = metric.compute(metadata)
    assert isinstance(result, MetricResult)
    assert result.name == "bus_factor"
    assert 0.0 <= result.value <= 1.0
    assert result.details["recent_committers"] == 5


def test_ramp_up_time_metric() -> None:
    metadata = {"repo_url": "https://huggingface.co/google-bert/bert-base-uncased"}
    metric = RampUpTimeMetric()
    result = metric.compute(metadata)
    assert isinstance(result, MetricResult)
    assert result.name == "ramp_up_time"
    assert 0.0 <= result.value <= 1.0
    assert isinstance(result.details, dict)


def test_performance_claims_metric() -> None:
    metadata = {"repo_url": "https://huggingface.co/google-bert/bert-base-uncased"}
    metric = PerformanceClaimsMetric()
    result = metric.compute(metadata)
    assert isinstance(result, MetricResult)
    assert result.name == "performance_claims"
    assert 0.0 <= result.value <= 1.0
    assert isinstance(result.details, dict)
