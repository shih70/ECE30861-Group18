from cli_project.metrics.size_score import SizeScoreMetric
from cli_project.core.entities import HFModelURL, HFModel
from cli_project.adapters.huggingface import fetch_repo_metadata

def test_size_score_from_url(url: str):
    print(f"\nTesting model size score from URL: {url}")

    # Create HFModel object from URL
    model_url = HFModelURL(url=url)
    model = HFModel(model_url=model_url)

    # Fetch metadata (fills in model.repo_id and model.metadata)
    try:
        fetch_repo_metadata(model)
    except Exception as e:
        print(f"[ERROR] Failed to fetch metadata: {e}")
        return

    # Run SizeScoreMetric
    metric = SizeScoreMetric()
    result = metric.compute(model.metadata)

    print(f"Model: {model.repo_id}")
    print(f"Size (MB): {model.metadata.get('size_mb')}")
    print(f"Score: {result.value}")
    print(f"Latency (ms): {result.latency_ms}")


if __name__ == "__main__":
    test_url = "https://huggingface.co/google-bert/bert-base-uncased"
    test_size_score_from_url(test_url)
