from __future__ import annotations


def test_version() -> None:
    import pytest_env  # ruff:ignore[import-outside-top-level]

    assert pytest_env.__version__ is not None
