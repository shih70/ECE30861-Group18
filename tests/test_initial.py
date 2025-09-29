# tests/test_smoke.py
import subprocess
import sys
from pathlib import Path

def test_cli_runs_help() -> None:
    """Smoke test: CLI should run with --help without errors."""
    result = subprocess.run(
        [sys.executable, "./run", "--help"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
