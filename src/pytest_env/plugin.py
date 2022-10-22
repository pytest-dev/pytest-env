"""Adopt environment section in pytest configuration files."""
from __future__ import annotations

import os

import pytest


_DEFAULT_FLAG = 'D'
_RAW_FLAG = 'R'

_ALLOWED_FLAGS = (_DEFAULT_FLAG, _RAW_FLAG)

def pytest_addoption(parser: pytest.Parser) -> None:
    """Add section to configuration files."""
    help_msg = "a line separated list of environment variables " "of the form NAME=VALUE."

    parser.addini("env", type="linelist", help=help_msg, default=[])


@pytest.hookimpl(tryfirst=True)  # type: ignore # untyped decorator
def pytest_load_initial_conftests(
    args: list[str], early_config: pytest.Config, parser: pytest.Parser  # noqa: U100
) -> None:
    """Load environment variables from configuration files."""
    for e in early_config.getini("env"):
        part = e.partition("=")
        # INI key consists of flags and of the env variable key
        # For example D:R:NAME=VAL has two flags (R and D), NAME key, and VAL value
        ini_key = part[0].strip()
        value = part[2].strip()

        ini_key_parts = ini_key.split(":")
        flags = ini_key_parts[:-1]
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
        rkey = key.split("R:")
        use_raw_value = False

        if len(rkey) == 2:
            key = rkey[1]
            use_raw_value = True

        # Replace environment variables in value. for instance:
        # TEST_DIR={USER}/repo_test_dir.
        if not use_raw_value:
            value = value.format(**os.environ)

        # use D: as a way to designate a default value that will only override env variables if they do not exist
        default_key = key.split("D:")
        default_val = False

        if len(default_key) == 2:
            key = default_key[1]
            default_val = True

        if not default_val or key not in os.environ:
            os.environ[key] = value
