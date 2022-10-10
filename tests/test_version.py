from __future__ import annotations


def test_version() -> None:
    import pytest_env

    assert pytest_env.__version__ is not None
