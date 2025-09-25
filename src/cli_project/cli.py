from pathlib import Path
import sys
import subprocess
import json, sys, time
from cli_project.urls.base import parse_url_file
from cli_project.io.ndjson import NDJSONEncoder
from cli_project.core.entities import HFModel
from cli_project.adapters.huggingface import fetch_repo_metadata

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

    sys.exit(1)

def score(url_file: str) -> None:
    """Implements ./run URL_FILE"""
    # Parse into URL objects
    model_urls = parse_url_file(Path(url_file))

    # Wrap into HFModel objects (so they include metrics)
    models = [HFModel(mu) for mu in model_urls]

    
    for model in models:
        info = fetch_repo_metadata(model)
        if info:
            print(f"Metadata for {info['repo_id']}:")
            print(f"  Downloads: {info['downloads']}")
            print(f"  Likes: {info['likes']}")
            print(f"  Last Modified: {info['last_modified']}")
            print(f"  Number of files: {info['num_files']}")
            print("-" * 40)
        else:
            print(f"Could not fetch metadata for {model.model_url.url}")

    # Encode + print as NDJSON
    NDJSONEncoder.print_records(models)
    sys.exit(0)

if __name__ == "__main__":
    pass
