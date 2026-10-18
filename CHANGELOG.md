# Changelog

## 1.8.1 (2026-10-18)

- Respect explicit empty native env_files over INI fallback ([#273](https://github.com/pytest-dev/pytest-env/pull/273))

## 1.8.0 (2026-10-10)

- Document [pytest] env configuration in pytest.toml / .pytest.toml
  ([#262](https://github.com/pytest-dev/pytest-env/pull/262))
- 👷 ci: pin ubuntu-26.04 and bump dependencies ([#268](https://github.com/pytest-dev/pytest-env/pull/268))
- feat(python): require 3.11 and default to 3.15 ([#270](https://github.com/pytest-dev/pytest-env/pull/270))

## 1.7.1 (2026-09-08)

- 🔧 chore: batch dependency updates weekly on Tuesday ([#256](https://github.com/pytest-dev/pytest-env/pull/256))
- Keep pyproject environment settings visible beside native pytest configuration
  ([#260](https://github.com/pytest-dev/pytest-env/pull/260))

## 1.7.0 (2026-07-21)

- 🔒 ci(workflows): add zizmor security auditing ([#216](https://github.com/pytest-dev/pytest-env/pull/216))
- 📦 build: move the testing extra to a dependency group ([#243](https://github.com/pytest-dev/pytest-env/pull/243))
- 👷 ci: test against Python 3.15 beta ([#245](https://github.com/pytest-dev/pytest-env/pull/245))

## 1.6.0 (2026-03-12)

- ✨ feat(env): preserve existing env values ([#213](https://github.com/pytest-dev/pytest-env/pull/213))

## 1.5.1 (2026-03-12)

- Add permissions to workflows ([#203](https://github.com/pytest-dev/pytest-env/pull/203))
- Add SECURITY.md to .github/ ([#206](https://github.com/pytest-dev/pytest-env/pull/206))
- Add missing .github config files ([#207](https://github.com/pytest-dev/pytest-env/pull/207))
- Standardize .github files to .yaml suffix ([#208](https://github.com/pytest-dev/pytest-env/pull/208))
- Fix verbose source attribution when falling back to INI env
  ([#211](https://github.com/pytest-dev/pytest-env/pull/211))

## 1.5.0 (2026-02-17)

- ✨ feat(plugin): add --pytest-env-verbose for debugging env assignments
  ([#199](https://github.com/pytest-dev/pytest-env/pull/199))

## 1.4.0 (2026-02-17)

- ✨ feat(cli): add --envfile option for runtime environment switching
  ([#197](https://github.com/pytest-dev/pytest-env/pull/197))

## 1.3.2 (2026-02-11)

[Release history](https://github.com/pytest-dev/pytest-env/releases/tag/1.3.2).

## 1.3.1 (2026-02-11)

- 🔧 build(type): migrate from mypy to ty ([#192](https://github.com/pytest-dev/pytest-env/pull/192))
- ♻️ refactor(plugin): consolidate TOML config parsing ([#193](https://github.com/pytest-dev/pytest-env/pull/193))
- ✅ test(plugin): verify env vars available during conftest imports
  ([#194](https://github.com/pytest-dev/pytest-env/pull/194))

## 1.3.0 (2026-02-11)

- Support pytest.toml and .pytest.toml ([#180](https://github.com/pytest-dev/pytest-env/pull/180))
- ✨ feat(config): support [tool.pytest] in pyproject.toml ([#189](https://github.com/pytest-dev/pytest-env/pull/189))
- ✨ feat(plugin): add U flag to unset env variables ([#188](https://github.com/pytest-dev/pytest-env/pull/188))
- 🐛 fix(config): use inipath for TOML file discovery ([#190](https://github.com/pytest-dev/pytest-env/pull/190))
- ✨ feat(plugin): add .env file loading support ([#191](https://github.com/pytest-dev/pytest-env/pull/191))

## 1.2.0 (2025-10-09)

- Add support for 3.14 and drop 3.9 ([#163](https://github.com/pytest-dev/pytest-env/pull/163))

## 1.1.5 (2024-09-17)

- Improve the CI ([#101](https://github.com/pytest-dev/pytest-env/pull/101))

## 1.1.4 (2024-09-07)

[Release history](https://github.com/pytest-dev/pytest-env/releases/tag/1.1.4).

## 1.1.3 (2023-11-28)

- fix README typo ([#63](https://github.com/pytest-dev/pytest-env/pull/63))

## 1.1.2 (2023-11-28)

[Release history](https://github.com/pytest-dev/pytest-env/releases/tag/1.1.2).

## 1.1.1 (2023-10-30)

- Fix native toml documentation does not match code ([#60](https://github.com/pytest-dev/pytest-env/pull/60))

## 1.1.0 (2023-10-24)

- Fix type checker ([#50](https://github.com/pytest-dev/pytest-env/pull/50))
- Drop the pytest dot ([#54](https://github.com/pytest-dev/pytest-env/pull/54))
- Add native toml support ([#59](https://github.com/pytest-dev/pytest-env/pull/59))

## 1.0.1 (2023-08-24)

- Disable plugin autoloading in the test suite ([#49](https://github.com/pytest-dev/pytest-env/pull/49))

## 1.0.0 (2023-08-22)

- Exclude dependabot and pre-commit ci from release notes ([#37](https://github.com/pytest-dev/pytest-env/pull/37))
- chore: typo fix in pyproject.toml ([#42](https://github.com/pytest-dev/pytest-env/pull/42))

## 0.8.2 (2023-06-15)

- Bump tools and deps ([#13](https://github.com/pytest-dev/pytest-env/pull/13))
- Bump pypa/gh-action-pypi-publish from 1.5.1 to 1.5.2 ([#14](https://github.com/pytest-dev/pytest-env/pull/14))
- Bump pypa/gh-action-pypi-publish from 1.5.2 to 1.6.1 ([#15](https://github.com/pytest-dev/pytest-env/pull/15))
- Bump pypa/gh-action-pypi-publish from 1.6.1 to 1.6.4 ([#16](https://github.com/pytest-dev/pytest-env/pull/16))
- Bump deps and tools ([#18](https://github.com/pytest-dev/pytest-env/pull/18))
- Add pyproject-fmt ([#19](https://github.com/pytest-dev/pytest-env/pull/19))
- Bump pypa/gh-action-pypi-publish from 1.6.4 to 1.7.1 ([#20](https://github.com/pytest-dev/pytest-env/pull/20))
- Bump pypa/gh-action-pypi-publish from 1.7.1 to 1.8.1 ([#21](https://github.com/pytest-dev/pytest-env/pull/21))
- Bump deps and tools ([#22](https://github.com/pytest-dev/pytest-env/pull/22))
- Bump deps and tools ([#23](https://github.com/pytest-dev/pytest-env/pull/23))
- Bump pypa/gh-action-pypi-publish from 1.8.1 to 1.8.3 ([#24](https://github.com/pytest-dev/pytest-env/pull/24))
- Bump pypa/gh-action-pypi-publish from 1.8.3 to 1.8.5 ([#25](https://github.com/pytest-dev/pytest-env/pull/25))
- Bump deps and tools ([#26](https://github.com/pytest-dev/pytest-env/pull/26))
- Bump deps and tools ([#28](https://github.com/pytest-dev/pytest-env/pull/28))
- Bump deps and tools ([#30](https://github.com/pytest-dev/pytest-env/pull/30))
- Add trusted-publish ([#31](https://github.com/pytest-dev/pytest-env/pull/31))
- Add 3.12 support ([#32](https://github.com/pytest-dev/pytest-env/pull/32))
- Bump pypa/gh-action-pypi-publish from 1.8.5 to 1.8.6 ([#33](https://github.com/pytest-dev/pytest-env/pull/33))
- git ls-files -z -- .github/workflows/check.yml | xargs -0 sed -i 's|3.12.0-alpha.7|3.12.0-beta.1|g'
  ([#34](https://github.com/pytest-dev/pytest-env/pull/34))
- Add ruff ([#35](https://github.com/pytest-dev/pytest-env/pull/35))

## 0.8.1 (2022-10-23)

- Add mention of pyproject.toml in the header of README.md ([#10](https://github.com/pytest-dev/pytest-env/pull/10))

## 0.8.0 (2022-10-23)

- Add R: prefix implementation and unit tests ([#9](https://github.com/pytest-dev/pytest-env/pull/9))

## 0.7.0 (2022-10-22)

[Release history](https://github.com/pytest-dev/pytest-env/releases/tag/0.7.0).

## 0.6.2 (2022-10-10)

[Release history](https://github.com/pytest-dev/pytest-env/releases/tag/0.6.2).
