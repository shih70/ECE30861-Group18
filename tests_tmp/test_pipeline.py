import time
from typing import Any
from cli_project.metrics.base import Metric, MetricResult

# Fake metric for testing concurrency
class FakeSlowMetric(Metric):
    @property
    def name(self) -> str:
        return "fake_slow"

    def compute(self, context: dict[str, Any]) -> MetricResult:
        t0 = time.perf_counter()
        time.sleep(0.1)  # simulate API delay
        latency = int((time.perf_counter() - t0) * 1000)
        return MetricResult(self.name, 1.0, {}, latency)


class FakeFastMetric(Metric):
    @property
    def name(self) -> str:
        return "fake_fast"

    def compute(self, context: dict[str, Any]) -> MetricResult:
        return MetricResult(self.name, 0.5, {}, 1)


def test_concurrent_pipeline_runs_fast():
    context = {"hf_metadata": {"license": "Apache-2.0"}}
    metrics = [FakeSlowMetric(), FakeFastMetric()]
    results = compute_all_metrics(context, metrics)
    names = [r.name for r in results]
    assert "fake_slow" in names
    assert "fake_fast" in names

def test_pipeline_attach_results_to_hfmodel():
    url = HFModelURL("https://huggingface.co/bert-base-uncased")
    model = HFModel(model_url=url)
    fake_results = [MetricResult("license", 1.0, {}, 10)]
    model.add_results(fake_results)
    assert "license" in model.metric_scores
    assert model.metric_scores["license"].value == 1.0
