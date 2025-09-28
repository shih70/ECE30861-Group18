# test_dataset_quality.py

from cli_project.core.entities import HFModel
from cli_project.metrics.dataset_quality import DatasetQualityMetric
from cli_project.adapters.huggingface import fetch_repo_metadata


def test_dataset_quality_from_url(url: str):
    # Step 1: Initialize model object
    model = HFModel(model_url=url, metrics={})

    # Step 2: Populate metadata
    fetch_repo_metadata(model)

    # Step 3: Run dataset quality metric
    metric = DatasetQualityMetric()
    score = metric.score(model)
    latency = metric.score_latency(model)

    # Step 4: Output results
    print("Model URL:", url)
    print("Dataset Quality Score:", score)
    print("Latency (ms):", latency["latency_ms"])


if __name__ == "__main__":
    # You can swap this out with another HF model that includes datasets
    test_url = "https://huggingface.co/bert-base-uncased"
    test_dataset_quality_from_url(test_url)
