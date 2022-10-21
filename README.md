# pytest-env

[![PyPI](https://img.shields.io/pypi/v/pytest-env?style=flat-square)](https://pypi.org/project/pytest-env/)
[![Supported Python
versions](https://img.shields.io/pypi/pyversions/pytest-env.svg)](https://pypi.org/project/pytest-env/)
[![check](https://github.com/pytest-dev/pytest-env/actions/workflows/check.yml/badge.svg)](https://github.com/pytest-dev/pytest-env/actions/workflows/check.yml)
[![Code style:
black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://pepy.tech/badge/pytest-env/month)](https://pepy.tech/project/pytest-env/month)

This is a py.test plugin that enables you to set environment variables in the pytest.ini file.

## Installation

Install with pip:

```shell
pip install pytest-env
```

## Usage

In your pytest.ini file add a key value pair with `env` as the key and the environment variables as a line separated list of `KEY=VALUE` entries.  The defined variables will be added to the environment before any tests are run:

```ini
[pytest]
env =
    HOME=~/tmp
    RUN_ENV=test
```

You can use `D:` (default) as prefix if you don't want to override existing environment variables:

```ini
[pytest]
env =
    D:HOME=~/tmp
    D:RUN_ENV=test
```

You can also use `R:` (raw) prefix if you wish to have curly bracket characters inside the env variable:

```ini
[pytest]
env =
    R:SOME_DICT={"key": "value"}
```

Lastly, you can use existing environment variables using a python-like format (Note: feature is disabled when using `R:` prefix):

```ini
[pytest]
env =
    RUN_PATH=/run/path/{USER}
```
