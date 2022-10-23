# WARNING: Do not modify this file. This file was generated and will be overwritten.
from __future__ import annotations

import os


def test_when_ini_has_a_new_key__then_it_is_added_to_env() -> None:
    expected_env_vars = {'MAGIC': 'alpha'}
    for key, expected_val in expected_env_vars.items():
        assert os.environ[key] == expected_val, f'Assertion failed for key {key}'
