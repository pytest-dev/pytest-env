from __future__ import annotations

import os
from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


@pytest.mark.parametrize("config_name", ["pytest.toml", ".pytest.toml"])
@pytest.mark.parametrize("fallback_location", ["sibling", "parent"])
def test_pyproject_env_with_native_pytest_config(
    pytester: pytest.Pytester, child: Path, config_name: str, fallback_location: str
) -> None:
    (child / config_name).write_text('[pytest]\naddopts = ["-q"]\n', encoding="utf-8")
    fallback_directory: Final[Path] = child if fallback_location == "sibling" else pytester.path
    (fallback_directory / "pyproject.toml").write_text(
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
    "config_name",
    [
        pytest.param("pytest.toml", id="pytest-toml"),
        pytest.param(".pytest.toml", id="hidden-pytest-toml"),
        pytest.param("pyproject.toml", id="pyproject-toml"),
    ],
)
@pytest.mark.parametrize(
    "empty_section",
    [pytest.param("", id="empty-table"), pytest.param("env_files = []\n", id="empty-env-files")],
)
@pytest.mark.parametrize("fallback_location", ["sibling", "parent"])
def test_empty_env_section_stops_discovery(
    pytester: pytest.Pytester,
    child: Path,
    config_name: str,
    empty_section: str,
    fallback_location: str,
) -> None:
    section: Final[str] = "tool.pytest_env" if config_name == "pyproject.toml" else "pytest_env"
    (child / config_name).write_text(f"[{section}]\n{empty_section}", encoding="utf-8")
    fallback_directory: Final[Path] = child if fallback_location == "sibling" else pytester.path
    fallback_name: Final[str] = "pytest.toml" if config_name == "pyproject.toml" else "pyproject.toml"
    fallback_section: Final[str] = "tool.pytest_env" if fallback_name == "pyproject.toml" else "pytest_env"
    (fallback_directory / fallback_name).write_text(
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
