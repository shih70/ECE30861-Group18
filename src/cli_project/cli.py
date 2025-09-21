from pathlib import Path
import sys
import subprocess
import json, sys, time
from cli_project.urls.base import parse_url_file

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
    """Implements ./run test (stub for now)"""
    print("0/0 test cases passed. 0% line coverage achieved.")
    print(">>> sys.path =", sys.path)
    sys.exit(1)

def score(url_file: str) -> None:
    """Implements ./run URL_FILE"""
    models = parse_url_file(Path(url_file))
    for model in models:
        print(json.dumps(model.to_record()))

    sys.exit(0)
    # path = Path(url_file)
    # if not path.exists():
    #     sys.stderr.write(f"File not found: {path}\n")
    #     sys.exit(1)

    # with path.open("r", encoding="utf-8") as f:
    #     urls = [line.strip() for line in f if line.strip()]
    
    # # dataset_urls: list = []
    # # code_urls: list = []

    # for url in urls:
    #     item = classify_url(url)
    #     print(item)
    # for url in urls:
    #     if "huggingface.co/datasets" in url:
    #         dataset_urls.append(url)
    #     elif "github.com" in url:
    #         code_urls.append(url)
    #     elif "huggingface.co" in url and "/tree/" in url:  # MODEL
    #         record = {
    #             "name": url,
    #             "category": "MODEL",
    #             "net_score": 0.0,
    #             "net_score_latency": 0,
    #             "ramp_up_time": 0.0,
    #             "ramp_up_time_latency": 0,
    #             "bus_factor": 0.0,
    #             "bus_factor_latency": 0,
    #             "performance_claims": 0.0,
    #             "performance_claims_latency": 0,
    #             "license": 0.0,
    #             "license_latency": 0,
    #             "size_score": {
    #                 "raspberry_pi": 0.0,
    #                 "jetson_nano": 0.0,
    #                 "desktop_pc": 0.0,
    #                 "aws_server": 0.0,
    #             },
    #             "size_score_latency": 0,
    #             "dataset_and_code_score": 0.0,
    #             "dataset_and_code_score_latency": 0,
    #             "dataset_quality": 0.0,
    #             "dataset_quality_latency": 0,
    #             "code_quality": 0.0,
    #             "code_quality_latency": 0,
    #         }

    #         if dataset_urls:
    #             record["linked_datasets"] = dataset_urls
    #         if code_urls:
    #             record["linked_code"] = code_urls

    #         print(json.dumps(record))

    #         dataset_urls = []
    #         code_urls = []

    #     else: 
    #         sys.stderr.write(f"Warning: {url} not recognized as dataset/code/model URL\n")
    #         continue

        
    # sys.exit(0)

if __name__ == "__main__":
    pass
    
