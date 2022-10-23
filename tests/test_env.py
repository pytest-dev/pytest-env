from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("env", "ini", "expected_env"),
    [
        pytest.param(
            {},
            "[pytest]\nenv = MAGIC=alpha",
            {"MAGIC": "alpha"},
            id="When ini has a new key, Then it is added to env",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = MAGIC=beta",
            {"MAGIC": "beta"},
            id="When ini has a key which already exists in env, Then the env value is overwritten",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = D:MAGIC=beta",
            {"MAGIC": "alpha"},
            id="Given D flag, When ini has a key which already exists in env, Then the original env value is kept",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv = MAGIC=hello_{PLANET}",
            {"MAGIC": "hello_world"},
            id="When ini value has an env key between curly braces, Then the key's value is interpolated",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv = R:MAGIC=hello_{PLANET}",
            {"MAGIC": "hello_{PLANET}"},
            id="When ini key has R flag, Then ini value is not interpolated",
        ),
        pytest.param(
            {"MAGIC": "a"},
            "[pytest]\nenv = R:MAGIC={MAGIC}b\n D:MAGIC={MAGIC}c\n MAGIC={MAGIC}d",
            {"MAGIC": "{MAGIC}bd"},
            id="When ini has repeating keys, Then values and flags are evaluated separately and incrementally",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = D:R:MAGIC=beta",
            {"MAGIC": "alpha"},
            id="When ini key has two flags, Then both are applied",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = R:D:MAGIC=beta",
            {"MAGIC": "alpha"},
            id="When ini key has two flags (in reverse order), Then both are applied",
        ),
    ],
)
def test_env(testdir: pytest.Testdir, env: dict[str, str], ini: str, expected_env: dict[str, str]) -> None:
    for env_var, val in env.items():
        testdir.monkeypatch.setenv(env_var, val)
    testdir.monkeypatch.setenv("_TEST_ENV", repr(expected_env))

    Path(str(testdir.tmpdir / "test_example.py")).symlink_to(Path(__file__).parent / "example.py")
    (testdir.tmpdir / "pytest.ini").write_text(ini, encoding="utf-8")

    result = testdir.runpytest()
    result.assert_outcomes(passed=1)
