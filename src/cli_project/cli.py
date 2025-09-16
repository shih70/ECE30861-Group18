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
        [py, "-m", "pip", "install", "--user", "--upgrade", "pip", "wheel"],
        [py, "-m", "pip", "install", "--user", "-r", str(req)],
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


# fix6: avoid name collision with the entrypoint `main()` below which caused F811 + mypy [no-redef/call-arg]
#       Rename the Typer callback to `root` so there is only one `main()` in the module.
@app.callback(invoke_without_command=True)
def root(ctx: typer.Context, url_file: Path | None = typer.Argument(None)) -> None:
    """
    Implements: ./run URL_FILE  (STUB)
      - If a URL file is provided and no subcommand was invoked:
        * validate the file exists & is readable
        * (stub) do nothing else, exit 0
      - If nothing provided and no subcommand: show usage, exit 1
    """
    # If a subcommand (install/test) was used, do nothing here.
    if ctx.invoked_subcommand is not None:
        return

    if url_file is None:
        _eprint("Usage: ./run [install|test|URL_FILE]")
        _exit(1)

    # fix7: help mypy narrow Optional[Path] → Path with an assert + local name
    assert url_file is not None
    path: Path = url_file

    # Validate file (ASCII newline-delimited URLs per spec)
    if not path.exists() or not path.is_file():
        _eprint(f"URL file not found: {path}")
        _exit(1)

    try:
        # Touch-read to ensure it's readable; your real scorer will parse lines here.
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if url:
                    print(json.dumps({"url": url, "result": "TODO"}))
    except Exception as exc:
        _eprint(f"Failed to read URL file: {exc}")
        _exit(1)

    # Spec says output only for Model URLs; stub emits nothing else.
    _exit(0)


def hello(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name to greet",
        ),
    ] = "world",
) -> None:
    """Say hello to someone."""
    typer.echo(f"Hello, {name}!")


# Register commands AFTER definitions to preserve typing
app.command(name="hello")(hello)


def main() -> None:
    """
    Entry-point for `python -m cli_project.cli`.
    fix8: keep a single `main()` that starts the Typer app; do NOT call the callback directly.
    """
    app()


if __name__ == "__main__":
    main()
