import pytest
from pathlib import Path
from typing import Any, Dict
from cli_project.metrics.code_quality import CodeQualityMetric
from cli_project.metrics.dataset_quality import DatasetQualityMetric
from cli_project.metrics.dataset_and_code import DatasetAndCodeMetric
from cli_project.metrics.base import MetricResult


# ----------------------------
# Fake metadata (matches your CLI structure)
# ----------------------------
FAKE_METADATA: Dict[str, Any] = {
    "hf_metadata": {"repo_id": "fake-user/fake-model"},
    "repo_metadata": {"repo_url": "https://github.com/fake-user/fake-model"},
    "nof_code_ds": {"nof_code": 1, "nof_ds": 1},
}


# ----------------------------
# Code Quality Metric
# ----------------------------
def test_code_quality_metric(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """CodeQualityMetric returns valid MetricResult and expected keys."""

    # Prepare fake repo contents
    (tmp_path / "README.md").write_text("This is a fake model readme with enough content.")
    (tmp_path / "config.json").write_text("{}")
    (tmp_path / "train.py").write_text("print('hello')")
    (tmp_path / "extra.py").write_text("print('x')")

    # Monkeypatch repo operations
    monkeypatch.setattr(
        "cli_project.metrics.code_quality.clone_model_repo",
        lambda _: tmp_path,
    )
    monkeypatch.setattr(
        "cli_project.metrics.code_quality.clean_up_cache",
        lambda _: None,
    )

    metric: CodeQualityMetric = CodeQualityMetric()
    result: MetricResult = metric.compute(FAKE_METADATA)

    assert isinstance(result, MetricResult)
    assert result.name == "code_quality"
    assert 0.0 <= float(result.value) <= 1.0
    for key in ["readme_score", "config_score", "training_script_score", "python_file_score", "structure_score"]:
        assert key in result.details


# ----------------------------
# Dataset Quality Metric
# ----------------------------
def test_dataset_quality_metric_runs() -> None:
    metric: DatasetQualityMetric = DatasetQualityMetric()
    result: MetricResult = metric.compute(FAKE_METADATA)

    assert isinstance(result, MetricResult)
    assert result.name == "dataset_quality"
    assert isinstance(result.details, dict)
    # value can be float or dict depending on implementation
    assert isinstance(result.value, (float, dict))


# ----------------------------
# Dataset + Code Metric
# ----------------------------
def test_dataset_and_code_metric_runs() -> None:
    metric: DatasetAndCodeMetric = DatasetAndCodeMetric()
    result: MetricResult = metric.compute(FAKE_METADATA)

    assert isinstance(result, MetricResult)
    assert result.name == "dataset_and_code"
    assert isinstance(result.details, dict)
    assert "nof_code" in FAKE_METADATA["nof_code_ds"]
    assert "nof_ds" in FAKE_METADATA["nof_code_ds"]
