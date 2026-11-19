"""Adopt environment section in pytest configuration files."""

from __future__ import annotations

__lazy_modules__ = [
    "tomllib",
]

import os
import tomllib
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Final, TypeAlias, TypeVar

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator
    from pathlib import Path

_Option = TypeVar("_Option", bool, list[str])

_ENV_ACTIONS_KEY: Final[pytest.StashKey[list[str]]] = pytest.StashKey[list[str]]()


_TomlValue: TypeAlias = str | int | float | bool | datetime | list["_TomlValue"] | dict[str, "_TomlValue"]


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
    actions: list[tuple[str, str, str, str]] | None = [] if verbose else None

    env_files_list: list[str] | None = None
    env_files_skip_if_set: bool | None = None
    if toml_config := _find_toml_config(early_config):
        toml = _load_toml_config(toml_config)
        env_files_list, env_files_skip_if_set = toml.env_files, toml.env_files_skip_if_set

    if env_files_skip_if_set is None:
        env_files_skip_if_set = _get_option(early_config, "env_files_skip_if_set", bool)

    preexisting = dict(os.environ) if env_files_skip_if_set else {}
    for env_file in _load_env_files(early_config, env_files_list):
        _apply_env_file(early_config, env_file, actions, preexisting, skip_if_set=env_files_skip_if_set)
    _apply_entries(early_config, actions)

    if verbose and actions:
        early_config.stash[_ENV_ACTIONS_KEY] = _format_actions(actions)


def _find_toml_config(early_config: pytest.Config) -> Path | None:
    # Find TOML config file by checking inipath first, then walking up the tree.
    if early_config.inipath and early_config.inipath.suffix == ".toml" and _has_env_section(early_config.inipath):
        return early_config.inipath

    start_path = early_config.inipath.parent if early_config.inipath is not None else early_config.rootpath
    for current_path in [start_path, *start_path.parents]:
        for toml_name in ("pytest.toml", ".pytest.toml", "pyproject.toml"):
            toml_file = current_path / toml_name
            if toml_file.is_file() and _has_env_section(toml_file):
                return toml_file
    return None


def _has_env_section(config_path: Path) -> bool:
    # Check section presence without treating an explicit empty section as absent.
    with config_path.open("rb") as file_handler:
        try:
            config = tomllib.load(file_handler)
        except (tomllib.TOMLDecodeError, UnicodeDecodeError) as error:
            msg = f"{config_path}: {error}"
            raise pytest.UsageError(msg) from error
    if config_path.name == "pyproject.toml":
        tool = config.get("tool", {})
        return isinstance(tool, dict) and isinstance(tool.get("pytest_env"), dict)
    return isinstance(config.get("pytest_env"), dict)


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
    if raw_skip is not None and not isinstance(raw_skip, bool):
        msg = f"{config_path}: env_files_skip_if_set must be true or false"
        raise pytest.UsageError(msg)
    return _TomlConfig(
        env_files=env_files,
        entries=list(_parse_toml_config(pytest_env_config)),
        env_files_skip_if_set=raw_skip,
    )


@dataclass(frozen=True, kw_only=True, slots=True)
class _TomlConfig:
    env_files: list[str] | None
    entries: list[Entry]
    env_files_skip_if_set: bool | None


def _parse_toml_config(config: dict[str, _TomlValue]) -> Generator[Entry, None, None]:
    for key, entry in config.items():
        if key == "env_files" and isinstance(entry, list):
            continue
        if key == "env_files_skip_if_set":
            continue
        if isinstance(entry, dict):
            yield _parse_toml_table(key, entry)
        else:
            yield Entry(key=key, value=str(entry), transform=False, skip_if_set=False, unset=False)


def _parse_toml_table(key: str, entry: dict[str, _TomlValue]) -> Entry:
    if unknown := sorted(entry.keys() - {"value", "transform", "skip_if_set", "unset"}):
        msg = f"pytest-env: entry {key!r} has unknown key {unknown[0]!r}"
        raise pytest.UsageError(msg)
    for flag in ("unset", "transform", "skip_if_set"):
        if flag in entry and not isinstance(entry[flag], bool):
            msg = f"pytest-env: entry {key!r}: {flag} must be true or false"
            raise pytest.UsageError(msg)
    unset = bool(entry.get("unset"))
    if not unset and "value" not in entry:
        msg = f"pytest-env: entry {key!r} needs a value or unset = true"
        raise pytest.UsageError(msg)
    value = "" if unset else str(entry["value"])
    return Entry(
        key=key,
        value=value,
        transform=bool(entry.get("transform")),
        skip_if_set=bool(entry.get("skip_if_set")),
        unset=unset,
    )


@dataclass
class Entry:
    """Configuration entries."""

    key: str
    value: str
    transform: bool
    skip_if_set: bool
    unset: bool = False


def _get_option(config: pytest.Config, name: str, kind: type[_Option]) -> _Option:
    try:
        return config.getini(name)
    except (pytest.UsageError, TypeError, ValueError):
        # pytest includes the rejected value in its type diagnostic.
        expected = "true or false" if kind is bool else "a list of strings"
        msg = f"pytest-env: invalid {name} option, expected {expected}"
        raise pytest.UsageError(msg) from None


def _load_env_files(early_config: pytest.Config, env_files: list[str] | None) -> Generator[Path, None, None]:
    # Resolve and yield existing env files, with CLI option taking precedence.
    configured_env_files: Final[list[str]] = (
        env_files if env_files is not None else _get_option(early_config, "env_files", list[str])
    )
    if (cli_envfile := getattr(early_config.known_args_namespace, "envfile", None)) is None:
        yield from _existing_env_files(early_config, configured_env_files)
        return
    extend = cli_envfile.startswith("+")
    name = cli_envfile[1:] if extend else cli_envfile
    # pytest resolves the rootdir before --envfile is registered, so a separate PATH value may have moved it.
    candidates = (early_config.invocation_params.dir / name, early_config.rootpath / name)
    if not name or (resolved := _regular_env_file(candidates)) is None:
        msg = f"Environment file not found: {name}"
        raise FileNotFoundError(msg)
    if extend:
        yield from _existing_env_files(early_config, configured_env_files)
    yield resolved


def _existing_env_files(early_config: pytest.Config, env_files: list[str]) -> Generator[Path, None, None]:
    for env_file_str in env_files:
        if (resolved := _regular_env_file((early_config.rootpath / env_file_str,))) is not None:
            yield resolved


def _regular_env_file(candidates: tuple[Path, ...]) -> Path | None:
    if path := next((path for path in candidates if path.is_file()), None):
        return path
    if path := next((path for path in candidates if path.exists()), None):
        msg = f"Environment file is not a regular file: {path}"
        raise pytest.UsageError(msg)
    return None


def _apply_env_file(
    config: pytest.Config,
    env_file: Path,
    actions: list[tuple[str, str, str, str]] | None,
    preexisting: dict[str, str],
    *,
    skip_if_set: bool,
) -> None:
    from dotenv.main import resolve_variables  # ruff: ignore[import-outside-top-level]  # only needed for env files
    from dotenv.variables import parse_variables  # ruff: ignore[import-outside-top-level]  # only needed for env files

    # python-dotenv expands references before the skip rule runs, so a reference would see a skipped assignment.
    entries = _read_env_file(config, env_file)
    for key, value in (dict(entries) if skip_if_set else resolve_variables(entries, override=True)).items():
        if value is None:
            continue
        if skip_if_set and (env_key := key.upper() if os.name == "nt" else key) in preexisting:
            if actions is not None:
                actions.append(("SKIP", key, preexisting[env_key], str(env_file)))
        else:
            final = "".join(atom.resolve(os.environ) for atom in parse_variables(value)) if skip_if_set else value
            _set_variable(key, final, env_file)
            if actions is not None:
                actions.append(("SET", key, final, str(env_file)))


def _read_env_file(config: pytest.Config, env_file: Path) -> Iterator[tuple[str, str | None]]:
    from dotenv.parser import parse_stream  # ruff: ignore[import-outside-top-level]  # only needed for env files

    with env_file.open(encoding="utf-8") as stream:
        for binding in parse_stream(stream):
            if binding.error:
                # python-dotenv includes preceding blank lines in the binding.
                raw = binding.original.string
                line = binding.original.line + raw.count("\n", 0, len(raw) - len(raw.lstrip()))
                msg = f"{env_file}:{line}: skipped malformed dotenv statement"
                config.issue_config_time_warning(pytest.PytestConfigWarning(msg), stacklevel=2)
            elif binding.key is not None:
                yield binding.key, binding.value


def _set_variable(key: str, value: str, source: Path | pytest.Config) -> None:
    try:
        os.environ[key] = value
    except (OSError, ValueError):
        location = _config_source(source) if isinstance(source, pytest.Config) else source
        # A malformed key may contain an entire assignment.
        msg = f"pytest-env: cannot set environment variable {key.partition('=')[0]!r} from {location}"
        raise pytest.UsageError(msg) from None


def _config_source(early_config: pytest.Config) -> str:
    # Describe the configuration source for verbose output.
    if (toml_path := _find_toml_config(early_config)) and _load_toml_config(toml_path).entries:
        return str(toml_path)
    if any(item.startswith("env=") for item in early_config.known_args_namespace.override_ini or ()):
        return "-o env"
    return str(early_config.inipath) if early_config.inipath else "config"


def _apply_entries(early_config: pytest.Config, actions: list[tuple[str, str, str, str]] | None) -> None:
    source = _config_source(early_config) if actions is not None else ""
    for entry in _load_values(early_config):
        if entry.skip_if_set and entry.key in os.environ:
            if actions is not None:
                actions.append(("SKIP", entry.key, os.environ[entry.key], source))
        elif entry.unset:
            os.environ.pop(entry.key, None)
            if actions is not None:
                actions.append(("UNSET", entry.key, "", source))
        else:
            final = _expand_value(entry)
            _set_variable(entry.key, final, early_config)
            if actions is not None:
                actions.append(("SET", entry.key, final, source))


def _load_values(early_config: pytest.Config) -> Iterator[Entry]:
    # Load env entries from config, preferring TOML over INI.
    if toml_config := _find_toml_config(early_config):
        yield from _load_toml_config(toml_config).entries
        return

    for index, line in enumerate(_get_option(early_config, "env", list[str]), start=1):
        # INI lines e.g. D:R:NAME=VAL has two flags (R and D), NAME key, and VAL value
        parts = line.partition("=")
        ini_key_parts = parts[0].split(":")
        flags = {k.strip().upper() for k in ini_key_parts[:-1]}
        if unknown := flags - {"D", "R", "U"}:
            # The value may be a secret, so the message names only the flag.
            msg = f"pytest-env: env entry {index}: unknown flag {min(unknown)!r}, expected D, R or U"
            raise pytest.UsageError(msg)
        key = ini_key_parts[-1].strip()
        if not key:
            msg = f"pytest-env: env entry {index}: missing variable name"
            raise pytest.UsageError(msg)
        # R: is a way to designate whether to use raw value -> perform no transformation of the value
        transform = "R" not in flags
        # D: is a way to mark the value to be set only if it does not exist yet
        skip_if_set = "D" in flags
        # U: is a way to unset (remove) an environment variable
        yield Entry(key=key, value=parts[2].strip(), transform=transform, skip_if_set=skip_if_set, unset="U" in flags)


def _expand_value(entry: Entry) -> str:
    if not entry.transform:
        return entry.value
    try:
        return entry.value.format_map(os.environ)
    except (KeyError, IndexError, AttributeError, TypeError, ValueError):
        # Formatting exceptions can include literal text from the template or an expanded value.
        msg = f"pytest-env: invalid {{VAR}} template in the value of {entry.key!r}"
        raise pytest.UsageError(msg) from None


def _format_actions(actions: list[tuple[str, str, str, str]]) -> list[str]:
    lines = ["pytest-env:"]
    for action, key, value, source in actions:
        if action == "UNSET":
            lines.append(f"  {action:<5} {_escape(key)}  (from {_escape(source)})")
        else:
            lines.append(f"  {action:<5} {_escape(key)}={_escape(value)}  (from {_escape(source)})")
    return lines


def _escape(text: str) -> str:
    return "".join(char if char.isprintable() else char.encode("unicode_escape").decode() for char in text)


def pytest_report_header(config: pytest.Config) -> list[str] | None:
    """Display environment variable assignments in test session header."""
    if _ENV_ACTIONS_KEY in config.stash:
        return config.stash[_ENV_ACTIONS_KEY]
    return None
