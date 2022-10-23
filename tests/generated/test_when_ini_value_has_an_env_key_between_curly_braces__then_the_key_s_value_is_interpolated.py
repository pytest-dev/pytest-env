# WARNING: Do not modify this file. This file was generated and will be overwritten.
from __future__ import annotations

import os


def test_when_ini_value_has_an_env_key_between_curly_braces__then_the_key_s_value_is_interpolated() -> None:
    expected_env_vars = {'MAGIC': 'hello_world'}
    for key, expected_val in expected_env_vars.items():
        assert os.environ[key] == expected_val, f'Assertion failed for key {key}'
