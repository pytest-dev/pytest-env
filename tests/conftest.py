from __future__ import annotations

from pathlib import Path
from typing import Final

import pytest

pytest_plugins = ["pytester"]


@pytest.fixture
def env_test_template() -> str:
    template: Final[Path] = Path(__file__).with_name("template.py")
    # Execute the original template so coverage still records its assertions.
    return f"from runpy import run_path\n\ntest_env = run_path({str(template)!r})['test_env']\n"
