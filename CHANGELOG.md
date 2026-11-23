# Changelog

<!-- towncrier release notes start -->

<a name="release-1-8-8"></a>

## 1.8.8 (2026-11-23)

<a name="release-1-8-8-fixed"></a>

### Fixed

- Expand dotenv references in file order when `env_files_skip_if_set` is enabled, including repeated definitions and
  bare names ([#358](https://github.com/pytest-dev/pytest-env/pull/358)) by
  [@narayana006](https://github.com/narayana006) and [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-7"></a>

## 1.8.7 (2026-11-19)

<a name="release-1-8-7-fixed"></a>

### Fixed

- Reject non-boolean `env_files_skip_if_set` values in native TOML configuration
  ([#355](https://github.com/pytest-dev/pytest-env/pull/355)) by [@gaborbernat](https://github.com/gaborbernat).
- Report `-o env` as the source of overridden INI entries in the verbose header
  ([#348](https://github.com/pytest-dev/pytest-env/pull/348)) by [@gaborbernat](https://github.com/gaborbernat).
- Report a configuration error for a directory or named pipe supplied as a dotenv file
  ([#356](https://github.com/pytest-dev/pytest-env/pull/356)) by [@gaborbernat](https://github.com/gaborbernat).
- Report a usage error naming the entry when the operating system rejects an environment assignment
  ([#349](https://github.com/pytest-dev/pytest-env/pull/349)) by [@gaborbernat](https://github.com/gaborbernat).
- Resolve mixed-case environment variable references on Windows
  ([#351](https://github.com/pytest-dev/pytest-env/pull/351)) by [@gaborbernat](https://github.com/gaborbernat).
- Show the file and line number of malformed dotenv statements in pytest's warning summary
  ([#350](https://github.com/pytest-dev/pytest-env/pull/350)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-7-security"></a>

### Security

- Omit rejected environment option values from configuration errors
  ([#353](https://github.com/pytest-dev/pytest-env/pull/353)) by [@gaborbernat](https://github.com/gaborbernat).
- Report invalid environment templates without including field text in error output
  ([#354](https://github.com/pytest-dev/pytest-env/pull/354)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-7-performance"></a>

### Performance

- Defer loading the `.env` parser until a configured environment file is read
  ([#341](https://github.com/pytest-dev/pytest-env/pull/341)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-6"></a>

## 1.8.6 (2026-11-17)

<a name="release-1-8-6-fixed"></a>

### Fixed

- Escape non-printable characters in the `--pytest-env-verbose` header so each assignment stays on one line
  ([#331](https://github.com/pytest-dev/pytest-env/pull/331)) by [@gaborbernat](https://github.com/gaborbernat).
- Expand `${VAR}` in `.env` files with the kept value when `env_files_skip_if_set` skips the file's own assignment
  ([#340](https://github.com/pytest-dev/pytest-env/pull/340)) by [@gaborbernat](https://github.com/gaborbernat).
- Keep an existing variable when an entry combines `skip_if_set` (`D:`) with `unset` (`U:`)
  ([#337](https://github.com/pytest-dev/pytest-env/pull/337)) by [@gaborbernat](https://github.com/gaborbernat).
- Name the file when a TOML file found during discovery does not parse, and skip files whose `pytest_env` is not a table
  ([#333](https://github.com/pytest-dev/pytest-env/pull/333)) by [@gaborbernat](https://github.com/gaborbernat).
- Raise `FileNotFoundError` for an empty `--envfile` value instead of loading the configured env files
  ([#330](https://github.com/pytest-dev/pytest-env/pull/330)) by [@gaborbernat](https://github.com/gaborbernat).
- Read `[pytest_env]` from a custom-named TOML file selected with `-c` instead of a sibling or parent file
  ([#339](https://github.com/pytest-dev/pytest-env/pull/339)) by [@gaborbernat](https://github.com/gaborbernat).
- Reject INI `env` lines with an unknown flag or no variable name instead of applying them
  ([#334](https://github.com/pytest-dev/pytest-env/pull/334)) by [@gaborbernat](https://github.com/gaborbernat).
- Reject native TOML entry tables with unknown keys, non-boolean flags or no value instead of applying them
  ([#338](https://github.com/pytest-dev/pytest-env/pull/338)) by [@gaborbernat](https://github.com/gaborbernat).
- Resolve `--envfile` against the invocation directory before the project root, so `--envfile ../file` loads the file it
  names ([#332](https://github.com/pytest-dev/pytest-env/pull/332)) by [@gaborbernat](https://github.com/gaborbernat).
- Skip directories and other non-regular entries named like a TOML configuration file during discovery
  ([#336](https://github.com/pytest-dev/pytest-env/pull/336)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-6-security"></a>

### Security

- Report an invalid `{VAR}` template as a usage error that names the entry instead of printing an environment value
  ([#335](https://github.com/pytest-dev/pytest-env/pull/335)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-6-packaging"></a>

### Packaging

- Every wheel now carries a [PEP 770](https://peps.python.org/pep-0770/) CycloneDX SBOM in its `.dist-info/sboms`
  directory, written at build time by [python-sbom](https://github.com/tox-dev/python-sbom)
  ([#309](https://github.com/pytest-dev/pytest-env/pull/309)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-5"></a>

## 1.8.5 (2026-11-04)

<a name="release-1-8-4"></a>

## 1.8.4 (2026-10-31)

<a name="release-1-8-4-fixed"></a>

### Fixed

- Honor an empty native TOML environment section over INI `env` settings
  ([#294](https://github.com/pytest-dev/pytest-env/pull/294)) by [@Zhuyuyangyy](https://github.com/Zhuyuyangyy) and
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-3"></a>

## 1.8.3 (2026-10-27)

<a name="release-1-8-2"></a>

## 1.8.2 (2026-10-27)

<a name="release-1-8-2-fixed"></a>

### Fixed

- Fix repository links in the PyPI project description ([#282](https://github.com/pytest-dev/pytest-env/pull/282)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-2-packaging"></a>

### Packaging

- Describe the pytest plugin and its testing purpose in package metadata
  ([#282](https://github.com/pytest-dev/pytest-env/pull/282)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-1"></a>

## 1.8.1 (2026-10-18)

<a name="release-1-8-1-fixed"></a>

### Fixed

- Respect an explicitly empty native `env_files` list over the INI fallback
  ([#273](https://github.com/pytest-dev/pytest-env/pull/273)) by [@edsonsims](https://github.com/edsonsims).

<a name="release-1-8-0"></a>

## 1.8.0 (2026-10-10)

<a name="release-1-8-0-added"></a>

### Added

- Require Python 3.11 or newer ([#270](https://github.com/pytest-dev/pytest-env/pull/270)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-0-documentation"></a>

### Documentation

- Document `[pytest]` environment settings in `pytest.toml` and `.pytest.toml`
  ([#262](https://github.com/pytest-dev/pytest-env/pull/262)) by [@devtechedge](https://github.com/devtechedge).

<a name="release-1-7-1"></a>

## 1.7.1 (2026-09-08)

<a name="release-1-7-1-fixed"></a>

### Fixed

- Discover `pyproject.toml` environment settings beside native pytest configuration
  ([#260](https://github.com/pytest-dev/pytest-env/pull/260)) by [@oyeong011](https://github.com/oyeong011).

<a name="release-1-7-0"></a>

## 1.7.0 (2026-07-21)

<a name="release-1-7-0-added"></a>

### Added

- Support Python 3.15 beta ([#245](https://github.com/pytest-dev/pytest-env/pull/245)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-6-0"></a>

## 1.6.0 (2026-03-12)

<a name="release-1-6-0-added"></a>

### Added

- Preserve existing environment values when requested ([#213](https://github.com/pytest-dev/pytest-env/pull/213)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-5-1"></a>

## 1.5.1 (2026-03-12)

<a name="release-1-5-1-fixed"></a>

### Fixed

- Attribute verbose output to INI configuration when falling back from TOML
  ([#211](https://github.com/pytest-dev/pytest-env/pull/211)) by [@shuofengzhang](https://github.com/shuofengzhang).

<a name="release-1-5-0"></a>

## 1.5.0 (2026-02-17)

<a name="release-1-5-0-added"></a>

### Added

- Trace environment assignments with `--pytest-env-verbose` ([#199](https://github.com/pytest-dev/pytest-env/pull/199))
  by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-4-0"></a>

## 1.4.0 (2026-02-17)

<a name="release-1-4-0-added"></a>

### Added

- Select an environment file at runtime with `--envfile` ([#197](https://github.com/pytest-dev/pytest-env/pull/197)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-3-2"></a>

## 1.3.2 (2026-02-11)

<a name="release-1-3-1"></a>

## 1.3.1 (2026-02-11)

<a name="release-1-3-0"></a>

## 1.3.0 (2026-02-11)

<a name="release-1-3-0-added"></a>

### Added

- Read environment settings from `pytest.toml` and `.pytest.toml`
  ([#180](https://github.com/pytest-dev/pytest-env/pull/180)) by [@mikicz](https://github.com/mikicz).

- Unset environment variables with the `U:` prefix ([#188](https://github.com/pytest-dev/pytest-env/pull/188)) by
  [@gaborbernat](https://github.com/gaborbernat).

- Load variables from `.env` files ([#191](https://github.com/pytest-dev/pytest-env/pull/191)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-3-0-fixed"></a>

### Fixed

- Discover TOML configuration through pytest's `inipath` ([#190](https://github.com/pytest-dev/pytest-env/pull/190)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-3-0-documentation"></a>

### Documentation

- Document `[tool.pytest]` configuration for pytest 9 ([#189](https://github.com/pytest-dev/pytest-env/pull/189)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-3-0-packaging"></a>

### Packaging

- Require pytest 9 or newer ([#189](https://github.com/pytest-dev/pytest-env/pull/189)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-2-0"></a>

## 1.2.0 (2025-10-09)

<a name="release-1-2-0-added"></a>

### Added

- Support Python 3.14 and require Python 3.10 or newer ([#163](https://github.com/pytest-dev/pytest-env/pull/163)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-1-5"></a>

## 1.1.5 (2024-09-17)

<a name="release-1-1-4"></a>

## 1.1.4 (2024-09-07)

<a name="release-1-1-4-added"></a>

### Added

- Support Python 3.13
  ([commit e95bd81](https://github.com/pytest-dev/pytest-env/commit/e95bd811349603766fec44c6f9737a8260dd390c)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-1-3"></a>

## 1.1.3 (2023-11-28)

<a name="release-1-1-2"></a>

## 1.1.2 (2023-11-28)

<a name="release-1-1-1"></a>

## 1.1.1 (2023-10-30)

<a name="release-1-1-1-documentation"></a>

### Documentation

- Correct the native TOML configuration example ([#60](https://github.com/pytest-dev/pytest-env/pull/60)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-1-0"></a>

## 1.1.0 (2023-10-24)

<a name="release-1-1-0-added"></a>

### Added

- Read environment settings from the native `[tool.pytest_env]` TOML table
  ([#59](https://github.com/pytest-dev/pytest-env/pull/59)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-1-0-packaging"></a>

### Packaging

- Require pytest 7.4.2 or newer ([#59](https://github.com/pytest-dev/pytest-env/pull/59)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-0-1"></a>

## 1.0.1 (2023-08-24)

<a name="release-1-0-0"></a>

## 1.0.0 (2023-08-22)

<a name="release-0-8-2"></a>

## 0.8.2 (2023-06-15)

<a name="release-0-8-2-added"></a>

### Added

- Support Python 3.12 ([#32](https://github.com/pytest-dev/pytest-env/pull/32)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-0-8-1"></a>

## 0.8.1 (2022-10-23)

<a name="release-0-8-1-documentation"></a>

### Documentation

- Show that pytest-env can be configured in `pyproject.toml` ([#10](https://github.com/pytest-dev/pytest-env/pull/10))
  by [@Elijas](https://github.com/Elijas).

<a name="release-0-8-0"></a>

## 0.8.0 (2022-10-23)

<a name="release-0-8-0-added"></a>

### Added

- Expand configured values with the `R:` prefix ([#9](https://github.com/pytest-dev/pytest-env/pull/9)) by
  [@Elijas](https://github.com/Elijas).

<a name="release-0-7-0"></a>

## 0.7.0 (2022-10-22)

<a name="release-0-7-0-added"></a>

### Added

- Require Python 3.7 or newer ([#1](https://github.com/pytest-dev/pytest-env/pull/1)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-0-7-0-packaging"></a>

### Packaging

- Ship a PEP 561 typing marker ([#1](https://github.com/pytest-dev/pytest-env/pull/1)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-0-6-2"></a>

## 0.6.2 (2022-10-10)

<a name="release-0-6-2-added"></a>

### Added

- Interpolate existing environment variables in configured values
  ([commit 4462c24](https://github.com/pytest-dev/pytest-env/commit/4462c2466ac0a155e840184198870757694176a4)) by
  [@jsmedmar](https://github.com/jsmedmar).

<a name="release-0-6-1"></a>

## 0.6.1 (2017-06-08)

<a name="release-0-6-1-changes"></a>

### Changes

- Set configured variables before other plugins and `conftest.py` import them
  ([commit 40ba073](https://github.com/pytest-dev/pytest-env/commit/40ba073a62bddc041c0a4383a63ab3730180f184)) by
  [@Schnouki](https://github.com/Schnouki).

<a name="release-0-6-1-documentation"></a>

### Documentation

- Document the `D:` prefix for default values
  ([commit fbf9672](https://github.com/pytest-dev/pytest-env/commit/fbf967261dfc32b112cc5fb60cbcefea6ce8f8a9)) by
  [@TauPan](https://github.com/TauPan).

<a name="release-0-6-0"></a>

## 0.6.0 (2015-10-14)

<a name="release-0-6-0-added"></a>

### Added

- Preserve an existing environment variable with the `D:` prefix
  ([commit 5b8e700](https://github.com/pytest-dev/pytest-env/commit/5b8e700b10343c827e788fec0c73cabc8202565c)) by
  [@lbudman](https://github.com/lbudman).

<a name="release-0-5-1"></a>

## 0.5.1 (2015-02-05)

<a name="release-0-5"></a>

## 0.5 (2015-02-05)

<a name="release-0-5-added"></a>

### Added

- Set environment variables from pytest configuration
  ([commit 54efe7f](https://github.com/pytest-dev/pytest-env/commit/54efe7f73ca0998372c82969a7173c0990ac075d)) by
  [@lbudman](https://github.com/lbudman).
