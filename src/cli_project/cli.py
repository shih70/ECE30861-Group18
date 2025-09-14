from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from typing import Annotated
import typer

# Single, global app instance
app = typer.Typer(help="CLI Project – starter CLI (typed)", add_completion=False, no_args_is_help=False)


## Helpers Functions
# A helper to print error messages to stderr
def _eprint(msg: str) -> None:
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()

# A helper to exit with a given code [0: sucess, not 0: failure]
def _exit(code: int) -> None:
    raise typer.Exit(code)


@app.command(help="Install dependendcies in userland")
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
    
    # Ensures that pip commands run with the venv python
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

@app.command(help="Run test suite and print coerage line")
def test() -> None:
    """
    Implements: ./run test  (STUB)
      - For now, just print the required line and exit 1 (so graders know it’s a stub).
      - Replace later with real pytest + coverage parsing.
    """
    print("0/0 test cases passed. 0% line coverage achieved.")
    _exit(1)


# @app.callback(invoke_without_command=True)
# def main(ctx: typer.Context, url_file: Path | None = typer.Argument(None)) -> None:
#     """
#     Implements: ./run URL_FILE  (STUB)
#       - If a URL file is provided and no subcommand was invoked:
#         * validate the file exists & is readable
#         * (stub) do nothing else, exit 0
#       - If nothing provided and no subcommand: show usage, exit 1
#     """
#     # If a subcommand (install/test) was used, do nothing here.
#     if ctx.invoked_subcommand is not None:
#         return

#     if url_file is None:
#         _eprint("Usage: ./run [install|test|URL_FILE]")
#         _exit(1)

#     # Validate file (ASCII newline-delimited URLs per spec)
#     if not url_file.exists() or not url_file.is_file():
#         _eprint(f"URL file not found: {url_file}")
#         _exit(1)

#     try:
#         # Touch-read to ensure it's readable; your real scorer will parse lines here.
#         _ = url_file.read_text(encoding="utf-8", errors="strict")
#     except Exception as exc:
#         _eprint(f"Failed to read URL file: {exc}")
#         _exit(1)

#     # Spec says output only for Model URLs; stub emits nothing.
#     _exit(0)



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
    """Entry-point for `python -m cli_project.cli`."""
    app()


if __name__ == "__main__":
    main()
