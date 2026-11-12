"""Adopt environment section in pytest configuration files."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Final, TypeAlias

import pytest
from dotenv import dotenv_values

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator
    from pathlib import Path

_ENV_ACTIONS_KEY: Final[pytest.StashKey[list[str]]] = pytest.StashKey[list[str]]()


_TomlValue: TypeAlias = str | int | float | bool | datetime | list["_TomlValue"] | dict[str, "_TomlValue"]


@dataclass
class Entry:
    """Configuration entries."""

    key: str
    value: str
    transform: bool
    skip_if_set: bool
    unset: bool = False


@dataclass(frozen=True, kw_only=True, slots=True)
class _TomlConfig:
    env_files: list[str] | None
    entries: list[Entry]
    env_files_skip_if_set: bool | None


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add section to configuration files."""
    help_msg = "a line separated list of environment variables of the form (FLAG:)NAME=VALUE"
    parser.addini("env", type="linelist", help=help_msg, default=[])
    parser.addini("env_files", type="linelist", help="a line separated list of .env files to load", default=[])
    parser.addini(
        "env_files_skip_if_set",
        type="bool",
        help="only set .env file variables when not already defined",
        default=False,
    )
    parser.addoption(
        "--envfile",
        action="store",
        dest="envfile",
        default=None,
        help="path to .env file to load (prefix with + to extend config files, otherwise replaces them)",
    )
    parser.addoption(
        "--pytest-env-verbose",
        action="store_true",
        dest="pytest_env_verbose",
        default=False,
        help="print environment variable assignments made by pytest-env",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(
    args: list[str],  # ruff:ignore[unused-function-argument] the hookspec passes it
    early_config: pytest.Config,
    parser: pytest.Parser,  # ruff:ignore[unused-function-argument] the hookspec passes it
) -> None:
    """Load environment variables from configuration files."""
    verbose = getattr(early_config.known_args_namespace, "pytest_env_verbose", False)
    # collected without --pytest-env-verbose too, so the loaders need no None check
    actions: list[tuple[str, str, str, str]] = []

    env_files_list: list[str] | None = None
    env_files_skip_if_set: bool | None = None
    if toml_config := _find_toml_config(early_config):
        toml = _load_toml_config(toml_config)
        env_files_list, env_files_skip_if_set = toml.env_files, toml.env_files_skip_if_set

    if env_files_skip_if_set is None:
        env_files_skip_if_set = bool(early_config.getini("env_files_skip_if_set"))

    _apply_env_files(early_config, env_files_list, actions, skip_if_set=env_files_skip_if_set)
    source = _config_source(early_config) if verbose else ""
    for entry in _load_values(early_config):
        if entry.unset:
            os.environ.pop(entry.key, None)
            actions.append(("UNSET", entry.key, "", source))
        elif entry.skip_if_set and entry.key in os.environ:
            actions.append(("SKIP", entry.key, os.environ[entry.key], source))
        else:
            final = entry.value.format(**os.environ) if entry.transform else entry.value
            os.environ[entry.key] = final
            actions.append(("SET", entry.key, final, source))

    if verbose and actions:
        early_config.stash[_ENV_ACTIONS_KEY] = _format_actions(actions)


def _find_toml_config(early_config: pytest.Config) -> Path | None:
    # Find TOML config file by checking inipath first, then walking up the tree.
    if (
        early_config.inipath
        and early_config.inipath.suffix == ".toml"
        and early_config.inipath.name in {"pytest.toml", ".pytest.toml", "pyproject.toml"}
        and _has_env_section(early_config.inipath)
    ):
        return early_config.inipath

    start_path = early_config.inipath.parent if early_config.inipath is not None else early_config.rootpath
    for current_path in [start_path, *start_path.parents]:
        for toml_name in ("pytest.toml", ".pytest.toml", "pyproject.toml"):
            toml_file = current_path / toml_name
            if toml_file.exists() and _has_env_section(toml_file):
                return toml_file
    return None


def _has_env_section(config_path: Path) -> bool:
    # Check section presence without treating an explicit empty section as absent.
    with config_path.open("rb") as file_handler:
        config = tomllib.load(file_handler)
    if config_path.name == "pyproject.toml":
        config = config.get("tool", {})
    return "pytest_env" in config


def _load_toml_config(config_path: Path) -> _TomlConfig:
    # Load env_files and entries from TOML config file.
    with config_path.open("rb") as file_handler:
        config = tomllib.load(file_handler)

    if config_path.name == "pyproject.toml":
        config = config.get("tool", {})

    pytest_env_config = config.get("pytest_env", {})
    if not pytest_env_config:
        return _TomlConfig(env_files=None, entries=[], env_files_skip_if_set=None)

    raw_env_files = pytest_env_config.get("env_files")
    env_files: Final[list[str] | None] = [str(f) for f in raw_env_files] if isinstance(raw_env_files, list) else None
    raw_skip = pytest_env_config.get("env_files_skip_if_set")
    return _TomlConfig(
        env_files=env_files,
        entries=list(_parse_toml_config(pytest_env_config)),
        env_files_skip_if_set=raw_skip if isinstance(raw_skip, bool) else None,
    )


def _parse_toml_config(config: dict[str, _TomlValue]) -> Generator[Entry, None, None]:
    for key, entry in config.items():
        if key == "env_files" and isinstance(entry, list):
            continue
        if key == "env_files_skip_if_set" and isinstance(entry, bool):
            continue
        if isinstance(entry, dict):
            unset = bool(entry.get("unset"))
            value = str(entry.get("value", "")) if not unset else ""
            transform, skip_if_set = bool(entry.get("transform")), bool(entry.get("skip_if_set"))
        else:
            value, transform, skip_if_set, unset = str(entry), False, False, False
        yield Entry(key=key, value=value, transform=transform, skip_if_set=skip_if_set, unset=unset)


def _apply_env_files(
    early_config: pytest.Config,
    env_files_list: list[str] | None,
    actions: list[tuple[str, str, str, str]],
    *,
    skip_if_set: bool,
) -> None:
    preexisting = dict(os.environ) if skip_if_set else {}
    for env_file in _load_env_files(early_config, env_files_list):
        for key, value in dotenv_values(env_file).items():
            if value is None:
                continue
            if skip_if_set and (env_key := key.upper() if os.name == "nt" else key) in preexisting:
                actions.append(("SKIP", key, preexisting[env_key], str(env_file)))
            else:
                os.environ[key] = value
                actions.append(("SET", key, value, str(env_file)))


def _load_env_files(early_config: pytest.Config, env_files: list[str] | None) -> Generator[Path, None, None]:
    # Resolve and yield existing env files, with CLI option taking precedence.
    configured_env_files: Final[list[str]] = (
        env_files if env_files is not None else list(early_config.getini("env_files"))
    )
    if not (cli_envfile := getattr(early_config.known_args_namespace, "envfile", None)):
        yield from _existing_env_files(early_config, configured_env_files)
        return
    extend = cli_envfile.startswith("+")
    name = cli_envfile[1:] if extend else cli_envfile
    if not (resolved := early_config.rootpath / name).is_file():
        msg = f"Environment file not found: {name}"
        raise FileNotFoundError(msg)
    if extend:
        yield from _existing_env_files(early_config, configured_env_files)
    yield resolved


def _existing_env_files(early_config: pytest.Config, env_files: list[str]) -> Generator[Path, None, None]:
    for env_file_str in env_files:
        if (resolved := early_config.rootpath / env_file_str).is_file():
            yield resolved


def _config_source(early_config: pytest.Config) -> str:
    # Describe the configuration source for verbose output.
    if (toml_path := _find_toml_config(early_config)) and _load_toml_config(toml_path).entries:
        return str(toml_path)
    return str(early_config.inipath or early_config.rootpath)


def _load_values(early_config: pytest.Config) -> Iterator[Entry]:
    # Load env entries from config, preferring TOML over INI.
    if toml_config := _find_toml_config(early_config):
        yield from _load_toml_config(toml_config).entries
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
        yield Entry(key=key, value=parts[2].strip(), transform=transform, skip_if_set=skip_if_set, unset=unset)


def _format_actions(actions: list[tuple[str, str, str, str]]) -> list[str]:
    lines = ["pytest-env:"]
    for action, key, value, source in actions:
        if action == "UNSET":
            lines.append(f"  {action:<5} {key}  (from {source})")
        else:
            lines.append(f"  {action:<5} {key}={value}  (from {source})")
    return lines


def pytest_report_header(config: pytest.Config) -> list[str] | None:
    """Display environment variable assignments in test session header."""
    if _ENV_ACTIONS_KEY in config.stash:
        return config.stash[_ENV_ACTIONS_KEY]
    return None


__all__ = [
    "Entry",
    "pytest_addoption",
    "pytest_load_initial_conftests",
    "pytest_report_header",
]
