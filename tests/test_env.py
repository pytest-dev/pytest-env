from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("env", "ini", "expected_env"),
    [
        pytest.param(
            {},  # empty dict means no preexisting environment variables
            "[pytest]\nenv = MAGIC=alpha",
            {"MAGIC": "alpha"},
            id="new key, add to env",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = MAGIC=beta",
            {"MAGIC": "beta"},
            id="key exists in env, overwrite",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = D:MAGIC=beta",
            {"MAGIC": "alpha"},
            id="D exists, original val kept",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv = MAGIC=hello_{PLANET}",
            {"MAGIC": "hello_world"},
            id="curly exist, interpolate var",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv = R:MAGIC=hello_{PLANET}",
            {"MAGIC": "hello_{PLANET}"},
            id="R exists, not interpolate var",
        ),
        pytest.param(
            {"MAGIC": "a"},
            "[pytest]\nenv = R:MAGIC={MAGIC}b\n D:MAGIC={MAGIC}c\n MAGIC={MAGIC}d",
            {"MAGIC": "{MAGIC}bd"},
            id="incremental interpolation",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = D:R:MAGIC=beta",
            {"MAGIC": "alpha"},
            id="two flags",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = R:D:MAGIC=beta",
            {"MAGIC": "alpha"},
            id="two flags, reversed",
        ),
    ],
)
def test_env(testdir: pytest.Testdir, env: dict[str, str], ini: str, expected_env: dict[str, str],
             request: pytest.FixtureRequest) -> None:
    for env_var, val in env.items():
        testdir.monkeypatch.setenv(env_var, val)
    testdir.monkeypatch.setenv("_TEST_ENV", repr(expected_env))

    test_name = re.sub(r'\W|^(?=\d)', '_', request.node.callspec.id).lower()
    Path(str(testdir.tmpdir / f"test_{test_name}.py")).symlink_to(Path(__file__).parent / "template.py")
    (testdir.tmpdir / "pytest.ini").write_text(ini, encoding="utf-8")

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)
