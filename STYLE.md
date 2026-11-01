# Python Style Guide

The reference for how MinchinWeb's Python projects are set up. New projects
start from `templates/`; existing projects are audited against this file.

Rules are numbered (e.g. **T1**) so an audit can cite them. "Library" means a
package published to PyPI; "app" means something deployed, not published
(e.g. Django sites); "tooling" means a repo of scripts, plugins or
configuration that is never built or published as a package (see section 8);
"Home Assistant integration" means a custom integration installed through
HACS (see section 9). Rules apply to libraries and apps unless a section says
otherwise.

## 1. Tooling at a glance

| Concern                    | Standard                                                    | Replaces                             |
| -------------------------- | ----------------------------------------------------------- | ------------------------------------ |
| Formatter                  | `ruff format`                                               | black                                |
| Import sorting             | `ruff check` rule `I`                                       | isort                                |
| Linting                    | `ruff check`                                                | flake8, flake8-pyproject             |
| Dependencies / venv / lock | `uv` (`uv.lock`)                                            | pip-tools, `.requirements/*.in/.txt` |
| Build backend              | setuptools (>= 77)                                          | `setup.py`, `setup.cfg`              |
| Tests                      | pytest (Django `TestCase` for Django apps)                  |                                      |
| Task runner                | invoke (`tasks.py`), shared tasks from `minchin.tasks`      |                                      |
| Release                    | `minchin.releaser` via invoke                               |                                      |
| CI                         | GitHub Actions `check.yml` with `setup-uv`                  |                                      |
| Pre-commit                 | not used                                                    |                                      |

## 2. Formatting and linting (ruff)

- **F1** One tool: ruff. No `[tool.black]` or `[tool.flake8]` tables, and no
  black/isort/flake8 in dependencies. The one exception is a `[tool.isort]`
  table mirroring the ruff isort settings (F4): `minchin.releaser` runs isort
  before a release (and brings isort in itself), and needs it to agree with ruff.
- **F2** Line length **88**.
- **F3** `[tool.ruff.lint] extend-select` is `A B E W I N PTH RUF SIM UP YTT`
  (default rules `E4 E7 E9 F` stay on). `future-annotations = true`.
  Add rule families deliberately, with a comment saying what they are.
- **F4** Import sorting keeps the historic style: `force-sort-within-sections
  = true` (so `import x` and `from x import y` sort together by module name),
  `known-first-party = ["minchin", ...]`. The Django and Pelican sections are
  standard boilerplate in every `pyproject.toml` (even when unused), via
  `section-order` and `[tool.ruff.lint.isort.sections]`, so they never need
  reviewing. Order: future, standard-library, django, pelican, third-party,
  first-party, local-folder.
- **F5** `[tool.ruff.format] docstring-code-format = true`, and
  `line-ending = "auto"`. (`native` would make the Linux CI runner rewrite
  every CRLF file checked out on Windows.)
- **F6** `force-exclude = true` and exclude generated code (migrations,
  submodules, `_build`) so a repo-wide `--fix` is safe.
- **F7** Per-file ignores are listed with a reason in a comment. Prefer a
  per-file ignore over a global one.
- **F8** Before finishing a change: `uv run invoke format`, then
  `uv run invoke check`.
- **F9** `pyproject.toml` itself is linted and formatted: `validate-pyproject`
  checks it against the packaging schemas, and `taplo format` lays it out
  (2-space indent, comments kept). Do not use `pyproject-fmt`: it reorders
  classifiers, breaks the commented menu (P5) and rewrites `name`.

## 3. Dependencies (uv)

- **D1** Direct requirements go in `[project.dependencies]` as static
  strings with a minimum version (`"requests >= 2.32.4"`). A comment gives the
  reason when the minimum is for security or compatibility.
- **D2** No `dynamic = ["dependencies"]` and no `.requirements/` folder. The
  layering is:
  - *direct, runtime* -> `[project.dependencies]`
  - *direct, optional for users* -> `[project.optional-dependencies]` (extras)
  - *direct, development only* -> `[dependency-groups]` (`dev`, `docs`,
    `release`; PEP 735), composed with `{include-group = "..."}`
  - *indirect (transitive)* -> never written by hand; pinned by `uv.lock`
- **D3** `uv.lock` is committed for libraries and apps.
- **D4** Apps pin the interpreter in `.python-version`. Libraries do not.
- **D5** `invoke update` and `invoke upgrade` (from `minchin.tasks`) mirror `apt`:
  - `update`: `uv lock --upgrade`, re-resolve the lock to the newest allowed
    versions. Nothing installed yet.
  - `upgrade`: `uv sync`, install what the lock says into `.venv`.
- **D6** Local sibling checkouts are tried through `[tool.uv.sources]` (a
  commented-out line is fine), never by editing `dependencies`.

## 4. `pyproject.toml`

Start from `templates/pyproject.toml`. Order: `build-system`, `project`,
`project.optional-dependencies`, `project.urls`, `dependency-groups`,
`tool.setuptools.*`, other tools alphabetically (`pytest`, then `ruff`).

- **P1** `pyproject.toml` is the only packaging file. No `setup.py`,
  `setup.cfg` or `MANIFEST.in` unless a documented need remains
  (`check-manifest` ignore lists live in `[tool.check-manifest]`).
- **P2** `requires = ["setuptools >= 77"]`. `license = "MIT"` (SPDX
  expression) plus `license-files`; no `License ::` classifier.
- **P3** `requires-python` is always set. Policy: support as old as is
  practical, test on the newest stable (3.15 at time of writing), and use
  newer language features where they help. Ruff derives its target version
  from `requires-python`, so `UP` rewrites stay compatible. Use
  `from __future__ import annotations` so `X | None` hints work on old
  versions.
- **P4** Only `version` and `readme` are dynamic.
  `[tool.setuptools.dynamic] version = {attr = "pkg.__version__"}`, where
  `__version__` is a plain string literal with no imports (static analysis
  must work). Apps may keep it in `constants.py`, which imports nothing local.
  `readme = {file = ["README.rst"], content-type = "text/x-rst"}`.
- **P5** The commented-out classifier menu (Development Status, Python
  versions) stays in each project. Uncomment the active line. Keep the menu
  current as Python releases.
- **P6** `[project.urls]` has at least Bug Tracker, Repository and Changelog.
- **P7** `[project.scripts]` (or `gui-scripts`) for entry points; plugins use
  the framework's entry-point group.

## 5. Folder structure

- **L1** Flat layout. Libraries in the `minchin.*` family use an implicit
  namespace: `minchin/<name>/__init__.py` at the repo root, with **no**
  `minchin/__init__.py`. `[tool.setuptools.packages.find] include =
  ["minchin*"]`.
- **L2** Apps use a single top-level package named after the project
  (`my_app/`), with Django subpackages beneath it.
- **L3** Tests live inside the package, in `minchin/<name>/tests/` (named
  `tests`, not `test`), so they ship with the library and mirror its layout.
  A top-level `tests/` (or `test/`) is excluded from the distribution by
  `[tool.setuptools.packages.find] exclude`, which matches top-level names
  only, so `minchin.<name>.tests` is kept. `pytest` config is in
  `pyproject.toml` with `testpaths = ["minchin"]`.
- **L4** Repo root contains: `pyproject.toml`, `uv.lock`, `README.rst` (or
  `README.md` for apps), a changelog (L5), `LICENSE.txt`, `tasks.py`, `invoke.yaml`,
  `.editorconfig`, `.gitignore`, `.gitattributes`,
  `.github/workflows/check.yml` and `test.yml`. Docs in `docs/`.
  The audit checks the **exact casing** of these names (e.g. `CHANGELOG.rst`,
  not `changelog.rst`; `README.rst`, not `Readme.rst`; `LICENSE.txt`, not
  `License.txt`, `LICENSE` or `LICENSE.rst`; the `.txt` opens in Windows).
  Windows and the default git config are case-insensitive, so
  fix a wrong case with a two-step `git mv` (to a temporary name, then the
  right one). Build output (`build/`, `dist/`) and `.venv/` are
  git-ignored. No `env/` folder: `.venv/` only.
- **L5** The changelog is in the `releases` (Sphinx) format, which
  `minchin.releaser` edits, and there is exactly **one** copy. It lives at
  either `CHANGELOG.rst` (repo root, the default) or `docs/changelog.rst`
  (when the project has Sphinx docs: lower case, because the file name becomes
  the page URL). Never both, and no links or copies: Git doesn't track hard
  links, and symlinks are unreliable on Windows checkouts. If the file is in
  `docs/`, the README and `[project.urls] Changelog` link to the docs page, and
  `invoke.yaml` (`releaser: changelog:`) names the real path.
- **L6** Releases are tagged `vMAJOR.MINOR.PATCH` (annotated), e.g. `v1.0.0`,
  on the `[release] x.y.z` commit. The `v` is always present; the changelog's
  `:release:` lines and `pyproject`/`__version__` stay bare (`1.0.0`).

## 6. Code

- **C1** Type hints on new and touched code; `from __future__ import
  annotations` at the top of each module (after the module docstring). Ruff
  enforces this (`required-imports`, rule `I002`; `--fix` adds it, empty files
  are skipped). Excluded generated code (F6, e.g. migrations) is exempt, as
  are settings files with nothing to annotate (Sphinx `docs/conf.py`, Pelican
  `pelicanconf.py` and `publishconf.py`), via per-file ignores (F7).
- **C2** Google-style docstrings (`Args:`, `Returns:`, `Raises:`), with the
  summary on the first line after the opening quotes or on its own line, kept
  consistent within a module.
- **C3** `pathlib` over `os.path` (ruff `PTH`).
- **C4** Prefer newer constructs where `requires-python` allows: f-strings,
  `match`, `X | None`, `dataclass`, `tomllib`.
- **C5** `logging`, not `print`, for anything that isn't CLI output.
- **C6** Tests are pytest functions with plain `assert`.
- **C7** Every module starts with a copyright notice, e.g. `# Copyright (c)
  2026 Name`, personal projects included. Ruff's `CPY001` enforces it (a
  preview-only rule, so the template sets `preview = true` with
  `explicit-preview-rules = true`). The notice goes above the module docstring
  and the `__future__` import. Excluded generated code (F6) is exempt.

## 7. CI and automation

- **A1** `.github/workflows/check.yml` (lint and formatting only): on push, a
  `format` job runs `ruff check --fix`, `ruff format` and `taplo format
  pyproject.toml`, and pushes a `🤖 Apply style fixes` commit if anything
  changed; a `lint` job then runs `invoke lint` (ruff, `validate-pyproject`,
  taplo `--check`). Pull requests from forks only run `lint` (they can't be
  pushed to).
- **A2** `.github/workflows/test.yml` is a separate run: a `detect` job looks
  for test files, and the `test` job (a Python version matrix) runs only when
  there are some. Commits made by the `format` job use `GITHUB_TOKEN`, so they
  do not start new runs: `lint` re-checks the fixed code itself, but the tests
  run on the commit as pushed (the fixes are style-only).
- **A3** No pre-commit.
- **A4** Dependabot (`.github/dependabot.yaml`) for `uv` and `github-actions`
  ecosystems. (Assumed: see open items.)

## 8. Tooling repos

A tooling repo holds scripts, Claude plugins, automation or similar. It is not
installed as a package. It keeps the formatting, dependency, task and CI
standards, and drops the packaging ones.

- **K1** Declared with `[tool.python-style] kind = "tooling"` in
  `pyproject.toml`. Without that marker a repo is audited as a library.
- **K2** Start from `templates/pyproject-tooling.toml`: a minimal `[project]`
  table (`name`, `version = "0"`, `requires-python`, `dependencies`), the
  `[dependency-groups]`, `[tool.uv] package = false`, and the same ruff and
  pytest config as a library (with `testpaths = ["tests"]`).
- **K3** Not required: build backend, `license-files`, classifiers, project
  URLs, a `minchin/` package. Still required: F1-F9, D1-D5, `README`,
  a changelog (L5), `LICENSE.txt`, `tasks.py`, `.editorconfig`, `.gitignore`,
  `.gitattributes`, `.github/workflows/check.yml`. (`invoke.yaml` only
  configures `minchin.releaser`, so tooling repos don't need it.)
- **K4** Tests live in a top-level `tests/` (nothing ships), run by
  `test.yml` when present.
- **K5** `requires-python` is the minimum the scripts are run on, not a
  published promise: use the oldest Python on any machine that runs them.

## 9. Home Assistant integrations

A custom integration (a "custom component") is copied into Home Assistant's
`config/custom_components/` by HACS. Like a tooling repo it is never built or
published as a package, so it keeps the formatting, dependency, task and CI
standards and drops the packaging ones; Home Assistant and HACS add their own
requirements on top.

- **H1** Declared with `[tool.python-style] kind = "homeassistant"` in
  `pyproject.toml`. Start from `templates/pyproject-homeassistant.toml`: a
  minimal `[project]` table, `[tool.uv] package = false`, the same ruff config
  as a library, and Home Assistant's pytest settings. K3's list of what is
  and isn't required applies, with the changes below.
- **H2** Layout: the integration lives in `custom_components/<domain>/` (HACS
  requires this path), with `manifest.json`, `__init__.py`, `config_flow.py`,
  `constants.py`, `strings.json`, `translations/en.json` and `icons.json`.
  `hacs.json` is at the repo root. `known-first-party = ["custom_components"]`
  replaces `minchin` (F4).
- **H3** The version lives only in `manifest.json` (`"version"`), which HACS
  and Home Assistant read. `pyproject.toml` has `version = "0"`, and there is
  no `__version__`. `minchin.releaser` only bumps a Python version string, so
  there is no `invoke.yaml`; to release, update `manifest.json` and the
  changelog's `:release:` line, tag `vX.Y.Z` (L6), and publish a **GitHub
  release** from the tag (HACS offers releases to users, not bare tags).
- **H4** `requires-python` is the minimum Python of the Home Assistant release
  the tests run against (`pytest-homeassistant-custom-component` pins one
  exact `homeassistant`), and CI tests that one Python (A2). Separately,
  `hacs.json` `"homeassistant"` is the oldest Home Assistant release the code
  supports; raise it when the code starts using a newer API.
- **H5** Dependencies (D1, D2): Home Assistant provides most of what an
  integration needs, so `[project.dependencies]` is usually empty. A real
  runtime requirement goes in both `manifest.json` `requirements` (where Home
  Assistant installs it from) and `[project.dependencies]` (so tests and the
  lock see it). The `dev` group adds `pytest-homeassistant-custom-component`
  in place of a direct `homeassistant` requirement, since it pins the matching
  release.
- **H6** Tests live in a top-level `tests/` (K4), with a `conftest.py` that
  turns on the `enable_custom_integrations` fixture for every test (see
  `templates/homeassistant/conftest.py`). Test through config entries and the
  config flow (`MockConfigEntry`, `hass.config_entries.flow`), not by
  constructing entities by hand, so the test fails when Home Assistant
  couldn't load the integration. The pytest plugin needs Linux (`fcntl`): on
  Windows, run the tests under WSL with `UV_PROJECT_ENVIRONMENT` pointing at a
  Linux-side venv, so it doesn't clash with the Windows `.venv`.
- **H7** Keep the maths and parsing in modules that don't import Home
  Assistant, so they're easy to test and reason about; the platform modules
  only adapt them to entities.
- **H8** Follow Home Assistant's current integration conventions: setup
  through a config flow only (no YAML), state in `entry.runtime_data`,
  `_attr_has_entity_name = True` with a `translation_key`, entity names and
  form text in `strings.json`. Custom integrations only read
  `translations/`, which can't use `[%key:...%]` references, so
  `translations/en.json` is `strings.json` with them resolved, checked by a
  test.
- **H9** CI: `check.yml` and `test.yml` (A1, A2), plus `validate.yml`, which
  runs the HACS action (`hacs/action`, category `integration`) and
  `hassfest`. See `templates/homeassistant/validate.yml`.
- **H10** Root files: as K3, with `README.md` (HACS renders it as the
  integration's page) rather than `README.rst`.

## 10. Open items

- Type checker (mypy or ty) not yet required.
- The `fix` job pushes straight to the branch; protected branches would need a
  bot token or a change of approach.
- `.gitattributes` text normalization (`* text=auto`) is not yet standard.
