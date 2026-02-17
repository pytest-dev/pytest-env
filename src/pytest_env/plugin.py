"""Adopt environment section in pytest configuration files."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
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
    parser.addoption(
        "--envfile",
        action="store",
        dest="envfile",
        default=None,
        help="path to .env file to load (prefix with + to extend config files, otherwise replaces them)",
    )


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
    env_files_list: list[str] = []
    if toml_config := _find_toml_config(early_config):
        env_files_list, _ = _load_toml_config(toml_config)

    for env_file in _load_env_files(early_config, env_files_list):
        for key, value in dotenv_values(env_file).items():
            if value is not None:
                os.environ[key] = value
    for entry in _load_values(early_config):
        if entry.unset:
            os.environ.pop(entry.key, None)
        elif entry.skip_if_set and entry.key in os.environ:
            continue
        else:
            os.environ[entry.key] = entry.value.format(**os.environ) if entry.transform else entry.value


def _find_toml_config(early_config: pytest.Config) -> Path | None:
    """Find TOML config file by checking inipath first, then walking up the tree."""
    if (
        early_config.inipath
        and early_config.inipath.suffix == ".toml"
        and early_config.inipath.name in {"pytest.toml", ".pytest.toml", "pyproject.toml"}
    ):
        return early_config.inipath

    start_path = early_config.inipath.parent if early_config.inipath is not None else early_config.rootpath
    for current_path in [start_path, *start_path.parents]:
        for toml_name in ("pytest.toml", ".pytest.toml", "pyproject.toml"):
            toml_file = current_path / toml_name
            if toml_file.exists():
                return toml_file
    return None


def _load_toml_config(config_path: Path) -> tuple[list[str], list[Entry]]:
    """Load env_files and entries from TOML config file."""
    with config_path.open("rb") as file_handler:
        config = tomllib.load(file_handler)

    if config_path.name == "pyproject.toml":
        config = config.get("tool", {})

    pytest_env_config = config.get("pytest_env", {})
    if not pytest_env_config:
        return [], []

    raw_env_files = pytest_env_config.get("env_files")
    env_files = [str(f) for f in raw_env_files] if isinstance(raw_env_files, list) else []

    entries = list(_parse_toml_config(pytest_env_config))
    return env_files, entries


def _load_env_files(early_config: pytest.Config, env_files: list[str]) -> Generator[Path, None, None]:
    """Resolve and yield existing env files, with CLI option taking precedence."""
    if cli_envfile := getattr(early_config.known_args_namespace, "envfile", None):
        if cli_envfile.startswith("+"):
            if not (resolved := early_config.rootpath / cli_envfile[1:]).is_file():
                msg = f"Environment file not found: {cli_envfile[1:]}"
                raise FileNotFoundError(msg)
            for env_file_str in env_files or list(early_config.getini("env_files")):
                if (config_resolved := early_config.rootpath / env_file_str).is_file():
                    yield config_resolved
            yield resolved
        else:
            if not (resolved := early_config.rootpath / cli_envfile).is_file():
                msg = f"Environment file not found: {cli_envfile}"
                raise FileNotFoundError(msg)
            yield resolved
        return

    for env_file_str in env_files or list(early_config.getini("env_files")):
        if (resolved := early_config.rootpath / env_file_str).is_file():
            yield resolved


def _load_values(early_config: pytest.Config) -> Iterator[Entry]:
    """Load env entries from config, preferring TOML over INI."""
    if toml_config := _find_toml_config(early_config):
        _, entries = _load_toml_config(toml_config)
        if entries:
            yield from entries
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
