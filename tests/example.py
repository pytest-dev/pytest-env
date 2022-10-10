from __future__ import annotations

import os


def test_works() -> None:
    assert "MAGIC" not in os.environ
