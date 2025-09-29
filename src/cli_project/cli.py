from pathlib import Path
import sys
import subprocess
import json, sys, time
from typing import Any
from cli_project.core import log
from cli_project import tester
from cli_project.urls.base import parse_url_file
from cli_project.io.ndjson import NDJSONEncoder
from cli_project.core.entities import HFModel
from cli_project.metrics.base import Metric, MetricResult
from cli_project.metrics.license import LicenseMetric
from cli_project.metrics.bus_factor import BusFactorMetric
from cli_project.metrics.performance_claims import PerformanceClaimsMetric
from cli_project.metrics.ramp_up_time import RampUpTimeMetric
from cli_project.metrics.size_score import SizeScoreMetric
from cli_project.metrics.dataset_and_code import DatasetAndCodeMetric
from cli_project.metrics.dataset_quality import DatasetQualityMetric
from cli_project.metrics.code_quality import CodeQualityMetric
from cli_project.metrics.dataset_quality import DatasetQualityMetric


from cli_project.adapters.huggingface import fetch_repo_metadata
from cli_project.adapters.git_repo import fetch_bus_factor_metrics, fetch_bus_factor_raw_contributors


# from cli_project.adapters.huggingface import fetch_repo_metadata

def install() -> None:
    """Implements ./run install"""
    log.setup_logging()
    
    log.info("installing requirements..")
    py = sys.executable
    cmds = [
        [py, "-m", "pip", "install", "--user", "--upgrade", "pip", "wheel"],
        [py, "-m", "pip", "install", "--user", "-r", "requirements.txt"],
    ]
    for cmd in cmds:
        rc = subprocess.call(cmd)
        if rc != 0:
            sys.stderr.write(f"Command failed: {' '.join(cmd)} (exit {rc})\n")
            log.error(f"Command failed: {' '.join(cmd)} (exit {rc})\n")
            sys.exit(rc)
    log.info("requiremetns installed successfully")
    sys.exit(0)

def test() -> None:
    """Implements ./run test """
    log.setup_logging()
    rc = tester.run_tests()

    sys.exit(rc)
    # print("0/0 test cases passed. 0% line coverage achieved.")

    # sys.exit(1)

def score(url_file: str) -> None:
    """Implements ./run URL_FILE"""
    log.setup_logging()

    url_path = Path(url_file)
    url_objs = parse_url_file(url_path)
    # print(url_objs)

    models: list[HFModel] = []
    for u in url_objs:
        # wrap HFModelURL into HFModel
        model = HFModel(model_url=u)
        hf_metadata = fetch_repo_metadata(model)  # fills model.repo_id + model.metadata
        nof_code_ds: dict[str, Any] = dict()
        nof_code_ds["nof_code"] = len(model.model_url.code)
        nof_code_ds["nof_ds"] = len(model.model_url.datasets)

        if model.model_url.code:
            repo_url = model.model_url.code[0].url
            repo_metadata = fetch_bus_factor_raw_contributors(repo_url)
            repo_metadata["repo_url"] = repo_url

        else:
            repo_metadata = {}

        if model.model_url.datasets:
            dataset_url = model.model_url.datasets[0].url
            hf_metadata["dataset_url"] = dataset_url

            # repo_metadata = fetch_bus_factor_raw_contributors(model.model_url.url)

        model.metadata =  {"hf_metadata" : hf_metadata, "repo_metadata" : repo_metadata, "nof_code_ds" : nof_code_ds}

        # print(model.metadata["hf_metadata"].get("repo_url"))
        metric_results: list[MetricResult] = []
        for metric_cls in Metric.__subclasses__():
            # print(metric_cls)
            metric = metric_cls()
            result = metric.compute(model.metadata)
            metric_results.append(result)


        model.add_results(metric_results)
        # print(model.metric_scores)
        models.append(model)
        # print(model.metric_scores["size_score"])

    # Encode + print as NDJSON
    NDJSONEncoder.print_records(models)
    sys.exit(0)

if __name__ == "__main__":
    pass
