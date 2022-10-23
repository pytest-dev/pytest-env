from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

import pytest
from _pytest.fixtures import FixtureRequest


@pytest.mark.parametrize("existing_env_vars,ini_contents,expected_env_vars", [
    pytest.param(
        {},  # empty dict means no preexisting environment variables
        "[pytest]\nenv = MAGIC=alpha",
        {"MAGIC": "alpha"},
        id="new key, add to env"
    ),
    pytest.param(
        {"MAGIC": "alpha"},
        "[pytest]\nenv = MAGIC=beta",
        {"MAGIC": "beta"},
        id="key exists in env, overwrite"
    ),
    pytest.param(
        {"MAGIC": "alpha"},
        "[pytest]\nenv = D:MAGIC=beta",
        {"MAGIC": "alpha"},
        id="D exists, original val kept"
    ),
    pytest.param(
        {"PLANET": "world"},
        "[pytest]\nenv = MAGIC=hello_{PLANET}",
        {"MAGIC": "hello_world"},
        id="curly exist, interpolate var"
    ),
    pytest.param(
        {"PLANET": "world"},
        "[pytest]\nenv = R:MAGIC=hello_{PLANET}",
        {"MAGIC": "hello_{PLANET}"},
        id="R exists, not interpolate var"
    ),
    pytest.param(
        {"MAGIC": "a"},
        "[pytest]\nenv = R:MAGIC={MAGIC}b\n D:MAGIC={MAGIC}c\n MAGIC={MAGIC}d",
        {"MAGIC": "{MAGIC}bd"},
        id="incremental interpolation"
    ),
    pytest.param(
        {"MAGIC": "alpha"},
        "[pytest]\nenv = D:R:MAGIC=beta",
        {"MAGIC": "alpha"},
        id="two flags"
    ),
    pytest.param(
        {"MAGIC": "alpha"},
        "[pytest]\nenv = R:D:MAGIC=beta",
        {"MAGIC": "alpha"},
        id="two flags, reversed"
    ),
])
def test_cases(testdir: pytest.Testdir, existing_env_vars: Dict[str, str], ini_contents: str,
               expected_env_vars: Dict[str, str], request: FixtureRequest, generated_dir: Path) -> None:
    # Set preexisting environment variables
    for env_var, val in existing_env_vars.items():
        testdir.monkeypatch.setenv(env_var, val)

    # Write test file to the "generated" folder for debug-ability and cover-ability
    test_name = re.sub(r'\W|^(?=\d)', '_', request.node.callspec.id).lower()
    py_contents = f"""
# WARNING: Do not modify this file. This file was generated and will be overwritten.
from __future__ import annotations

import os


def test_{test_name}() -> None:
    expected_env_vars = {expected_env_vars}
    for key, expected_val in expected_env_vars.items():
        assert os.environ[key] == expected_val, f'Assertion failed for key {{key}}'
    """.lstrip().rstrip(' ')
    src = generated_dir / f"test_{test_name}.py"
    src.write_text(py_contents, encoding="utf-8")

    # Write test files to the temp folder where the test will be run
    dest = Path(str(testdir.tmpdir / f"test_{test_name}.py"))
    dest.symlink_to(src)
    (testdir.tmpdir / "pytest.ini").write_text(ini_contents, encoding="utf-8")

    # Run the test
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.fixture(scope="session")
def generated_dir() -> Path:
    generated_dir = Path(__file__).parent / "generated"
    for pyfile in generated_dir.glob("*.py"):
        pyfile.unlink()
    return generated_dir
