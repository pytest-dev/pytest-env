from __future__ import annotations

from typing import Dict

import pytest


@pytest.mark.parametrize("name,existing_env_vars,ini_contents,expected_env_vars", [
    pytest.param(
        "test_adds_environment_variable",
        {},  # empty dict means no preexisting environment variables
        "[pytest]\nenv = MAGIC=alpha",
        {"MAGIC": "alpha"}
    ),
    pytest.param(
        "test_given_existing_env_var_returns_new_value",
        {"MAGIC": "alpha"},
        "[pytest]\nenv = MAGIC=beta",
        {"MAGIC": "beta"}
    ),
    pytest.param(
        "test_given_existing_env_var_and_with_default_flag_returns_existing_value",
        {"MAGIC": "alpha"},
        "[pytest]\nenv = D:MAGIC=beta",
        {"MAGIC": "alpha"}
    ),
    pytest.param(
        "test_given_curly_braces_and_no_raw_flag_returns_concatenated",
        {"PLANET": "world"},
        "[pytest]\nenv = MAGIC=hello_{PLANET}",
        {"MAGIC": "hello_world"}
    ),
    pytest.param(
        "test_given_curly_braces_and_raw_flag_returns_raw_value",
        {"PLANET": "world"},
        "[pytest]\nenv = R:MAGIC=hello_{PLANET}",
        {"MAGIC": "hello_{PLANET}"}
    ),
    pytest.param(
        "test_given_curly_braces_take_only_the_newest_value",
        {"PLANET": "earth"},
        "[pytest]\nenv = PLANET=mars\n MAGIC={PLANET}",
        {"MAGIC": "mars"}
    ),
    pytest.param(
        "test_given_curly_braces_take_only_the_applied_value",
        {"PLANET": "earth"},
        "[pytest]\nenv = D:PLANET=mars\n MAGIC={PLANET}",
        {"MAGIC": "earth"}
    ),
    pytest.param(
        "test_given_two_flags_applies_both_of_them",
        {"MAGIC": "alpha"},
        "[pytest]\nenv = D:R:MAGIC=beta",
        {"MAGIC": "alpha"}
    ),
    pytest.param(
        "test_given_two_flags_in_reverse_order_applies_both_of_them",
        {"MAGIC": "alpha"},
        "[pytest]\nenv = R:D:MAGIC=beta",
        {"MAGIC": "alpha"}
    ),
])
def test_cases(testdir: pytest.Testdir, name: str, existing_env_vars: Dict[str, str], ini_contents: str,
               expected_env_vars: Dict[str, str]) -> None:
    set_env_variables(testdir, expected_env_vars)
    for env_var, val in expected_env_vars.items():
        testdir.monkeypatch.setenv(env_var, val)
    write_to_files(testdir, name, ini_contents, expected_env_vars)
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def set_env_variables(testdir: pytest.Testdir, env_vars: Dict[str, str]):
    for env_var, val in env_vars.items():
        testdir.monkeypatch.setenv(env_var, val)


def write_to_files(testdir: pytest.Testdir, name: str, ini_contents: str,
                   expected_env_vars: Dict[str, str]) -> None:
    contents = """
from __future__ import annotations
import ast
import os

def %s() -> None:
    for key, expected_val in ast.literal_eval(\"\"\"%s\"\"\").items():
        assert os.environ[key] == expected_val
    """ % (name, expected_env_vars)

    (testdir.tmpdir / ("%s.py" % name)).write_text(contents, encoding="utf-8")
    (testdir.tmpdir / "pytest.ini").write_text(ini_contents, encoding="utf-8")
