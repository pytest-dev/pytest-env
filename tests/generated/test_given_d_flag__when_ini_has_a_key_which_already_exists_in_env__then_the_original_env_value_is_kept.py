# WARNING: Do not modify this file. This file was generated and will be overwritten.
from __future__ import annotations

import os


def test_given_d_flag__when_ini_has_a_key_which_already_exists_in_env__then_the_original_env_value_is_kept() -> None:
    expected_env_vars = {'MAGIC': 'alpha'}
    for key, expected_val in expected_env_vars.items():
        assert os.environ[key] == expected_val, f'Assertion failed for key {key}'
