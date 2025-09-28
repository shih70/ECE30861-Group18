#!/usr/bin/env python3
import json
from cli_project.metrics.dataset_quality import DatasetQualityMetric
from cli_project.metrics.base import MetricResult

# Hardcode a real Hugging Face dataset URL for testing
TEST_DATASETS = [
    "https://huggingface.co/datasets/openai/gdpval",
    "https://huggingface.co/datasets/HuggingFaceFW/fineweb-2",
    "https://huggingface.co/datasets/cnn_dailymail"
]


def run_test():
    metric = DatasetQualityMetric()

    for ds_url in TEST_DATASETS:
        metadata = {"repo_url": ds_url}
        result: MetricResult = metric.compute(metadata)

        print(f"\n=== Dataset Quality Metric: {ds_url} ===")
        print(f"Score: {result.value}")
        print("Details:", json.dumps(result.details, indent=2))
        print(f"Latency (ms): {result.latency_ms}")


if __name__ == "__main__":
    run_test()
