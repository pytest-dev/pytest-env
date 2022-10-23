"""Adopt environment section in pytest configuration files."""
from __future__ import annotations

import os
from typing import Final, Tuple

import pytest

_DEFAULT_FLAG: Final[str] = 'D'
_RAW_FLAG: Final[str] = 'R'

_ALLOWED_FLAGS: Final[Tuple[str, ...]] = (_DEFAULT_FLAG, _RAW_FLAG)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add section to configuration files."""
    help_msg = "a line separated list of environment variables of the form NAME=VALUE."

    parser.addini("env", type="linelist", help=help_msg, default=[])


@pytest.hookimpl(tryfirst=True)  # type: ignore # untyped decorator
def pytest_load_initial_conftests(
        args: list[str], early_config: pytest.Config, parser: pytest.Parser  # noqa: U100
) -> None:
    """Load environment variables from configuration files."""
    for line in early_config.getini("env"):
        part = line.partition("=")
        # INI key consists of flags and of the env variable key
        # For example D:R:NAME=VAL has two flags (R and D), NAME key, and VAL value
        ini_key = part[0].strip()
        value = part[2].strip()

        ini_key_parts = ini_key.split(":")
        flags = ini_key_parts[:-1]
        print(flags)
        for flag in flags:
            if flag not in _ALLOWED_FLAGS:
                raise Exception(
                    'Flag "%s" is not recognized. '
                    'Colons in variable names can only be used to denote flags.' % flag
                )
        key = ini_key_parts[-1]

        # use R: as a way to designate whether to use
        # "raw" value (skip replacing environment
        # variables in a value). Use this to allow
        # curly bracket characters in a value.
        use_raw_value = _RAW_FLAG in flags

        # use D: as a way to designate a default value
        # that will only override env variables if they
        # do not exist already
        use_default_value = _DEFAULT_FLAG in flags

        # Replace environment variables in value. for instance:
        # TEST_DIR={USER}/repo_test_dir.
        if not use_raw_value:
            value = value.format(**os.environ)

        if not use_default_value or key not in os.environ:
            os.environ[key] = value
