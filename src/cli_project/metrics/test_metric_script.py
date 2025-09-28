from cli_project.metrics.dataset_and_code import DatasetAndCodeMetric
from cli_project.adapters.huggingface import fetch_repo_metadata

class FakeModel:
    """Minimal fake model just to satisfy fetch_repo_metadata()."""
    def __init__(self, url: str):
        self.model_url = type("obj", (), {"url": url})
        self.metadata = {}
        self.repo_id = None


def run_test(url: str, label: str):
    print(f"\n=== Test: {label} ===")

    # Make fake model to pass into API
    fake_model = FakeModel(url)

    # Fetch metadata from HF API
    metadata = fetch_repo_metadata(fake_model)

    # Add dummy counts for dataset/code URLs
    metadata["nof_code_ds"] = {"nof_code": 0, "nof_ds": 0}

    # Run metric
    metric = DatasetAndCodeMetric()
    result = metric.compute(metadata)

    print("Repo URL:", url)
    print("Score:", result.value)
    print("Details:", result.details)
    print("Latency (ms):", result.latency_ms)


if __name__ == "__main__":
    run_test("https://huggingface.co/google-bert/bert-base-uncased", "BERT Base")
    run_test("https://huggingface.co/openai/whisper-tiny", "Whisper Tiny")
    run_test("https://huggingface.co/microsoft/resnet-50", "ResNet-50")
