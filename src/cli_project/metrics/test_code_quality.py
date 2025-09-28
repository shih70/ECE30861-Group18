from cli_project.metrics.code_quality import CodeQualityMetric
from cli_project.adapters.huggingface import fetch_repo_metadata
from cli_project.core.entities import HFModelURL, HFModel


def test_code_quality_from_url(repo_url: str):
    """
    Test code quality metric using a Hugging Face repo URL.
    """
    model_url = HFModelURL(url=repo_url)
    model = HFModel(model_url=model_url)
    try:
        fetch_repo_metadata(model)
    except Exception as e:
        print(f"[ERROR] Failed to fetch metadata: {e}")
        return

    # Run the CodeQualityMetric
    metric = CodeQualityMetric()
    result = metric.compute(model.metadata)

    # Print results
    print("Model URL:", repo_url)
    print("Code Quality Score:", result.value)
    print("Latency (ms):", result.latency_ms)
    print("Details:", result.details)


if __name__ == "__main__":
    # 🔹 Replace this URL with a repo that actually contains Python code
    test_url = "https://huggingface.co/openai/whisper-tiny/tree/main"  # or "openai/whisper" etc.
    test_code_quality_from_url(test_url)
