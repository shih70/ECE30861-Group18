from cli_project.metrics.bus_factor import BusFactorMetric
from cli_project.adapters.git_repo import fetch_bus_factor_raw_contributors

if __name__ == "__main__":
    repo_url = "https://github.com/shih70/ECE30861-Group18"  # change if needed

    # Step 1: fetch raw GitHub data
    gh_data = fetch_bus_factor_raw_contributors(repo_url)
    print("Raw GitHub data:", gh_data)

    # Step 2: compute the metric
    metric = BusFactorMetric()
    result = metric.compute(gh_data)
    print("MetricResult:", result)
