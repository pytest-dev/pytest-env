# WARNING: Do not modify this file. This file was generated and will be overwritten.
from __future__ import annotations

import os


def test_when_ini_has_a_key_which_already_exists_in_env__then_the_env_value_is_overwritten() -> None:
    expected_env_vars = {'MAGIC': 'beta'}
    for key, expected_val in expected_env_vars.items():
        assert os.environ[key] == expected_val, f'Assertion failed for key {key}'
