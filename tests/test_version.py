from __future__ import annotations


def test_version() -> None:
    import pytest_env  # noqa: PLC0415

    assert pytest_env.__version__ is not None
