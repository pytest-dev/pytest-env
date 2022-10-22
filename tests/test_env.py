from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pytest


@dataclass
class TestCase:
    name: str  # name of the test case
    existing_env_vars: Dict[str, str]  # preexisting environment variables
    ini_contents: str  # pytest.ini contents
    expected_env_vars: Dict[str, str]  # variables that are expected to be found after the plugin has done its job

    # This helps pytest output to show test name for each test
    def __str__(self):
        return self.name


all_test_cases = [
    TestCase(
        name="test_adds_environment_variable",
        existing_env_vars={},  # empty dict means no preexisting environment variables
        ini_contents="[pytest]\nenv = MAGIC=alpha",
        expected_env_vars={"MAGIC": "alpha"}
    ),
    TestCase(
        name="test_given_existing_env_var_and_returns_new_value",
        existing_env_vars={"MAGIC": "alpha"},
        ini_contents="[pytest]\nenv = MAGIC=beta",
        expected_env_vars={"MAGIC": "beta"}
    ),
    TestCase(
        name="test_given_existing_env_var_and_with_default_flag_returns_existing_value",
        existing_env_vars={"MAGIC": "alpha"},
        ini_contents="[pytest]\nenv = D:MAGIC=beta",
        expected_env_vars={"MAGIC": "alpha"}
    ),
    TestCase(
        name="test_given_curly_braces_and_no_raw_flag_returns_concatenated",
        existing_env_vars={"PLANET": "world"},
        ini_contents="[pytest]\nenv = MAGIC=hello_{PLANET}",
        expected_env_vars={"MAGIC": "hello_world"}
    ),
    TestCase(
        name="test_given_curly_braces_and_raw_flag_returns_raw_value",
        existing_env_vars={"PLANET": "world"},
        ini_contents="[pytest]\nenv = R:MAGIC=hello_{PLANET}",
        expected_env_vars={"MAGIC": "hello_{PLANET}"}
    ),
    TestCase(
        name="test_given_curly_braces_take_only_the_newest_value",
        existing_env_vars={"PLANET": "earth"},
        ini_contents="[pytest]\nenv = PLANET=mars\n MAGIC={PLANET}",
        expected_env_vars={"MAGIC": "mars"}
    ),
    TestCase(
        name="test_given_curly_braces_take_only_the_applied_value",
        existing_env_vars={"PLANET": "earth"},
        ini_contents="[pytest]\nenv = D:PLANET=mars\n MAGIC={PLANET}",
        expected_env_vars={"MAGIC": "earth"}
    ),
    TestCase(
        name="test_given_two_flags_applies_both_of_them",
        existing_env_vars={"MAGIC": "alpha"},
        ini_contents="[pytest]\nenv = D:R:MAGIC=beta",
        expected_env_vars={"MAGIC": "alpha"}
    ),
    TestCase(
        name="test_given_two_flags_in_reversed_order_applies_both_of_them",
        existing_env_vars={"MAGIC": "alpha"},
        ini_contents="[pytest]\nenv = R:D:MAGIC=beta",
        expected_env_vars={"MAGIC": "alpha"}
    ),
]


@pytest.mark.parametrize("testcase", all_test_cases, ids=str)
def test_cases(testdir: pytest.Testdir, testcase: TestCase) -> None:
    for env_var, val in testcase.existing_env_vars.items():
        testdir.monkeypatch.setenv(env_var, val)
    create_test(testdir, testcase)

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def create_test(testdir: pytest.Testdir, testcase: TestCase) -> None:
    contents = """
from __future__ import annotations
import ast
import os

def %s() -> None:
    for key, expected_val in ast.literal_eval(\"\"\"%s\"\"\").items():
        assert os.environ[key] == expected_val
    """ % (testcase.name, testcase.expected_env_vars)

    (testdir.tmpdir / ("%s.py" % testcase.name)).write_text(contents, encoding="utf-8")
    (testdir.tmpdir / "pytest.ini").write_text(testcase.ini_contents, encoding="utf-8")
