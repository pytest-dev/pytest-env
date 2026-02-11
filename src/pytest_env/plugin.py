"""Adopt environment section in pytest configuration files."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, Any

import pytest
from dotenv import dotenv_values

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator
    from pathlib import Path

if sys.version_info >= (3, 11):  # pragma: >=3.11 cover
    import tomllib
else:  # pragma: <3.11 cover
    import tomli as tomllib


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add section to configuration files."""
    help_msg = "a line separated list of environment variables of the form (FLAG:)NAME=VALUE"
    parser.addini("env", type="linelist", help=help_msg, default=[])
    parser.addini("env_files", type="linelist", help="a line separated list of .env files to load", default=[])


@dataclass
class Entry:
    """Configuration entries."""

    key: str
    value: str
    transform: bool
    skip_if_set: bool
    unset: bool = False


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(
    args: list[str],  # noqa: ARG001
    early_config: pytest.Config,
    parser: pytest.Parser,  # noqa: ARG001
) -> None:
    """Load environment variables from configuration files."""
    for env_file in _load_env_files(early_config):
        for key, value in dotenv_values(env_file).items():
            if value is not None:
                os.environ[key] = value
    for entry in _load_values(early_config):
        if entry.unset:
            os.environ.pop(entry.key, None)
        elif entry.skip_if_set and entry.key in os.environ:
            continue
        else:
            # transformation -> replace environment variables, e.g. TEST_DIR={USER}/repo_test_dir.
            os.environ[entry.key] = entry.value.format(**os.environ) if entry.transform else entry.value


def _env_files_from_toml(early_config: pytest.Config) -> list[str]:
    for path in chain.from_iterable([[early_config.rootpath], early_config.rootpath.parents]):
        for pytest_toml_name in ("pytest.toml", ".pytest.toml", "pyproject.toml"):
            pytest_toml_file = path / pytest_toml_name
            if not pytest_toml_file.exists():
                continue
            with pytest_toml_file.open("rb") as file_handler:
                try:
                    config = tomllib.load(file_handler)
                except tomllib.TOMLDecodeError:
                    return []
                if pytest_toml_name == "pyproject.toml":
                    config = config.get("tool", {})
                if (
                    (pytest_env := config.get("pytest_env"))
                    and isinstance(pytest_env, dict)
                    and (raw := pytest_env.get("env_files"))
                ):
                    return [str(f) for f in (raw if isinstance(raw, list) else [raw])]
                return []
    return []


def _load_env_files(early_config: pytest.Config) -> Generator[Path, None, None]:
    if not (env_files := _env_files_from_toml(early_config)):
        env_files = list(early_config.getini("env_files"))
    for env_file_str in env_files:
        if (resolved := early_config.rootpath / env_file_str).is_file():
            yield resolved


def _parse_toml_config(config: dict[str, Any]) -> Generator[Entry, None, None]:
    for key, entry in config.items():
        if key == "env_files" and isinstance(entry, list):
            continue
        if isinstance(entry, dict):
            unset = bool(entry.get("unset"))
            value = str(entry.get("value", "")) if not unset else ""
            transform, skip_if_set = bool(entry.get("transform")), bool(entry.get("skip_if_set"))
        else:
            value, transform, skip_if_set, unset = str(entry), False, False, False
        yield Entry(key, value, transform, skip_if_set, unset=unset)


def _load_values(early_config: pytest.Config) -> Iterator[Entry]:
    has_toml = False
    start_path = early_config.inipath.parent if early_config.inipath is not None else early_config.rootpath
    for path in chain.from_iterable([[start_path], start_path.parents]):
        for pytest_toml_name in ("pytest.toml", ".pytest.toml", "pyproject.toml"):
            pytest_toml_file = path / pytest_toml_name
            if pytest_toml_file.exists():
                with pytest_toml_file.open("rb") as file_handler:
                    config = tomllib.load(file_handler)

                    if pytest_toml_name == "pyproject.toml":  # in pyproject.toml the path is tool.pytest_env
                        config = config.get("tool", {})

                    if "pytest_env" in config:
                        has_toml = True
                        yield from _parse_toml_config(config["pytest_env"])

                break  # breaks the pytest_toml_name forloop
        if has_toml:  # breaks the path forloop
            break

    if has_toml:
        return

    for line in early_config.getini("env"):
        # INI lines e.g. D:R:NAME=VAL has two flags (R and D), NAME key, and VAL value
        parts = line.partition("=")
        ini_key_parts = parts[0].split(":")
        flags = {k.strip().upper() for k in ini_key_parts[:-1]}
        # R: is a way to designate whether to use raw value -> perform no transformation of the value
        transform = "R" not in flags
        # D: is a way to mark the value to be set only if it does not exist yet
        skip_if_set = "D" in flags
        # U: is a way to unset (remove) an environment variable
        unset = "U" in flags
        key = ini_key_parts[-1].strip()
        value = parts[2].strip()
        yield Entry(key, value, transform, skip_if_set, unset=unset)
