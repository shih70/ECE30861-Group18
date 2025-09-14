import cli_project as cp


def test_smoke() -> None:
    # importing the package triggers coverage
    assert isinstance(cp.__version__, str)
