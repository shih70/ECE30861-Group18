from pathlib import Path
import sys
import subprocess
import json, sys, time
from cli_project import tester
from cli_project.urls.base import parse_url_file
from cli_project.io.ndjson import NDJSONEncoder
from cli_project.core.entities import HFModel
from cli_project.metrics.base import MetricResult
# from cli_project.adapters.huggingface import fetch_repo_metadata

def install() -> None:
    """Implements ./run install"""
    py = sys.executable
    cmds = [
        [py, "-m", "pip", "install", "--user", "--upgrade", "pip", "wheel"],
        [py, "-m", "pip", "install", "--user", "-r", "requirements.txt"],
    ]
    for cmd in cmds:
        rc = subprocess.call(cmd)
        if rc != 0:
            sys.stderr.write(f"Command failed: {' '.join(cmd)} (exit {rc})\n")
            sys.exit(rc)
    sys.exit(0)

def test() -> None:
    """Implements ./run test """
    rc = tester.run_tests()

    sys.exit(rc)
    # print("0/0 test cases passed. 0% line coverage achieved.")

    # sys.exit(1)

def score(url_file: str) -> None:
    """Implements ./run URL_FILE"""
    url_path = Path(url_file)
    url_objs = parse_url_file(url_path)

    models: list[HFModel] = []
    for u in url_objs:
        # wrap HFModelURL into HFModel
        model = HFModel(model_url=u)
        
        # attach fake results
        fake_results = [
            MetricResult("license", 1.0, {"normalized": "apache-2.0"}, 10),
            MetricResult("bus_factor", 0.9, {"contributors": 3}, 20),
        ]
        model.add_results(fake_results)
        models.append(model)

    # Encode + print as NDJSON
    NDJSONEncoder.print_records(models)
    sys.exit(0)

if __name__ == "__main__":
    pass
