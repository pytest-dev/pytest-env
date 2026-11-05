# Contributing

Install the project with `tox run -e dev` and run the tests with `tox run -e 3.15`. Run `prek run --all-files` before
pushing changes.

## Release notes

Add one `changelog.d/+short-name.<category>.md` file for each user-facing change. A pull request can contain several
fragments, including more than one category. Release preparation resolves the pull request number from the squash merge
and credits its commit authors and co-authors, then runs `release-creator contributors` to list first-time contributors;
do not put a number or author credit in the fragment text. A numeric fragment name remains supported.

Use `feature` for new behavior and Python support additions or removals, `change` for changes to existing behavior,
`bugfix` for corrections, and `doc` for documentation changes users need to know about. Use `breaking`, `security`,
`performance`, `deprecation`, `removal`, or `packaging` when those describe a user-facing change more precisely. The
tracked changelog calls the first four categories Added, Changes, Fixed, and Documentation. Empty categories are
omitted.

For example, `changelog.d/+native-env-files.bugfix.md` could contain:

```markdown
Respect an empty native `env_files` list over INI fallback.
```

Apply the `skip news` label to a PR that changes only maintenance work and has no user-facing effect. The news check
runs again if the label changes. Maintenance bot PRs receive the label automatically unless they provide a fragment. Bot
accounts are not listed as authors of release notes.

## Tests

Add a test for every new feature and bug fix: a fix needs a test that fails without it. A change without a test needs a
reason in the pull request description. Run the suite with `tox run -e 3.15`, which fails below 100% coverage. Pass
pytest arguments after `--` to run a subset, for example `tox run -e 3.15 -- tests/test_env.py -k env_files`.
