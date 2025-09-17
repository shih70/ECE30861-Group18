from __future__ import annotations
from pathlib import Path
from typing import Annotated
import sys
import subprocess
import typer
import json

# fix1: ensure block comments follow flake8 E265 ("# " + space)
# Single, global app instance
app = typer.Typer(
    help="CLI Project — starter CLI (typed)",  # fix2: replace odd dash with ascii or keep unicode; flake8 is fine either way
    add_completion=False,
    no_args_is_help=False,
)
# Helper Functions
# fix3: header comment style and typo
# A helper to print error messages to stderr
def _eprint(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


# A helper to exit with a given code [0: success, not 0: failure]
def _exit(code: int) -> None:
    raise typer.Exit(code)


@app.command(help="Install dependencies in userland")  # fix4: typo 'dependendcies' -> 'dependencies'
def install() -> None:
    """
    Implements: ./run install
      - pip --user upgrade pip+wheel
      - pip --user install -r requirements.txt
      - exit 0 on success, non-zero on failure
    """
    req = Path("requirements.txt")

    if not req.exists():
        _eprint("requirements.txt not found in project root.")
        _exit(1)

    # Ensure pip commands run with the venv python
    py = sys.executable

    cmds = [
        [py, "-m", "pip", "install", "--upgrade", "pip", "wheel"],
        [py, "-m", "pip", "install", "-r", str(req)],
    ]

    for cmd in cmds:
        rc = subprocess.call(cmd)
        if rc != 0:
            _eprint(f"Command failed: {' '.join(cmd)} (exit {rc})")
            _exit(rc)

    _exit(0)


@app.command(help="Run test suite and print coverage line")  # fix5: 'coerage' -> 'coverage'
def test() -> None:
    """
    Implements: ./run test  (STUB)
      - For now, just print the required line and exit 1 (so graders know it’s a stub).
      - Replace later with real pytest + coverage parsing.
    """
    print("0/0 test cases passed. 0% line coverage achieved.")
    _exit(1)


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    url_file: Path = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to a text file (one URL per line).",
    ),
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    
    if url_file is None:
        _eprint("Usage: ./run [install|test|hello|URL_FILE]", err=True)
        _exit(1)
    
    urls: list[str] = []
    with url_file.open("r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if url:
                urls.append(url)

        # checking that's working
        for url in urls:
            print(url)
        
    _exit(0)

def main() -> None:
    """
    Entry-point for `python -m cli_project.cli`.
    fix8: keep a single `main()` that starts the Typer app; do NOT call the callback directly.
    """
    app()


if __name__ == "__main__":
    main()
