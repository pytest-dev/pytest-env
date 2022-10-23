# WARNING: Do not modify this file. This file was generated and will be overwritten.
from __future__ import annotations

import os


def test_new_key__add_to_env() -> None:
    expected_env_vars = {'MAGIC': 'alpha'}
    for key, expected_val in expected_env_vars.items():
        assert os.environ[key] == expected_val, f'Assertion failed for key {key}'
