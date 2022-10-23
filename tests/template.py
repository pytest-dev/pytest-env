from __future__ import annotations

import ast
import os


def test_env() -> None:
    for key, value in ast.literal_eval(os.environ["_TEST_ENV"]).items():
        assert os.environ[key] == value, key
