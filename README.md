# pytest-env

[![PyPI](https://img.shields.io/pypi/v/pytest-env?style=flat-square)](https://pypi.org/project/pytest-env/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pytest-env.svg)](https://pypi.org/project/pytest-env/)
[![check](https://github.com/pytest-dev/pytest-env/actions/workflows/check.yaml/badge.svg)](https://github.com/pytest-dev/pytest-env/actions/workflows/check.yaml)
[![Downloads](https://static.pepy.tech/badge/pytest-env/month)](https://pepy.tech/project/pytest-env)

A `pytest` plugin that sets environment variables from `pyproject.toml`, `pytest.toml`, `.pytest.toml`, or `pytest.ini`
configuration files. It can also load variables from `.env` files.

## Installation

```shell
pip install pytest-env
```

## Quick start

Add environment variables to your `pyproject.toml`:

```toml
[tool.pytest_env]
DATABASE_URL = "postgresql://localhost/test_db"
DEBUG = "true"
```

Run your tests. The environment variables are now available:

```python
import os


def test_database_connection():
    assert os.environ["DATABASE_URL"] == "postgresql://localhost/test_db"
    assert os.environ["DEBUG"] == "true"
```

## How-to guides

### Set different environments for test suites

Create a subdirectory config to override parent settings:

```
project/
├── pyproject.toml          # [tool.pytest_env] DB_HOST = "prod-db"
└── tests_integration/
    ├── pytest.toml          # [pytest_env] DB_HOST = "test-db"
    └── test_api.py
```

Running `pytest tests_integration/` uses the subdirectory configuration.

### Switch environments at runtime

Use the `--envfile` CLI option to override or extend your configuration:

```shell
# Override all configured env files with a different one.
pytest --envfile .env.local

# Add an additional env file to those already configured.
pytest --envfile +.env.override
```

Override mode loads only the specified file. Extend mode (prefix with `+`) loads configuration files first, then the CLI
file. Variables in the CLI file take precedence.

### Load variables from `.env` files

Specify `.env` files in your configuration:

```toml
[tool.pytest_env]
env_files = [".env", ".env.test"]
```

Create your `.env` file:

```shell
DATABASE_URL=postgres://localhost/mydb
SECRET_KEY='my-secret-key'
DEBUG="true"
```

Files are loaded before inline variables, so inline configuration takes precedence.

### Expand variables using other environment variables

Reference existing environment variables in values:

```toml
[tool.pytest_env]
RUN_PATH = { value = "/run/path/{USER}", transform = true }
```

The `{USER}` placeholder expands to the current user's name.

### Set conditional defaults

Only set a variable if it does not already exist:

```toml
[tool.pytest_env]
HOME = { value = "~/tmp", skip_if_set = true }
```

This leaves `HOME` unchanged if already set, otherwise sets it to `~/tmp`.

### Remove variables from the environment

Unset a variable completely (different from setting to empty string):

```toml
[tool.pytest_env]
DATABASE_URL = { unset = true }
```

## Reference

### TOML configuration format

Define environment variables under `[tool.pytest_env]` in `pyproject.toml`, or `[pytest_env]` in `pytest.toml` or
`.pytest.toml`:

```toml
# pyproject.toml
[tool.pytest_env]
SIMPLE_VAR = "value"
NUMBER_VAR = 42
EXPANDED = { value = "{HOME}/path", transform = true }
CONDITIONAL = { value = "default", skip_if_set = true }
REMOVED = { unset = true }
```

Each key is the environment variable name. Values can be:

- **Plain values**: Cast to string and set directly.
- **Inline tables**: Objects with the following keys:

| Key           | Type   | Description                                                                  |
| ------------- | ------ | ---------------------------------------------------------------------------- |
| `value`       | string | The value to set.                                                            |
| `transform`   | bool   | Expand `{VAR}` references in the value using existing environment variables. |
| `skip_if_set` | bool   | Only set the variable if it is not already defined.                          |
| `unset`       | bool   | Remove the variable from the environment (ignores `value`).                  |

### INI configuration format

Define environment variables as line-separated `KEY=VALUE` entries:

```ini
# pytest.ini
[pytest]
env =
    HOME=~/tmp
    RUN_ENV=test
    D:CONDITIONAL=value
    R:RAW_VALUE={USER}
    U:REMOVED_VAR
```

```toml
# pyproject.toml (INI-style)
[tool.pytest]
env = [
  "HOME=~/tmp",
  "RUN_ENV=test",
]
```

Prefix flags modify behavior. Flags are case-insensitive and can be combined in any order (e.g., `R:D:KEY=VALUE`):

| Flag | Description                                                         |
| ---- | ------------------------------------------------------------------- |
| `D:` | Default — only set if the variable is not already defined.          |
| `R:` | Raw — skip `{VAR}` expansion (INI expands by default, unlike TOML). |
| `U:` | Unset — remove the variable from the environment entirely.          |

**Note**: In INI format, variable expansion is enabled by default. In TOML format, it requires `transform = true`.

### `.env` file format

Specify `.env` files using the `env_files` configuration option:

```toml
[tool.pytest_env]
env_files = [".env", ".env.test"]
```

```ini
[pytest]
env_files =
    .env
    .env.test
```

Files are parsed by [python-dotenv](https://github.com/theskumar/python-dotenv) and support:

- `KEY=VALUE` lines
- `#` comments
- `export` prefix
- Quoted values with escape sequences in double quotes
- `${VAR:-default}` expansion

Example `.env` file:

```shell
DATABASE_URL=postgres://localhost/mydb
export SECRET_KEY='my-secret-key'
DEBUG="true"
MESSAGE="hello\nworld"
API_KEY=${FALLBACK_KEY:-default_key}
```

Missing `.env` files are silently skipped. Paths are resolved relative to the project root.

### CLI option: `--envfile`

Override or extend configuration-based `env_files` at runtime:

```shell
pytest --envfile PATH        # Override mode
pytest --envfile +PATH       # Extend mode
```

**Override mode** (`--envfile PATH`): Loads only the specified file, ignoring all `env_files` from configuration.

**Extend mode** (`--envfile +PATH`): Loads configuration files first in their normal order, then loads the CLI file.
Variables from the CLI file override those from configuration files.

Unlike configuration-based `env_files`, CLI-specified files must exist. Missing files raise `FileNotFoundError`. Paths
are resolved relative to the project root.

## Explanation

### Configuration precedence

When multiple configuration sources define the same variable, the following precedence rules apply (highest to lowest):

1. Inline variables in configuration files (TOML or INI format)
1. Variables from `.env` files loaded via `env_files`
1. Variables already present in the environment (unless `skip_if_set = false` or no `D:` flag)

When using `--envfile`, CLI files take precedence over configuration-based `env_files`, but inline variables still win.

### Configuration format precedence

When multiple configuration formats are present:

1. TOML native format (`[pytest_env]` or `[tool.pytest_env]`) takes precedence over INI format.
1. Among TOML files, the first file with a `pytest_env` section is used, checked in order: `pytest.toml`,
   `.pytest.toml`, `pyproject.toml`.
1. If no TOML file contains `pytest_env`, the plugin falls back to INI-style `env` configuration.

### File discovery

The plugin walks up the directory tree starting from pytest's resolved configuration directory. For each directory, it
checks `pytest.toml`, `.pytest.toml`, and `pyproject.toml` in order, stopping at the first file containing a
`pytest_env` section.

This means subdirectory configurations take precedence over parent configurations, allowing you to have different
settings for integration tests versus unit tests.

### When to use TOML vs INI format

Use the **TOML native format** (`[pytest_env]`) when:

- You need fine-grained control over expansion and conditional setting.
- Your configuration is complex with multiple inline tables.
- You prefer explicit `transform = true` for variable expansion.

Use the **INI format** (`env` key) when:

- You want simple `KEY=VALUE` pairs with minimal syntax.
- You prefer expansion by default (add `R:` to disable).
- You are migrating from an existing INI-based setup.

Both formats are fully supported and can coexist (TOML takes precedence if both are present).

### When to use `.env` files vs inline configuration

Use **`.env` files** when:

- You have many environment variables that would clutter your config file.
- You want to share environment configuration with other tools (e.g., Docker, shell scripts).
- You need different `.env` files for different environments (dev, staging, prod).

Use **inline configuration** when:

- You have a small number of test-specific variables.
- You want variables to be version-controlled alongside test configuration.
- You need features like `transform`, `skip_if_set`, or `unset` that `.env` files do not support.

You can combine both approaches. Inline variables always take precedence over `.env` files.
