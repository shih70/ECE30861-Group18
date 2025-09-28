from cli_project.metrics.ramp_up_time import RampUpTimeMetric

if __name__ == "__main__":
    # Example repo URL to test
    url = "https://huggingface.co/openbmb/VoxCPM-0.5B/tree/main"

    # Build metadata dict expected by the metric
    metadata = {"repo_url": url}

    # Instantiate and compute
    metric = RampUpTimeMetric()
    result = metric.compute(metadata)

    print("\n=== Ramp-Up Time Metric ===")
    print(result)
