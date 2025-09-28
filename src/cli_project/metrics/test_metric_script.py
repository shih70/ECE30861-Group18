from cli_project.metrics.performance_claims import PerformanceClaimsMetric
from cli_project.core.entities import HFModel


if __name__ == "__main__":
    # Pick any Hugging Face repo with evaluation claims in its README
    repo_url = "https://huggingface.co/google-bert/bert-base-uncased/tree/main"

    # Build metadata dict (LLM fetcher expects repo_url inside metadata)
    metadata = {"repo_url": repo_url}

    metric = PerformanceClaimsMetric()
    result = metric.compute(metadata)

    print("\n=== Performance Claims Metric (LLM) ===")
    print(result)
