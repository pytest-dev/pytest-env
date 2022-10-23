"""Adopt environment section in pytest configuration files."""
from __future__ import annotations

import os

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add section to configuration files."""
    help_msg = "a line separated list of environment variables of the form (FLAG:)NAME=VALUE"
    parser.addini("env", type="linelist", help=help_msg, default=[])


@pytest.hookimpl(tryfirst=True)  # type: ignore # untyped decorator
def pytest_load_initial_conftests(
    args: list[str], early_config: pytest.Config, parser: pytest.Parser  # noqa: U100
) -> None:
    """Load environment variables from configuration files."""
    for line in early_config.getini("env"):

        # INI lines e.g. D:R:NAME=VAL has two flags (R and D), NAME key, and VAL value
        parts = line.partition("=")
        ini_key_parts = parts[0].split(":")
        flags = {k.strip().upper() for k in ini_key_parts[:-1]}
        # R: is a way to designate whether to use raw value -> perform no transformation of the value
        transform = "R" not in flags
        # D: is a way to mark the value to be set only if it does not exist yet
        skip_if_set = "D" in flags
        key = ini_key_parts[-1].strip()
        value = parts[2].strip()

        if skip_if_set and key in os.environ:
            continue
        # transformation -> replace environment variables, e.g. TEST_DIR={USER}/repo_test_dir.
        os.environ[key] = value.format(**os.environ) if transform else value
