from __future__ import annotations

from pathlib import Path
from shutil import copy2

import pytest

_EXAMPLE = Path(__file__).parent / "example.py"


@pytest.fixture()
def example(testdir: pytest.Testdir) -> pytest.Testdir:
    dest = Path(str(testdir.tmpdir / "test_example.py"))
    # dest.symlink_to(_EXAMPLE)  # for local debugging use this
    copy2(str(_EXAMPLE), str(dest))
    return testdir


def test_simple(example: pytest.Testdir) -> None:
    result = example.runpytest()
    result.assert_outcomes(passed=1)
