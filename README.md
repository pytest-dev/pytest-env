# pytest-env

[![PyPI](https://img.shields.io/pypi/v/pytest-env?style=flat-square)](https://pypi.org/project/pytest-env/)
[![Supported Python
versions](https://img.shields.io/pypi/pyversions/pytest-env.svg)](https://pypi.org/project/pytest-env/)
[![check](https://github.com/pytest-dev/pytest-env/actions/workflows/check.yaml/badge.svg)](https://github.com/pytest-dev/pytest-env/actions/workflows/check.yaml)
[![Downloads](https://static.pepy.tech/badge/pytest-env/month)](https://pepy.tech/project/pytest-env)

This is a `pytest` plugin that enables you to set environment variables in a `pytest.ini` or `pyproject.toml` file.

## Installation

Install with pip:

```shell
pip install pytest-env
```

## Usage

### Native form in `pyproject.toml`

```toml
[tool.pytest_env]
HOME = "~/tmp"
RUN_ENV = 1
TRANSFORMED = {value = "{USER}/alpha", transform = true}
SKIP_IF_SET = {value = "on", skip_if_set = true}
```

The `tool.pytest_env` tables keys are the environment variables keys to set. The right hand side of the assignment:

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
[tool.pytest.ini_options]
env = [
    "HOME=~/tmp",
    "RUN_ENV=test",
]
```

### Only set if not already set

You can use `D:` (default) as prefix if you don't want to override existing environment variables:

```ini
[pytest]
env =
    D:HOME=~/tmp
    D:RUN_ENV=test
```

### Transformation

You can use existing environment variables using a python-like format, these environment variables will be expended
before setting the environment variable:

```ini
[pytest]
env =
    RUN_PATH=/run/path/{USER}
```

You can apply the `R:` prefix to keep the raw value and skip this transformation step (can combine with the `D:` flag,
order is not important):

```ini
[pytest]
env =
    R:RUN_PATH=/run/path/{USER}
    R:D:RUN_PATH_IF_NOT_SET=/run/path/{USER}
```
