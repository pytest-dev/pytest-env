"""Adopt environment section in pytest configuration files."""
from __future__ import annotations

import os

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add section to configuration files."""
    help_msg = "a line separated list of environment variables " "of the form NAME=VALUE."

    parser.addini("env", type="linelist", help=help_msg, default=[])


@pytest.hookimpl(tryfirst=True)  # type: ignore # untyped decorator
def pytest_load_initial_conftests(
    args: list[str], early_config: pytest.Config, parser: pytest.Parser  # noqa: U100
) -> None:
    """Load environment variables from configuration files."""
    for line in early_config.getini("env"):
        part = line.partition("=")
        key = part[0].strip()
        value = part[2].strip()

        # Replace environment variables in value. for instance  TEST_DIR={USER}/repo_test_dir.
        value = value.format(**os.environ)

        # use D: as a way to designate a default value that will only override env variables if they do not exist
        default_key = key.split("D:")
        default_val = False

        if len(default_key) == 2:
            key = default_key[1]
            default_val = True

        if not default_val or key not in os.environ:
            os.environ[key] = value
