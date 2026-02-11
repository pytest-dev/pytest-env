from __future__ import annotations

import ast
import os


def test_env() -> None:
    for key, value in ast.literal_eval(os.environ["_TEST_ENV"]).items():
        if value is None:
            assert key not in os.environ, f"{key} should be unset"
        else:
            assert os.environ[key] == value, key
