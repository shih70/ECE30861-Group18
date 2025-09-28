# test_dataset_quality.py

from cli_project.core.entities import HFModel, HFModelURL
from cli_project.metrics.dataset_quality import DatasetQualityMetric
from cli_project.adapters.huggingface import fetch_repo_metadata


def test_dataset_quality_from_url(url: str):
    # Step 1: Initialize model object
    model_url = HFModelURL(url=url)
    model = HFModel(model_url=model_url)

    # Step 2: Populate metadata
    try:
        fetch_repo_metadata(model)
    except Exception as e:
        print(f"[ERROR] Failed to fetch metadata: {e}")
        return

    # Step 3: Run dataset quality metric
    metric = DatasetQualityMetric()
    score = metric.compute(model.metadata)

    # Step 4: Output results
    print("Model URL:", url)
    print(f"Model: {model.repo_id}")
    print(f"Size (MB): {model.metadata.get('size_mb')}")
    print(f"Score: {score.value}")
    print(f"Latency (ms): {score.latency_ms}")
  
