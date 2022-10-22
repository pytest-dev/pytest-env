from __future__ import annotations

from pathlib import Path
from shutil import copy2

import pytest

_EXAMPLE_PY = Path(__file__).parent / "example.py"
_EXAMPLE_INI = Path(__file__).parent / "example_pytest.ini"


@pytest.fixture()
def example(testdir: pytest.Testdir) -> pytest.Testdir:
    dest = Path(str(testdir.tmpdir / "test_example.py"))
    # dest.symlink_to(_EXAMPLE)  # for local debugging use this
    copy2(str(_EXAMPLE_PY), str(dest))

    dest = Path(str(testdir.tmpdir / "pytest.ini"))
    # dest.symlink_to(_EXAMPLE)  # for local debugging use this
    copy2(str(_EXAMPLE_INI), str(dest))

    return testdir


def test_simple(example: pytest.Testdir, monkeypatch) -> None:
    monkeypatch.setenv('EXISTING_KEY', 'EXISTING_VALUE')
    monkeypatch.setenv('EXISTING_KEY_D', 'EXISTING_VALUE_D')
    monkeypatch.setenv('PLANET', 'WORLD')

    result = example.runpytest()
    result.assert_outcomes(passed=9)
