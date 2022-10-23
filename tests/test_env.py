from __future__ import annotations

from typing import Dict

import pytest


@pytest.mark.parametrize("existing_env_vars,ini_contents,expected_env_vars", [
    pytest.param(
        {},  # empty dict means no preexisting environment variables
        "[pytest]\nenv = MAGIC=alpha",
        {"MAGIC": "alpha"},
        id="When ini has a new key, Then it is added to env"
    ),
    pytest.param(
        {"MAGIC": "alpha"},
        "[pytest]\nenv = MAGIC=beta",
        {"MAGIC": "beta"},
        id="When ini has a key which already exists in env, Then the env value is overwritten"
    ),
    pytest.param(
        {"MAGIC": "alpha"},
        "[pytest]\nenv = D:MAGIC=beta",
        {"MAGIC": "alpha"},
        id="Given D flag, When ini has a key which already exists in env, Then the original env value is kept"
    ),
    pytest.param(
        {"PLANET": "world"},
        "[pytest]\nenv = MAGIC=hello_{PLANET}",
        {"MAGIC": "hello_world"},
        id="When ini value has an env key between curly braces, Then the key's value is interpolated"
    ),
    pytest.param(
        {"PLANET": "world"},
        "[pytest]\nenv = R:MAGIC=hello_{PLANET}",
        {"MAGIC": "hello_{PLANET}"},
        id="When ini key has R flag, Then ini value is not interpolated"
    ),
    pytest.param(
        {"MAGIC": "a"},
        "[pytest]\nenv = R:MAGIC={MAGIC}b\n D:MAGIC={MAGIC}c\n MAGIC={MAGIC}d",
        {"MAGIC": "{MAGIC}bd"},
        id="When ini has repeating keys, Then values and flags are evaluated separately and incrementally"
    ),
    pytest.param(
        {"MAGIC": "alpha"},
        "[pytest]\nenv = D:R:MAGIC=beta",
        {"MAGIC": "alpha"},
        id="When ini key has two flags, Then both are applied"
    ),
    pytest.param(
        {"MAGIC": "alpha"},
        "[pytest]\nenv = R:D:MAGIC=beta",
        {"MAGIC": "alpha"},
        id="When ini key has two flags (in reverse order), Then both are applied"
    ),
])
def test_cases(testdir: pytest.Testdir, existing_env_vars: Dict[str, str], ini_contents: str,
               expected_env_vars: Dict[str, str]) -> None:
    set_env_variables(testdir, existing_env_vars)
    write_to_files(testdir, ini_contents, expected_env_vars)
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def set_env_variables(testdir: pytest.Testdir, env_vars: Dict[str, str]):
    for env_var, val in env_vars.items():
        testdir.monkeypatch.setenv(env_var, val)


def write_to_files(testdir: pytest.Testdir, ini_contents: str,
                   expected_env_vars: Dict[str, str]) -> None:
    contents = """
from __future__ import annotations
import ast
import os


def test_() -> None:
    expected_env_vars = ast.literal_eval(\"\"\"%s\"\"\")
    for key, expected_val in expected_env_vars.items():
        assert os.environ[key] == expected_val, f'Assertion failed for key {key}'
    """ % expected_env_vars

    (testdir.tmpdir / 'test_.py').write_text(contents, encoding="utf-8")
    (testdir.tmpdir / "pytest.ini").write_text(ini_contents, encoding="utf-8")
