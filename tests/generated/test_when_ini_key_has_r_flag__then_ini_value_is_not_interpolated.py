# WARNING: Do not modify this file. This file was generated and will be overwritten.
from __future__ import annotations

import os


def test_when_ini_key_has_r_flag__then_ini_value_is_not_interpolated() -> None:
    expected_env_vars = {'MAGIC': 'hello_{PLANET}'}
    for key, expected_val in expected_env_vars.items():
        assert os.environ[key] == expected_val, f'Assertion failed for key {key}'
