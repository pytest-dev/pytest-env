from __future__ import annotations

from collections import namedtuple
from typing import Dict

import pytest

fields = "test_name,existing_env_vars,ini_contents,expected_env_vars"
TestCase = namedtuple("TestCase", fields)
all_test_cases = [
    TestCase(
        test_name="test_adds_environment_variable",  # name of the test case
        existing_env_vars={},  # empty dict means no preexisting environment variables
        ini_contents="[pytest]\nenv = MAGIC=alpha",  # pytest.ini contents
        expected_env_vars={"MAGIC": "alpha"}
    ),
    TestCase(
        test_name="test_given_existing_env_var_and_returns_new_value",
        existing_env_vars={"MAGIC": "alpha"},
        ini_contents="[pytest]\nenv = MAGIC=beta",
        expected_env_vars={"MAGIC": "beta"}
    ),
    TestCase(
        test_name="test_given_existing_env_var_and_with_default_flag_returns_existing_value",
        existing_env_vars={"MAGIC": "alpha"},
        ini_contents="[pytest]\nenv = D:MAGIC=beta",
        expected_env_vars={"MAGIC": "alpha"}
    ),
    TestCase(
        test_name="test_given_curly_braces_and_no_raw_flag_returns_concatenated",
        existing_env_vars={"PLANET": "world"},
        ini_contents="[pytest]\nenv = MAGIC=hello_{PLANET}",
        expected_env_vars={"MAGIC": "hello_world"}
    ),
    TestCase(
        test_name="test_given_curly_braces_and_raw_flag_returns_raw_value",
        existing_env_vars={"PLANET": "world"},
        ini_contents="[pytest]\nenv = R:MAGIC=hello_{PLANET}",
        expected_env_vars={"MAGIC": "hello_{PLANET}"}
    ),
    TestCase(
        test_name="test_given_curly_braces_take_only_the_newest_value",
        existing_env_vars={"PLANET": "earth"},
        ini_contents="[pytest]\nenv = \n    PLANET=mars\n    MAGIC={PLANET}",
        expected_env_vars={"MAGIC": "mars"}
    ),
    TestCase(
        test_name="test_given_curly_braces_take_only_the_applied_value",
        existing_env_vars={"PLANET": "earth"},
        ini_contents="[pytest]\nenv = \n    D:PLANET=mars\n    MAGIC={PLANET}",
        expected_env_vars={"MAGIC": "earth"}
    ),
    TestCase(
        test_name="test_given_two_flags_applies_both_of_them",
        existing_env_vars={"MAGIC": "alpha"},
        ini_contents="[pytest]\nenv = D:R:MAGIC=beta",
        expected_env_vars={"MAGIC": "alpha"}
    ),
    TestCase(
        test_name="test_given_two_flags_in_reversed_order_applies_both_of_them",
        existing_env_vars={"MAGIC": "alpha"},
        ini_contents="[pytest]\nenv = R:D:MAGIC=beta",
        expected_env_vars={"MAGIC": "alpha"}
    ),
]


@pytest.mark.parametrize(fields, all_test_cases)
def test_cases(testdir: pytest.Testdir, test_name, existing_env_vars, ini_contents, expected_env_vars) -> None:
    for env_var, val in existing_env_vars.items():
        testdir.monkeypatch.setenv(env_var, val)
    create_test(testdir, test_name, expected_env_vars, ini_contents)

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def create_test(testdir: pytest.Testdir, test_name: str, expected_env_vars: Dict[str, str], ini_contents: str) -> None:
    contents = """
from __future__ import annotations
import ast
import os

def %s() -> None:
    for key, expected_val in ast.literal_eval(\"\"\"%s\"\"\").items():
        assert os.environ[key] == expected_val
    """ % (test_name, expected_env_vars)

    (testdir.tmpdir / "test_returns_value.py").write_text(contents, encoding="utf-8")
    (testdir.tmpdir / "pytest.ini").write_text(ini_contents, encoding="utf-8")
