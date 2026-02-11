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

## Usage

### TOML configuration (native form)

Define environment variables under `[tool.pytest_env]` in `pyproject.toml`, or `[pytest_env]` in `pytest.toml` /
`.pytest.toml`:

```toml
# pyproject.toml
[tool.pytest_env]
HOME = "~/tmp"
RUN_ENV = 1
TRANSFORMED = { value = "{USER}/alpha", transform = true }
SKIP_IF_SET = { value = "on", skip_if_set = true }
DATABASE_URL = { unset = true }
```

```toml
# pytest.toml or .pytest.toml
[pytest_env]
HOME = "~/tmp"
RUN_ENV = 1
TRANSFORMED = { value = "{USER}/alpha", transform = true }
SKIP_IF_SET = { value = "on", skip_if_set = true }
DATABASE_URL = { unset = true }
```

Each key is the environment variable name. The value is either a plain value (cast to string) or an inline table with
the following keys:

| Key           | Type   | Description                                                                 |
| ------------- | ------ | --------------------------------------------------------------------------- |
| `value`       | string | The value to set                                                            |
| `transform`   | bool   | Expand `{VAR}` references in the value using existing environment variables |
| `skip_if_set` | bool   | Only set the variable if it is not already defined                          |
| `unset`       | bool   | Remove the variable from the environment (ignores `value`)                  |

### INI configuration

Define environment variables as a line-separated list of `KEY=VALUE` entries under the `env` key:

```ini
# pytest.ini
[pytest]
env =
    HOME=~/tmp
    RUN_ENV=test
```

```toml
# pyproject.toml
[tool.pytest]
env = [
  "HOME=~/tmp",
  "RUN_ENV=test",
]
```

Prefix flags modify behavior. Flags are case-insensitive and can be combined in any order (e.g., `R:D:KEY=VALUE`):

| Flag | Description                                                        |
| ---- | ------------------------------------------------------------------ |
| `D:` | Default — only set if the variable is not already defined          |
| `R:` | Raw — skip `{VAR}` expansion (INI expands by default, unlike TOML) |
| `U:` | Unset — remove the variable from the environment entirely          |

### Precedence

When multiple configuration sources are present, the native TOML form takes precedence over the INI form. Within the
TOML form, files are checked in this order: `pytest.toml`, `.pytest.toml`, `pyproject.toml`. The first file containing a
`pytest_env` section wins.

### Configuration file discovery

The plugin walks the directory tree starting from the directory containing the configuration file pytest resolved
(`inipath`). For each directory it checks `pytest.toml`, `.pytest.toml`, and `pyproject.toml` in order, stopping at the
first file with a `pytest_env` section. This means a subdirectory config takes precedence over a parent config:

```
project/
├── pyproject.toml          # [tool.pytest_env] DB_HOST = "prod-db"
└── tests_integration/
    ├── pytest.toml          # [pytest_env] DB_HOST = "test-db"
    └── test_api.py
```

Running `pytest tests_integration/` uses `DB_HOST = "test-db"` from the subdirectory.

If no TOML file with a `pytest_env` section is found, the plugin falls back to the INI-style `env` key.

### Loading `.env` files

Use `env_files` to load variables from `.env` files. Files are loaded before inline `env` entries, so inline config
takes precedence. Missing files are silently skipped. Paths are relative to the project root.

```toml
# pyproject.toml
[tool.pytest_env]
env_files = [".env", ".env.test"]
API_KEY = "override_value"
```

```toml
# pytest.toml or .pytest.toml
[pytest_env]
env_files = [".env"]
```

```ini
# pytest.ini
[pytest]
env_files =
    .env
    .env.test
```

Files are parsed by [python-dotenv](https://github.com/theskumar/python-dotenv), supporting `KEY=VALUE` lines, `#`
comments, `export` prefix, quoted values (with escape sequences in double quotes), and `${VAR:-default}` expansion:

```shell
# .env
DATABASE_URL=postgres://localhost/mydb
export SECRET_KEY='my-secret-key'
DEBUG="true"
MESSAGE="hello\nworld"
```

### Examples

**Expanding environment variables** — reference existing variables using `{VAR}` syntax:

```toml
[pytest_env]
RUN_PATH = { value = "/run/path/{USER}", transform = true }
```

```ini
[pytest]
env =
    RUN_PATH=/run/path/{USER}
```

In TOML, expansion requires `transform = true`. In INI, expansion is the default; use the `R:` flag to disable it.

**Keeping raw values** — prevent `{VAR}` expansion:

```toml
[pytest_env]
PATTERN = { value = "/run/path/{USER}" }
```

```ini
[pytest]
env =
    R:PATTERN=/run/path/{USER}
```

**Conditional defaults** — only set when not already defined:

```toml
[pytest_env]
HOME = { value = "~/tmp", skip_if_set = true }
```

```ini
[pytest]
env =
    D:HOME=~/tmp
```

**Unsetting variables** — completely remove a variable from `os.environ` (not the same as setting to empty string):

```toml
[pytest_env]
DATABASE_URL = { unset = true }
```

```ini
[pytest]
env =
    U:DATABASE_URL
```

**Combining flags** — flags can be combined in any order:

```ini
[pytest]
env =
    R:D:TEMPLATE=/path/{placeholder}
```
