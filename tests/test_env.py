from __future__ import annotations

import os
import re
from pathlib import Path
from unittest import mock

import pytest

from pytest_env.plugin import _load_toml_config  # noqa: PLC2701


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
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = U:MAGIC",
            {"MAGIC": None},
            id="U flag - unset existing var",
        ),
        pytest.param(
            {},
            "[pytest]\nenv = U:MAGIC",
            {"MAGIC": None},
            id="U flag - unset non-existing var",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[pytest]\nenv = U:MAGIC\n MAGIC=beta",
            {"MAGIC": "beta"},
            id="U flag then set - var is set",
        ),
    ],
)
def test_env_via_pytest(
    pytester: pytest.Pytester,
    env: dict[str, str],
    ini: str,
    expected_env: dict[str, str],
    request: pytest.FixtureRequest,
) -> None:
    test_name = re.sub(r"\W|^(?=\d)", "_", request.node.callspec.id).lower()
    (pytester.path / f"test_{test_name}.py").symlink_to(Path(__file__).parent / "template.py")
    (pytester.path / "pytest.ini").write_text(ini, encoding="utf-8")

    new_env = {
        **env,
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest()

    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    ("env", "pyproject_toml", "pytest_toml", "ini", "expected_env", "pytest_toml_name"),
    [
        pytest.param(
            {},
            '[tool.pytest.ini_options]\nenv = ["MAGIC=toml", "MAGIC_2=toml2"]',
            "",
            "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            {"MAGIC": "ini", "MAGIC_2": "ini2"},
            None,
            id="ini over pyproject toml ini_options",
        ),
        pytest.param(
            {},
            '[tool.pytest.ini_options]\nenv = ["MAGIC=toml", "MAGIC_2=toml2"]',
            "",
            "",
            {"MAGIC": "toml", "MAGIC_2": "toml2"},
            None,
            id="pyproject toml via ini_options",
        ),
        pytest.param(
            {},
            '[tool.pytest]\nenv = ["MAGIC=toml", "MAGIC_2=toml2"]',
            "",
            "",
            {"MAGIC": "toml", "MAGIC_2": "toml2"},
            None,
            id="pyproject toml via tool.pytest",
        ),
        pytest.param(
            {},
            '[tool.pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
            "",
            "",
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            None,
            id="pyproject toml native",
        ),
        pytest.param(
            {},
            "",
            '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
            "",
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            "pytest.toml",
            id="pytest toml",
        ),
        pytest.param(
            {},
            "",
            '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
            "",
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            ".pytest.toml",
            id="hidden pytest toml",
        ),
        pytest.param(
            {},
            '[tool.pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
            "",
            "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            None,
            id="pyproject toml native over ini",
        ),
        pytest.param(
            {},
            "",
            '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
            "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            "pytest.toml",
            id="pytest toml native over ini",
        ),
        pytest.param(
            {},
            "",
            '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
            "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            ".pytest.toml",
            id="hidden pytest toml native over ini",
        ),
        pytest.param(
            {},
            '[tool.pytest_env]\nMAGIC = {value = "toml", "transform"= true, "skip_if_set" = true}',
            "",
            "",
            {"MAGIC": "toml"},
            None,
            id="pyproject toml inline table",
        ),
        pytest.param(
            {},
            "",
            '[pytest_env]\nMAGIC = {value = "toml", "transform"= true, "skip_if_set" = true}',
            "",
            {"MAGIC": "toml"},
            "pytest.toml",
            id="pytest toml inline table",
        ),
        pytest.param(
            {},
            '[tool.pytest_env]\nMAGIC = 1\nMAGIC_2 = "pyproject"',
            '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "pytest"',
            "",
            {"MAGIC": "1", "MAGIC_2": "pytest"},
            "pytest.toml",
            id="pytest toml over pyproject toml",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            "[tool.pytest_env]\nMAGIC = {unset = true}",
            "",
            "",
            {"MAGIC": None},
            None,
            id="pyproject toml unset",
        ),
        pytest.param(
            {},
            "[tool.pytest_env]\nMAGIC = {unset = true}",
            "",
            "",
            {"MAGIC": None},
            None,
            id="pyproject toml unset non-existing",
        ),
        pytest.param(
            {},
            '[tool.pytest_env]\nMAGIC = "parent"',
            '[pytest_env]\nMAGIC = "child"',
            "",
            {"MAGIC": "child"},
            "sub/pytest.toml",
            id="subdir pytest toml over parent pyproject toml",
        ),
    ],
)
def test_env_via_toml(  # noqa: PLR0913, PLR0917
    pytester: pytest.Pytester,
    env: dict[str, str],
    pyproject_toml: str,
    pytest_toml: str,
    ini: str,
    expected_env: dict[str, str],
    pytest_toml_name: str | None,
    request: pytest.FixtureRequest,
) -> None:
    test_name = re.sub(r"\W|^(?=\d)", "_", request.node.callspec.id).lower()
    if pyproject_toml:
        (pytester.path / "pyproject.toml").write_text(pyproject_toml, encoding="utf-8")
    if pytest_toml and pytest_toml_name:
        toml_path = pytester.path / pytest_toml_name
        toml_path.parent.mkdir(parents=True, exist_ok=True)
        toml_path.write_text(pytest_toml, encoding="utf-8")

    if pytest_toml_name and "/" in pytest_toml_name:
        test_dir = pytester.path / Path(pytest_toml_name).parent
    else:
        test_dir = pytester.path
        if ini:
            (pytester.path / "pytest.ini").write_text(ini, encoding="utf-8")

    (test_dir / f"test_{test_name}.py").symlink_to(Path(__file__).parent / "template.py")

    new_env = {
        **env,
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest(str(test_dir))

    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    ("env", "env_file_content", "config", "expected_env", "config_type"),
    [
        pytest.param(
            {},
            "MAGIC=alpha\nSORCERY=beta",
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"MAGIC": "alpha", "SORCERY": "beta"},
            "pyproject",
            id="basic env file via pyproject toml",
        ),
        pytest.param(
            {},
            "MAGIC=alpha\nSORCERY=beta",
            '[pytest_env]\nenv_files = [".env"]',
            {"MAGIC": "alpha", "SORCERY": "beta"},
            "pytest.toml",
            id="basic env file via pytest toml",
        ),
        pytest.param(
            {},
            "MAGIC=alpha\nSORCERY=beta",
            "[pytest]\nenv_files = .env",
            {"MAGIC": "alpha", "SORCERY": "beta"},
            "ini",
            id="basic env file via ini",
        ),
        pytest.param(
            {},
            "# comment line\n\nMAGIC=alpha\n  # indented comment\n",
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"MAGIC": "alpha"},
            "pyproject",
            id="comments and blank lines",
        ),
        pytest.param(
            {},
            "SINGLE='hello world'\nDOUBLE=\"hello world\"",
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"SINGLE": "hello world", "DOUBLE": "hello world"},
            "pyproject",
            id="quoted values",
        ),
        pytest.param(
            {},
            "MAGIC=alpha",
            '[tool.pytest_env]\nenv_files = [".env"]\nMAGIC = "beta"',
            {"MAGIC": "beta"},
            "pyproject",
            id="inline overrides env file",
        ),
        pytest.param(
            {},
            "",
            '[tool.pytest_env]\nenv_files = ["missing.env"]',
            {},
            "pyproject",
            id="missing env file is skipped",
        ),
        pytest.param(
            {},
            "KEY_ONLY\nVALID=yes",
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"VALID": "yes"},
            "pyproject",
            id="line without equals is skipped",
        ),
        pytest.param(
            {},
            "MAGIC=has=equals",
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"MAGIC": "has=equals"},
            "pyproject",
            id="value with equals sign",
        ),
        pytest.param(
            {},
            "  MAGIC  =  alpha  ",
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"MAGIC": "alpha"},
            "pyproject",
            id="whitespace around key and value",
        ),
        pytest.param(
            {"MAGIC": "original"},
            "MAGIC=from_file",
            '[tool.pytest_env]\nenv_files = [".env"]\nMAGIC = {value = "from_file", skip_if_set = true}',
            {"MAGIC": "from_file"},
            "pyproject",
            id="skip if set respects env file",
        ),
        pytest.param(
            {},
            "=no_key\nVALID=yes",
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"VALID": "yes"},
            "pyproject",
            id="empty key is skipped",
        ),
        pytest.param(
            {},
            "",
            '[tool.pytest_env]\nenv_files = "some_value"',
            {"env_files": "some_value"},
            "pyproject",
            id="env_files as env var when string",
        ),
        pytest.param(
            {},
            "export MAGIC=alpha",
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"MAGIC": "alpha"},
            "pyproject",
            id="export prefix",
        ),
        pytest.param(
            {},
            'MAGIC="hello\\nworld"',
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"MAGIC": "hello\nworld"},
            "pyproject",
            id="escape sequences in double quotes",
        ),
        pytest.param(
            {},
            "MAGIC=alpha #comment",
            '[tool.pytest_env]\nenv_files = [".env"]',
            {"MAGIC": "alpha"},
            "pyproject",
            id="inline comment",
        ),
    ],
)
def test_env_via_env_file(  # noqa: PLR0913, PLR0917
    pytester: pytest.Pytester,
    env: dict[str, str],
    env_file_content: str,
    config: str,
    expected_env: dict[str, str | None],
    config_type: str,
    request: pytest.FixtureRequest,
) -> None:
    test_name = re.sub(r"\W|^(?=\d)", "_", request.node.callspec.id).lower()
    (pytester.path / f"test_{test_name}.py").symlink_to(Path(__file__).parent / "template.py")
    if env_file_content:
        (pytester.path / ".env").write_text(env_file_content, encoding="utf-8")
    config_file_names = {"pyproject": "pyproject.toml", "pytest.toml": "pytest.toml", "ini": "pytest.ini"}
    (pytester.path / config_file_names[config_type]).write_text(config, encoding="utf-8")

    new_env = {
        **env,
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest()

    result.assert_outcomes(passed=1)


def test_env_files_from_toml_bad_toml(tmp_path: Path) -> None:
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text("bad toml", encoding="utf-8")
    with pytest.raises(Exception, match="Expected '=' after a key"):
        _load_toml_config(toml_file)


@pytest.mark.parametrize("toml_name", ["pytest.toml", ".pytest.toml", "pyproject.toml"])
def test_env_via_pyproject_toml_bad(pytester: pytest.Pytester, toml_name: str) -> None:
    toml_file = pytester.path / toml_name
    toml_file.write_text("bad toml", encoding="utf-8")

    result = pytester.runpytest()
    assert result.ret == 4
    assert result.errlines == [
        f"ERROR: {toml_file}: Expected '=' after a key in a key/value pair (at line 1, column 5)",
        "",
    ]
