from __future__ import annotations

import os
import re
from pathlib import Path
from unittest import mock

import pytest


@pytest.mark.parametrize(
    ("env", "ini", "expected_env"),
    [
        pytest.param(
            {},
            "[pytest]\nenv = MAGIC=alpha",
            {"MAGIC": "alpha"},
            id="new key - add to env",
        ),
        pytest.param(
            {},
            "[pytest]\nenv = MAGIC=alpha\n SORCERY=beta",
            {"MAGIC": "alpha", "SORCERY": "beta"},
            id="two new keys - add to env",
        ),
        pytest.param(
            # This test also tests for non-interference of env variables between this test and tests above
            {},
            "[pytest]\nenv = d:MAGIC=beta",
            {"MAGIC": "beta"},
            id="D flag - add to env",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = MAGIC=beta",
            {"MAGIC": "beta"},
            id="key exists in env - overwrite",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = D:MAGIC=beta",
            {"MAGIC": "alpha"},
            id="D exists - original val kept",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv = MAGIC=hello_{PLANET}",
            {"MAGIC": "hello_world"},
            id="curly exist - interpolate var",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv = R:MAGIC=hello_{PLANET}",
            {"MAGIC": "hello_{PLANET}"},
            id="R exists - not interpolate var",
        ),
        pytest.param(
            {"MAGIC": "a"},
            "[pytest]\nenv = R:MAGIC={MAGIC}b\n D:MAGIC={MAGIC}c\n MAGIC={MAGIC}d",
            {"MAGIC": "{MAGIC}bd"},
            id="incremental interpolation",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv = D:R:RESULT=hello_{PLANET}",
            {"RESULT": "hello_{PLANET}"},
            id="two flags",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv = R:D:RESULT=hello_{PLANET}",
            {"RESULT": "hello_{PLANET}"},
            id="two flags - reversed",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv = d:r:RESULT=hello_{PLANET}",
            {"RESULT": "hello_{PLANET}"},
            id="lowercase flags",
        ),
        pytest.param(
            {"PLANET": "world"},
            "[pytest]\nenv =  D  :  R  :  RESULT  =  hello_{PLANET}",
            {"RESULT": "hello_{PLANET}"},
            id="whitespace is ignored",
        ),
        pytest.param(
            {"MAGIC": "zero"},
            "",
            {"MAGIC": "zero"},
            id="empty ini works",
        ),
    ],
)
def test_env_via_pytest(
    testdir: pytest.Testdir,
    env: dict[str, str],
    ini: str,
    expected_env: dict[str, str],
    request: pytest.FixtureRequest,
) -> None:
    tmp_dir = Path(str(testdir.tmpdir))
    test_name = re.sub(r"\W|^(?=\d)", "_", request.node.callspec.id).lower()
    Path(str(tmp_dir / f"test_{test_name}.py")).symlink_to(Path(__file__).parent / "template.py")
    (tmp_dir / "pytest.ini").write_text(ini, encoding="utf-8")

    new_env = {
        **env,
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    # monkeypatch persists env variables across parametrized tests, therefore using mock.patch.dict
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = testdir.runpytest()

    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    ("env", "toml", "ini", "expected_env"),
    [
        pytest.param(
            {},
            '[tool.pytest.ini_options]\nenv = ["MAGIC=toml", "MAGIC_2=toml2"]',
            "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            {"MAGIC": "ini", "MAGIC_2": "ini2"},
            id="ini over toml ini_options",
        ),
        pytest.param(
            {},
            '[tool.pytest.ini_options]\nenv = ["MAGIC=toml", "MAGIC_2=toml2"]',
            "",
            {"MAGIC": "toml", "MAGIC_2": "toml2"},
            id="toml via ini_options",
        ),
        pytest.param(
            {},
            '[tool.pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
            "",
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            id="toml native",
        ),
        pytest.param(
            {},
            '[tool.pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
            "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            id="toml native over ini",
        ),
        pytest.param(
            {},
            '[tool.pytest_env]\nMAGIC = {value = "toml", "transform"= true, "skip_if_set" = true}',
            "",
            {"MAGIC": "toml"},
            id="toml inline table",
        ),
    ],
)
def test_env_via_toml(  # noqa: PLR0913, PLR0917
    testdir: pytest.Testdir,
    env: dict[str, str],
    toml: str,
    ini: str,
    expected_env: dict[str, str],
    request: pytest.FixtureRequest,
) -> None:
    tmp_dir = Path(str(testdir.tmpdir))
    test_name = re.sub(r"\W|^(?=\d)", "_", request.node.callspec.id).lower()
    Path(str(tmp_dir / f"test_{test_name}.py")).symlink_to(Path(__file__).parent / "template.py")
    if ini:
        (tmp_dir / "pytest.ini").write_text(ini, encoding="utf-8")
    (tmp_dir / "pyproject.toml").write_text(toml, encoding="utf-8")

    new_env = {
        **env,
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    # monkeypatch persists env variables across parametrized tests, therefore using mock.patch.dict
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = testdir.runpytest()

    result.assert_outcomes(passed=1)


def test_env_via_toml_bad(testdir: pytest.Testdir) -> None:
    toml_file = Path(str(testdir.tmpdir)) / "pyproject.toml"
    toml_file.write_text("bad toml", encoding="utf-8")

    result = testdir.runpytest()
    assert result.ret == 4
    assert result.errlines == [
        f"ERROR: {toml_file}: Expected '=' after a key in a key/value pair (at line 1, column 5)",
        "",
    ]
