from __future__ import annotations

import os
import re
from textwrap import dedent
from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


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
    env_test_template: str,
    env: dict[str, str],
    ini: str,
    expected_env: dict[str, str],
    request: pytest.FixtureRequest,
    mocker: MockerFixture,
) -> None:
    test_name = re.sub(r"\W|^(?=\d)", "_", request.node.callspec.id).lower()
    (pytester.path / f"test_{test_name}.py").write_text(env_test_template, encoding="utf-8")
    (pytester.path / "pytest.ini").write_text(ini, encoding="utf-8")

    new_env = {
        **env,
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    mocker.patch.dict(os.environ, new_env, clear=True)
    pytester.runpytest().assert_outcomes(passed=1)


@pytest.mark.parametrize(
    ("env", "files", "expected_env", "test_dir"),
    [
        pytest.param(
            {},
            {
                "pyproject.toml": '[tool.pytest.ini_options]\nenv = ["MAGIC=toml", "MAGIC_2=toml2"]',
                "pytest.ini": "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            },
            {"MAGIC": "ini", "MAGIC_2": "ini2"},
            ".",
            id="ini over pyproject toml ini_options",
        ),
        pytest.param(
            {},
            {"pyproject.toml": '[tool.pytest.ini_options]\nenv = ["MAGIC=toml", "MAGIC_2=toml2"]'},
            {"MAGIC": "toml", "MAGIC_2": "toml2"},
            ".",
            id="pyproject toml via ini_options",
        ),
        pytest.param(
            {},
            {"pyproject.toml": '[tool.pytest]\nenv = ["MAGIC=toml", "MAGIC_2=toml2"]'},
            {"MAGIC": "toml", "MAGIC_2": "toml2"},
            ".",
            id="pyproject toml via tool.pytest",
        ),
        pytest.param(
            {},
            {"pyproject.toml": '[tool.pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"'},
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            ".",
            id="pyproject toml native",
        ),
        pytest.param(
            {},
            {"pytest.toml": '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"'},
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            ".",
            id="pytest toml",
        ),
        pytest.param(
            {},
            {".pytest.toml": '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"'},
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            ".",
            id="hidden pytest toml",
        ),
        pytest.param(
            {},
            {
                "pyproject.toml": '[tool.pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
                "pytest.ini": "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            },
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            ".",
            id="pyproject toml native over ini",
        ),
        pytest.param(
            {},
            {
                "pytest.toml": '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
                "pytest.ini": "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            },
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            ".",
            id="pytest toml native over ini",
        ),
        pytest.param(
            {},
            {
                ".pytest.toml": '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "toml2"',
                "pytest.ini": "[pytest]\nenv = MAGIC=ini\n MAGIC_2=ini2",
            },
            {"MAGIC": "1", "MAGIC_2": "toml2"},
            ".",
            id="hidden pytest toml native over ini",
        ),
        pytest.param(
            {},
            {"pyproject.toml": "[tool.pytest_env]\n", "pytest.ini": "[pytest]\nenv = FROM_INI=unexpected"},
            {"FROM_INI": None},
            ".",
            id="empty pyproject native over ini",
        ),
        pytest.param(
            {},
            {"pytest.toml": "[pytest_env]\n", "pytest.ini": "[pytest]\nenv = FROM_INI=unexpected"},
            {"FROM_INI": None},
            ".",
            id="empty pytest toml native over ini",
        ),
        pytest.param(
            {},
            {".pytest.toml": "[pytest_env]\n", "pytest.ini": "[pytest]\nenv = FROM_INI=unexpected"},
            {"FROM_INI": None},
            ".",
            id="empty hidden pytest toml native over ini",
        ),
        pytest.param(
            {},
            {"pyproject.toml": '[tool.pytest_env]\nMAGIC = {value = "toml", "transform"= true, "skip_if_set" = true}'},
            {"MAGIC": "toml"},
            ".",
            id="pyproject toml inline table",
        ),
        pytest.param(
            {},
            {"pytest.toml": '[pytest_env]\nMAGIC = {value = "toml", "transform"= true, "skip_if_set" = true}'},
            {"MAGIC": "toml"},
            ".",
            id="pytest toml inline table",
        ),
        pytest.param(
            {},
            {
                "pyproject.toml": '[tool.pytest_env]\nMAGIC = 1\nMAGIC_2 = "pyproject"',
                "pytest.toml": '[pytest_env]\nMAGIC = 1\nMAGIC_2 = "pytest"',
            },
            {"MAGIC": "1", "MAGIC_2": "pytest"},
            ".",
            id="pytest toml over pyproject toml",
        ),
        pytest.param(
            {"MAGIC": "alpha"},
            {"pyproject.toml": "[tool.pytest_env]\nMAGIC = {unset = true}"},
            {"MAGIC": None},
            ".",
            id="pyproject toml unset",
        ),
        pytest.param(
            {},
            {"pyproject.toml": "[tool.pytest_env]\nMAGIC = {unset = true}"},
            {"MAGIC": None},
            ".",
            id="pyproject toml unset non-existing",
        ),
        pytest.param(
            {},
            {
                "pyproject.toml": '[tool.pytest_env]\nMAGIC = "parent"',
                "sub/pytest.toml": '[pytest_env]\nMAGIC = "child"',
            },
            {"MAGIC": "child"},
            "sub",
            id="subdir pytest toml over parent pyproject toml",
        ),
    ],
)
def test_env_via_toml(
    pytester: pytest.Pytester,
    env_test_template: str,
    env: dict[str, str],
    files: dict[str, str],
    expected_env: dict[str, str],
    test_dir: str,
    request: pytest.FixtureRequest,
    mocker: MockerFixture,
) -> None:
    test_name = re.sub(r"\W|^(?=\d)", "_", request.node.callspec.id).lower()
    for name, content in files.items():
        (pytester.path / name).parent.mkdir(parents=True, exist_ok=True)
        (pytester.path / name).write_text(content, encoding="utf-8")
    (pytester.path / test_dir / f"test_{test_name}.py").write_text(env_test_template, encoding="utf-8")

    new_env = {
        **env,
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }
    mocker.patch.dict(os.environ, new_env, clear=True)
    pytester.runpytest(str(pytester.path / test_dir)).assert_outcomes(passed=1)


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
            {"MAGIC": "original"},
            "MAGIC=from_file",
            dedent("""\
                [tool.pytest_env]
                env_files = [".env"]
                env_files_skip_if_set = true
            """),
            {"MAGIC": "original"},
            "pyproject",
            id="env_files_skip_if_set pyproject",
        ),
        pytest.param(
            {"MAGIC": "original"},
            "MAGIC=from_file",
            dedent("""\
                [pytest]
                env_files = .env
                env_files_skip_if_set = true
            """),
            {"MAGIC": "original"},
            "ini",
            id="env_files_skip_if_set ini",
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
def test_env_via_env_file(
    pytester: pytest.Pytester,
    env_test_template: str,
    env: dict[str, str],
    env_file_content: str,
    config: str,
    expected_env: dict[str, str | None],
    config_type: str,
    request: pytest.FixtureRequest,
    mocker: MockerFixture,
) -> None:
    test_name = re.sub(r"\W|^(?=\d)", "_", request.node.callspec.id).lower()
    (pytester.path / f"test_{test_name}.py").write_text(env_test_template, encoding="utf-8")
    (pytester.path / ".env").write_text(env_file_content, encoding="utf-8")
    config_file_names = {"pyproject": "pyproject.toml", "pytest.toml": "pytest.toml", "ini": "pytest.ini"}
    (pytester.path / config_file_names[config_type]).write_text(config, encoding="utf-8")

    new_env = {
        **env,
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    mocker.patch.dict(os.environ, new_env, clear=True)
    pytester.runpytest().assert_outcomes(passed=1)


@pytest.mark.parametrize(
    ("config_content", "config_file"),
    [
        pytest.param(
            "[pytest]\nenv = MAGIC=alpha",
            "pytest.ini",
            id="ini",
        ),
        pytest.param(
            '[tool.pytest_env]\nMAGIC = "alpha"',
            "pyproject.toml",
            id="pyproject toml",
        ),
        pytest.param(
            '[pytest_env]\nMAGIC = "alpha"',
            "pytest.toml",
            id="pytest toml",
        ),
    ],
)
def test_conftest_import_uses_env(
    pytester: pytest.Pytester,
    config_content: str,
    config_file: str,
    mocker: MockerFixture,
) -> None:
    (pytester.path / config_file).write_text(config_content, encoding="utf-8")
    (pytester.path / "app_config.py").write_text(
        dedent("""\
            import os

            VALUE = os.environ['MAGIC']
        """),
        encoding="utf-8",
    )
    pytester.makeconftest("from app_config import VALUE")
    pytester.makepyfile(
        test_it=dedent("""\
            from conftest import VALUE

            def test_it() -> None:
                assert VALUE == 'alpha'
        """),
    )

    new_env = {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTEST_PLUGINS": "pytest_env.plugin"}
    mocker.patch.dict(os.environ, new_env, clear=True)
    pytester.runpytest().assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "toml_name",
    [
        pytest.param("pytest.toml", id="pytest-toml"),
        pytest.param(".pytest.toml", id="hidden-pytest-toml"),
        pytest.param("pyproject.toml", id="pyproject-toml"),
    ],
)
def test_env_via_pyproject_toml_bad(pytester: pytest.Pytester, toml_name: str) -> None:
    toml_file = pytester.path / toml_name
    toml_file.write_text("bad toml", encoding="utf-8")

    result = pytester.runpytest()
    assert (result.ret, result.errlines) == (
        4,
        [f"ERROR: {toml_file}: Expected '=' after a key in a key/value pair (at line 1, column 5)", ""],
    )


@pytest.mark.parametrize(
    ("files", "cli_arg", "expected_env"),
    [
        pytest.param(
            {
                "cli.env": "MAGIC=from_cli",
                ".env": "MAGIC=from_env",
                "pyproject.toml": '[tool.pytest_env]\nenv_files = [".env"]',
            },
            "cli.env",
            {"MAGIC": "from_cli"},
            id="override mode",
        ),
        pytest.param(
            {
                "cli.env": "MAGIC=from_cli",
                ".env": "MAGIC=from_env\nEXTRA=config",
                "pyproject.toml": '[tool.pytest_env]\nenv_files = [".env"]',
            },
            "+cli.env",
            {"MAGIC": "from_cli", "EXTRA": "config"},
            id="extend mode",
        ),
        pytest.param(
            {"cli.env": "MAGIC=from_cli"},
            "cli.env",
            {"MAGIC": "from_cli"},
            id="no config files override",
        ),
        pytest.param(
            {"cli.env": "MAGIC=from_cli"},
            "+cli.env",
            {"MAGIC": "from_cli"},
            id="no config files extend",
        ),
        pytest.param(
            {
                "cli.env": "EXTRA=from_cli",
                ".env": "MAGIC=from_env",
                "pyproject.toml": '[tool.pytest_env]\nenv_files = [".env", "missing.env"]',
            },
            "+cli.env",
            {"MAGIC": "from_env", "EXTRA": "from_cli"},
            id="extend with missing config file",
        ),
    ],
)
def test_envfile_cli(
    pytester: pytest.Pytester,
    env_test_template: str,
    files: dict[str, str],
    cli_arg: str,
    expected_env: dict[str, str],
    mocker: MockerFixture,
) -> None:
    (pytester.path / "test_cli.py").write_text(env_test_template, encoding="utf-8")
    for name, content in files.items():
        (pytester.path / name).write_text(content, encoding="utf-8")

    new_env = {
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    mocker.patch.dict(os.environ, new_env, clear=True)
    pytester.runpytest("--envfile", cli_arg).assert_outcomes(passed=1)


def test_envfile_cli_skip_if_set(pytester: pytest.Pytester, env_test_template: str, mocker: MockerFixture) -> None:
    (pytester.path / "test_cli_skip.py").write_text(env_test_template, encoding="utf-8")
    (pytester.path / "cli.env").write_text("MAGIC=from_cli", encoding="utf-8")
    (pytester.path / "pyproject.toml").write_text(
        dedent("""\
            [tool.pytest_env]
            env_files_skip_if_set = true
        """),
        encoding="utf-8",
    )

    expected_env = {"MAGIC": "original"}
    new_env = {
        "MAGIC": "original",
        "_TEST_ENV": repr(expected_env),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    mocker.patch.dict(os.environ, new_env, clear=True)
    pytester.runpytest("--envfile", "cli.env").assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "cli_arg",
    [
        pytest.param("nonexistent.env", id="missing file override"),
        pytest.param("+nonexistent.env", id="missing file extend"),
    ],
)
def test_envfile_cli_missing_file(pytester: pytest.Pytester, cli_arg: str, mocker: MockerFixture) -> None:
    pytester.makepyfile(test_it="def test_it() -> None:\n    pass")

    new_env = {
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }

    mocker.patch.dict(os.environ, new_env, clear=True)
    result = pytester.runpytest("--envfile", cli_arg)

    assert result.ret != 0
    error_file = cli_arg.lstrip("+")
    assert any(f"Environment file not found: {error_file}" in line for line in result.errlines)


@pytest.mark.parametrize(
    "config_name",
    [
        pytest.param("pytest.toml", id="pytest-toml"),
        pytest.param(".pytest.toml", id="hidden-pytest-toml"),
    ],
)
@pytest.mark.parametrize(
    "fallback_dir",
    [
        pytest.param("child", id="sibling"),
        pytest.param(".", id="parent"),
    ],
)
def test_pyproject_env_with_native_pytest_config(
    pytester: pytest.Pytester, child: Path, config_name: str, fallback_dir: str
) -> None:
    (child / config_name).write_text('[pytest]\naddopts = ["-q"]\n', encoding="utf-8")
    (pytester.path / fallback_dir / "pyproject.toml").write_text(
        '[tool.pytest_env]\nNATIVE_CONFIG_ENV = "configured"\n', encoding="utf-8"
    )
    (child / "test_configured_env.py").write_text(
        'import os\ndef test_env() -> None:\n    assert os.environ["NATIVE_CONFIG_ENV"] == "configured"\n',
        encoding="utf-8",
    )
    result: Final[pytest.RunResult] = pytester.runpytest(str(child))
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.OK


@pytest.mark.parametrize(
    ("config_name", "section", "fallback_name", "fallback_section"),
    [
        pytest.param("pytest.toml", "pytest_env", "pyproject.toml", "tool.pytest_env", id="pytest-toml"),
        pytest.param(".pytest.toml", "pytest_env", "pyproject.toml", "tool.pytest_env", id="hidden-pytest-toml"),
        pytest.param("pyproject.toml", "tool.pytest_env", "pytest.toml", "pytest_env", id="pyproject-toml"),
    ],
)
@pytest.mark.parametrize(
    "empty_section",
    [pytest.param("", id="empty-table"), pytest.param("env_files = []\n", id="empty-env-files")],
)
@pytest.mark.parametrize(
    "fallback_dir",
    [
        pytest.param("child", id="sibling"),
        pytest.param(".", id="parent"),
    ],
)
def test_empty_env_section_stops_discovery(
    pytester: pytest.Pytester,
    child: Path,
    config_name: str,
    section: str,
    fallback_name: str,
    fallback_section: str,
    empty_section: str,
    fallback_dir: str,
) -> None:
    (child / config_name).write_text(f"[{section}]\n{empty_section}", encoding="utf-8")
    (pytester.path / fallback_dir / fallback_name).write_text(
        f'[{fallback_section}]\nPYTEST_ENV_INHERITED = "parent-value"\n', encoding="utf-8"
    )
    (child / "test_configured_env.py").write_text(
        'import os\ndef test_env() -> None:\n    assert "PYTEST_ENV_INHERITED" not in os.environ\n', encoding="utf-8"
    )
    result: Final[pytest.RunResult] = pytester.runpytest("-c", str(child / config_name), str(child))
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.OK


@pytest.fixture
def child(pytester: pytest.Pytester, mocker: MockerFixture) -> Path:
    mocker.patch.dict(
        os.environ,
        {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTEST_PLUGINS": "pytest_env.plugin"},
        clear=True,
    )
    child: Final[Path] = pytester.path / "child"
    child.mkdir()
    return child


@pytest.mark.parametrize(
    ("files", "expected_ini"),
    [
        pytest.param(
            {"pytest.toml": '[pytest_env]\n\n[pytest]\nenv_files = ["fallback.env"]\n'},
            "from_ini",
            id="pytest-toml-omitted",
        ),
        pytest.param(
            {"pytest.toml": '[pytest_env]\nenv_files = []\n\n[pytest]\nenv_files = ["fallback.env"]\n'},
            None,
            id="pytest-toml-empty",
        ),
        pytest.param(
            {".pytest.toml": '[pytest_env]\n\n[pytest]\nenv_files = ["fallback.env"]\n'},
            "from_ini",
            id="hidden-pytest-toml-omitted",
        ),
        pytest.param(
            {".pytest.toml": '[pytest_env]\nenv_files = []\n\n[pytest]\nenv_files = ["fallback.env"]\n'},
            None,
            id="hidden-pytest-toml-empty",
        ),
        pytest.param(
            {"pyproject.toml": "[tool.pytest_env]\n", "tox.ini": "[pytest]\nenv_files = fallback.env\n"},
            "from_ini",
            id="pyproject-toml-omitted",
        ),
        pytest.param(
            {
                "pyproject.toml": "[tool.pytest_env]\nenv_files = []\n",
                "tox.ini": "[pytest]\nenv_files = fallback.env\n",
            },
            None,
            id="pyproject-toml-empty",
        ),
    ],
)
@pytest.mark.parametrize(
    ("cli_args", "expected_cli", "python_env", "expected_python"),
    [
        pytest.param((), None, {}, (False, None), id="config-only-unset"),
        pytest.param(
            (),
            None,
            {"PYTHONPATH": "pythonpath_marker", "PYTHONDONTWRITEBYTECODE": "1"},
            (True, "1"),
            id="config-only-set",
        ),
        pytest.param(("--envfile", "+cli.env"), "from_cli", {}, (False, None), id="cli-extend-unset"),
        pytest.param(
            ("--envfile", "+cli.env"),
            "from_cli",
            {"PYTHONPATH": "pythonpath_marker", "PYTHONDONTWRITEBYTECODE": "1"},
            (True, "1"),
            id="cli-extend-set",
        ),
    ],
)
def test_native_env_files_override_ini(
    pytester: pytest.Pytester,
    mocker: MockerFixture,
    files: dict[str, str],
    expected_ini: str | None,
    cli_args: tuple[str, ...],
    expected_cli: str | None,
    python_env: dict[str, str],
    expected_python: tuple[bool, str | None],
) -> None:
    (pytester.path / "fallback.env").write_text("INHERITED=from_ini\n", encoding="utf-8")
    (pytester.path / "cli.env").write_text("FROM_CLI=from_cli\n", encoding="utf-8")
    for name, content in files.items():
        (pytester.path / name).write_text(content, encoding="utf-8")
    expected_env: Final[tuple[str | None, str | None, bool, str | None]] = (
        expected_ini,
        expected_cli,
        *expected_python,
    )
    pytester.makepyfile(
        test_env=dedent(f"""\
            import os

            def test_env() -> None:
                assert (
                    os.environ.get("INHERITED"),
                    os.environ.get("FROM_CLI"),
                    "pythonpath_marker" in os.environ.get("PYTHONPATH", "").split(os.pathsep),
                    os.environ.get("PYTHONDONTWRITEBYTECODE"),
                ) == {expected_env!r}
        """),
    )
    system_env: Final[dict[str, str]] = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR") if key in os.environ}
    mocker.patch.dict(
        os.environ,
        {
            **system_env,
            **python_env,
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTEST_PLUGINS": "pytest_env.plugin",
        },
        clear=True,
    )
    pytester.runpytest_subprocess(*cli_args).assert_outcomes(passed=1)


@pytest.mark.parametrize(
    ("file_key", "expected", "action"),
    [
        pytest.param("PYTEST_ENV_CASE", "original", "SKIP", id="same-case"),
        pytest.param(
            "pytest_env_case",
            "original" if os.name == "nt" else "from_file",
            "SKIP" if os.name == "nt" else "SET",
            id="different-case",
        ),
    ],
)
def test_env_files_skip_if_set_respects_platform_case(
    pytester: pytest.Pytester, file_key: str, expected: str, action: str, mocker: MockerFixture
) -> None:
    (pytester.path / ".env").write_text(f"{file_key}=from_file\n", encoding="utf-8")
    (pytester.path / "pytest.ini").write_text(
        "[pytest]\nenv_files = .env\nenv_files_skip_if_set = true\n", encoding="utf-8"
    )
    pytester.makepyfile(
        test_case=(
            f'import os\ndef test_case() -> None:\n    assert os.environ["{file_key}"] == {expected!r}\n'
            '    assert os.environ["PYTEST_ENV_CASE"] == "original"\n'
        )
    )
    mocker.patch.dict(
        os.environ,
        {
            "PYTEST_ENV_CASE": "original",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTEST_PLUGINS": "pytest_env.plugin",
        },
        clear=True,
    )
    result: Final[pytest.RunResult] = pytester.runpytest("--pytest-env-verbose")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([f"*{action}*{file_key}={expected}*(from*.env*"])


def test_verbose_envfile_without_config(pytester: pytest.Pytester, mocker: MockerFixture) -> None:
    (pytester.path / "cli.env").write_text("MAGIC=from_cli\n", encoding="utf-8")
    pytester.makepyfile(
        test_verbose_cli_env='import os\ndef test_env() -> None:\n    assert os.environ["MAGIC"] == "from_cli"\n'
    )
    mocker.patch.dict(
        os.environ,
        {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTEST_PLUGINS": "pytest_env.plugin"},
        clear=True,
    )

    result = pytester.runpytest("--pytest-env-verbose", "--envfile", "cli.env")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*pytest-env:", "*SET*MAGIC=from_cli*(from*cli.env*"])
