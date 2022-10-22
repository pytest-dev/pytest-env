from __future__ import annotations

import os


def test_works() -> None:
    assert os.environ["MAGIC"] == os.environ["_PATCH"]
