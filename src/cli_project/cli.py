from __future__ import annotations

from typing import Annotated
import typer

# Single, global app instance
app = typer.Typer(help="CLI Project – starter CLI (typed)")


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
