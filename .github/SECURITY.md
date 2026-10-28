# Security policy

pytest-env is a pytest plugin that sets environment variables for a test session from pytest configuration and `.env`
files. This policy says how to report a security problem and how we decide whether a report is one.

## Reporting a vulnerability

**Do not open a public issue for a security problem.** Use
[GitHub's private vulnerability reporting](https://github.com/pytest-dev/pytest-env/security/advisories/new). If you do
not have a GitHub account, or you are a Tidelift subscriber, report through the
[Tidelift security contact](https://tidelift.com/security) instead; Tidelift coordinates the fix and the disclosure with
us. If neither works for you, email [gaborjbernat@gmail.com](mailto:gaborjbernat@gmail.com).

Include what the attacker controls and what they gain, the steps or a proof of concept, and the versions and platform
you tested. Write the report yourself; unreviewed tool or model output takes longer to triage.

## What to expect

Volunteers maintain pytest-env, with no on-call rotation. We aim to acknowledge a report within **5 working days** and
assess it within **15 working days**. Fixes are developed in a private fork attached to the draft advisory, ship in a
new release, and the advisory, with a CVE requested through GitHub, goes out with that release. The default embargo is
**90 days** from the report; we agree any change with the reporter. We credit reporters in the advisory under the name
they choose, or not at all. There is no bug bounty.

## Supported versions

Only the latest release receives fixes. Confirm the problem reproduces on it before reporting.

## Vulnerability or bug

A report is a vulnerability when an attacker who controls only an input that the [threat model](THREAT_MODEL.md) lists
as untrusted breaks a guarantee pytest-env makes. A report that first needs control of something the threat model
trusts, such as the pytest configuration or the `.env` files it names, is a bug: we fix it in the open and publish no
advisory. Classify by who supplies the dangerous input, not by how bad the outcome sounds.

**In scope**

- pytest-env loading a `.env` file the configuration or `--envfile` did not name, or one outside the rootdir for a
  relative name.
- A variable value printed when `--pytest-env-verbose` is off.

**Out of scope**

- Values the configuration sets: the project's pytest configuration is trusted, like the tests it runs.
- `{VAR}` expansion reaching other variables: it is documented, and `R:` turns it off.
- Values printed with `--pytest-env-verbose`, which exists to print them.
- Parsing behavior of `.env` files, which belongs to python-dotenv.

If you cannot tell which side a finding falls on, report it privately and we will decide.
