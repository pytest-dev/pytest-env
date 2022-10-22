from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def example(testdir: pytest.Testdir) -> pytest.Testdir:
    src = Path(__file__).parent / "example.py"
    dest = Path(str(testdir.tmpdir / "test_example.py"))
    dest.symlink_to(src)
    return testdir


def test_simple(example: pytest.Testdir) -> None:
    (example.tmpdir / "pytest.ini").write_text("[pytest]\nenv = MAGIC=alpha", encoding="utf-8")
    example.monkeypatch.setenv("_PATCH", "alpha")
    result = example.runpytest()
    result.assert_outcomes(passed=1)
