# pytest-env

[![PyPI](https://img.shields.io/pypi/v/pytest-env?style=flat-square)](https://pypi.org/project/pytest-env/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pytest-env.svg)](https://pypi.org/project/pytest-env/)
[![check](https://github.com/pytest-dev/pytest-env/actions/workflows/check.yaml/badge.svg)](https://github.com/pytest-dev/pytest-env/actions/workflows/check.yaml)
[![Downloads](https://static.pepy.tech/badge/pytest-env/month)](https://pepy.tech/project/pytest-env)

This is a `pytest` plugin that enables you to set environment variables in `pytest.ini`, `pyproject.toml`, `pytest.toml`
or `.pytest.toml` files.

## Installation

Install with pip:

```shell
pip install pytest-env
```

## Usage

### Native form in `pyproject.toml`, `pytest.toml` and `.pytest.toml`

Native form takes precedence over the `pytest.ini` form. `pytest.toml` takes precedence over `.pytest.toml`, and that
takes precedence over `pyproject.toml`.

In `pyproject.toml`:

```toml
[tool.pytest_env]
HOME = "~/tmp"
RUN_ENV = 1
TRANSFORMED = { value = "{USER}/alpha", transform = true }
SKIP_IF_SET = { value = "on", skip_if_set = true }
```

In `pytest.toml` (or `.pytest.toml`):

```toml
[pytest_env]
HOME = "~/tmp"
RUN_ENV = 1
TRANSFORMED = { value = "{USER}/alpha", transform = true }
SKIP_IF_SET = { value = "on", skip_if_set = true }
```

The `tool.pytest_env` (`pytest_env` in `pytest.toml` and `.pytest.toml`) tables keys are the environment variables keys
to set. The right hand side of the assignment:

- if an inline table you can set options via the `transform` or `skip_if_set` keys, while the `value` key holds the
  value to set (or transform before setting). For transformation the variables you can use is other environment
  variable,
- otherwise the value to set for the environment variable to set (casted to a string).

### Via pytest configurations

In your pytest.ini file add a key value pair with `env` as the key and the environment variables as a line separated
list of `KEY=VALUE` entries. The defined variables will be added to the environment before any tests are run:

```ini
[pytest]
env =
    HOME=~/tmp
    RUN_ENV=test
```

Or with `pyproject.toml`:

```toml
[tool.pytest]
env = [
  "HOME=~/tmp",
  "RUN_ENV=test",
]
```

### Only set if not already set

Use `skip_if_set = true` in the native TOML form, or the `D:` (default) prefix in INI form, to only set the variable
when it is not already defined in the environment:

```toml
[pytest_env]
HOME = { value = "~/tmp", skip_if_set = true }
RUN_ENV = { value = "test", skip_if_set = true }
```

```ini
[pytest]
env =
    D:HOME=~/tmp
    D:RUN_ENV=test
```

### Transformation

You can reference existing environment variables using a python-like format. Use `transform = true` in the native TOML
form, or omit the `R:` prefix in INI form (transformation is the default in INI):

```toml
[pytest_env]
RUN_PATH = { value = "/run/path/{USER}", transform = true }
```

```ini
[pytest]
env =
    RUN_PATH=/run/path/{USER}
```

To keep the raw value and skip transformation, omit `transform` (or set it to `false`) in TOML, or apply the `R:` prefix
in INI (can combine with `D:`/`skip_if_set`, order is not important):

```toml
[pytest_env]
RUN_PATH = { value = "/run/path/{USER}" }
RUN_PATH_IF_NOT_SET = { value = "/run/path/{USER}", skip_if_set = true }
```

```ini
[pytest]
env =
    R:RUN_PATH=/run/path/{USER}
    R:D:RUN_PATH_IF_NOT_SET=/run/path/{USER}
```
