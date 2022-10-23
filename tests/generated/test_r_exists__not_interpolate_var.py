# WARNING: Do not modify this file. This file was generated and will be overwritten.
from __future__ import annotations

import os


def test_r_exists__not_interpolate_var() -> None:
    expected_env_vars = {'MAGIC': 'hello_{PLANET}'}
    for key, expected_val in expected_env_vars.items():
        assert os.environ[key] == expected_val, f'Assertion failed for key {key}'
