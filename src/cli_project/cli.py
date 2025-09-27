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
    url_path = Path(url_file)
    models = parse_url_file(url_path)

    for m in models:
        print("MODEL:", m.url)
        for c in m.code:
            print("  CODE:", c.url)
        for d in m.datasets:
            print("  DATASET:", d.url)

    # Encode + print as NDJSON
    # NDJSONEncoder.print_records(models)
    sys.exit(0)

if __name__ == "__main__":
    pass
