from cli_project.core.entities import HFModel
from cli_project.metrics.code_quality import CodeQualityMetric
from cli_project.adapters.huggingface import fetch_repo_metadata
from cli_project.urls.base import HFModelURL


def test_code_quality_from_url(url: str):
    # Step 1: Construct model URL object
    model_url_obj = HFModelURL(url)

    model = HFModel(model_url_obj)

    # Step 2: Fetch metadata (populates model.repo_id and metadata)
    fetch_repo_metadata(model)

    # Step 3: Run code quality metric
    metric = CodeQualityMetric()
    score = metric.score(model)
    latency = metric.score_latency(model)

    # Step 4: Print results
    print("Model URL:", url)
    print(f"\nCode Quality Score: {score:.3f}")
    print(f"Latency: {latency['latency_ms']:.3f} ms")


if __name__ == "__main__":
    # Try with a real Hugging Face repo that includes code
    test_url = "https://huggingface.co/google-bert/bert-base-uncased"
    test_code_quality_from_url(test_url)
