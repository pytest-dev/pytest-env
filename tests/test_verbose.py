from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING
from unittest import mock

if TYPE_CHECKING:
    import pytest


def test_verbose_shows_set_from_ini(pytester: pytest.Pytester) -> None:
    (pytester.path / "test_it.py").symlink_to(Path(__file__).parent / "template.py")
    (pytester.path / "pytest.ini").write_text("[pytest]\nenv = MAGIC=alpha", encoding="utf-8")

    new_env = {
        "_TEST_ENV": repr({"MAGIC": "alpha"}),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest("--pytest-env-verbose")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*pytest-env:*", "*SET*MAGIC=alpha*"])


def test_verbose_shows_set_from_toml(pytester: pytest.Pytester) -> None:
    (pytester.path / "test_it.py").symlink_to(Path(__file__).parent / "template.py")
    (pytester.path / "pyproject.toml").write_text(
        '[tool.pytest_env]\nMY_VAR = "hello"',
        encoding="utf-8",
    )

    new_env = {
        "_TEST_ENV": repr({"MY_VAR": "hello"}),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest("--pytest-env-verbose")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*pytest-env:*", "*SET*MY_VAR=hello*(from*pyproject.toml*"])


def test_verbose_shows_set_from_env_file(pytester: pytest.Pytester) -> None:
    (pytester.path / "test_it.py").symlink_to(Path(__file__).parent / "template.py")
    (pytester.path / ".env").write_text("FROM_FILE=value", encoding="utf-8")
    (pytester.path / "pyproject.toml").write_text(
        '[tool.pytest_env]\nenv_files = [".env"]',
        encoding="utf-8",
    )

    new_env = {
        "_TEST_ENV": repr({"FROM_FILE": "value"}),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest("--pytest-env-verbose")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*SET*FROM_FILE=value*(from*.env*"])


def test_verbose_shows_skip(pytester: pytest.Pytester) -> None:
    (pytester.path / "test_it.py").symlink_to(Path(__file__).parent / "template.py")
    (pytester.path / "pytest.ini").write_text("[pytest]\nenv = D:EXISTING=new", encoding="utf-8")

    new_env = {
        "EXISTING": "original",
        "_TEST_ENV": repr({"EXISTING": "original"}),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest("--pytest-env-verbose")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*SKIP*EXISTING=original*"])


def test_verbose_shows_unset(pytester: pytest.Pytester) -> None:
    (pytester.path / "test_it.py").symlink_to(Path(__file__).parent / "template.py")
    (pytester.path / "pytest.ini").write_text("[pytest]\nenv = U:TO_REMOVE", encoding="utf-8")

    new_env = {
        "TO_REMOVE": "gone",
        "_TEST_ENV": repr({"TO_REMOVE": None}),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest("--pytest-env-verbose")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*UNSET*TO_REMOVE*"])


def test_verbose_shows_transform(pytester: pytest.Pytester) -> None:
    (pytester.path / "test_it.py").symlink_to(Path(__file__).parent / "template.py")
    (pytester.path / "pyproject.toml").write_text(
        dedent("""\
            [tool.pytest_env]
            GREETING = {value = "hello_{PLANET}", transform = true}
        """),
        encoding="utf-8",
    )

    new_env = {
        "PLANET": "world",
        "_TEST_ENV": repr({"GREETING": "hello_world"}),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest("--pytest-env-verbose")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*SET*GREETING=hello_world*"])


def test_no_verbose_output_without_flag(pytester: pytest.Pytester) -> None:
    (pytester.path / "test_it.py").symlink_to(Path(__file__).parent / "template.py")
    (pytester.path / "pytest.ini").write_text("[pytest]\nenv = MAGIC=alpha", encoding="utf-8")

    new_env = {
        "_TEST_ENV": repr({"MAGIC": "alpha"}),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest()

    result.assert_outcomes(passed=1)
    result.stdout.no_fnmatch_line("*pytest-env:*")


def test_verbose_multiple_sources(pytester: pytest.Pytester) -> None:
    (pytester.path / "test_it.py").symlink_to(Path(__file__).parent / "template.py")
    (pytester.path / ".env").write_text("FROM_FILE=file_val", encoding="utf-8")
    (pytester.path / "pyproject.toml").write_text(
        dedent("""\
            [tool.pytest_env]
            env_files = [".env"]
            INLINE = "inline_val"
        """),
        encoding="utf-8",
    )

    new_env = {
        "_TEST_ENV": repr({"FROM_FILE": "file_val", "INLINE": "inline_val"}),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_PLUGINS": "pytest_env.plugin",
    }
    with mock.patch.dict(os.environ, new_env, clear=True):
        result = pytester.runpytest("--pytest-env-verbose")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([
        "*SET*FROM_FILE=file_val*(from*.env*",
        "*SET*INLINE=inline_val*(from*pyproject.toml*",
    ])
