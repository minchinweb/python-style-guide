# Python Style Guide

The reference for how MinchinWeb's Python projects are set up. New projects
start from `templates/`; existing projects are audited against this file.

Rules are numbered (e.g. **T1**) so an audit can cite them. "Library" means a
package published to PyPI; "app" means something deployed, not published
(e.g. Django sites).

## 1. Tooling at a glance

| Concern                    | Standard                                                    | Replaces                             |
| -------------------------- | ----------------------------------------------------------- | ------------------------------------ |
| Formatter                  | `ruff format`                                               | black                                |
| Import sorting             | `ruff check` rule `I`                                       | isort                                |
| Linting                    | `ruff check`                                                | flake8, flake8-pyproject             |
| Dependencies / venv / lock | `uv` (`uv.lock`)                                            | pip-tools, `.requirements/*.in/.txt` |
| Build backend              | setuptools (>= 77)                                          | `setup.py`, `setup.cfg`              |
| Tests                      | pytest (Django `TestCase` for Django apps)                  |                                      |
| Task runner                | invoke (`tasks.py`), works on Windows with no extra install |                                      |
| Release                    | `minchin.releaser` via invoke                               |                                      |
| CI                         | GitHub Actions `check.yml` with `setup-uv`                  |                                      |
| Pre-commit                 | not used                                                    |                                      |

## 2. Formatting and linting (ruff)

- **F1** One tool: ruff. No `[tool.black]`, `[tool.isort]` or `[tool.flake8]`
  tables, and no black/isort/flake8 in dependencies.
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
- **D5** `invoke update` and `invoke upgrade` mirror `apt`:
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
  `README.md` for apps), `CHANGELOG.rst`, `LICENSE.txt`, `tasks.py`, `invoke.yaml`,
  `.editorconfig`, `.gitignore`, `.gitattributes`,
  `.github/workflows/check.yml` and `test.yml`. Docs in `docs/`.
  The audit checks the **exact casing** of these names (e.g. `CHANGELOG.rst`,
  not `changelog.rst`; `README.rst`, not `Readme.rst`; `LICENSE.txt`, not
  `License.txt`, `LICENSE` or `LICENSE.rst`; the `.txt` opens in Windows).
  Windows and the default git config are case-insensitive, so
  fix a wrong case with a two-step `git mv` (to a temporary name, then the
  right one). Build output (`build/`, `dist/`) and `.venv/` are
  git-ignored. No `env/` folder: `.venv/` only.
- **L5** Changelog is `CHANGELOG.rst` in the `releases` (Sphinx) format, which
  `minchin.releaser` edits.

## 6. Code

- **C1** Type hints on new and touched code; `from __future__ import
  annotations` at the top of each module (after the module docstring).
- **C2** Google-style docstrings (`Args:`, `Returns:`, `Raises:`), with the
  summary on the first line after the opening quotes or on its own line, kept
  consistent within a module.
- **C3** `pathlib` over `os.path` (ruff `PTH`).
- **C4** Prefer newer constructs where `requires-python` allows: f-strings,
  `match`, `X | None`, `dataclass`, `tomllib`.
- **C5** `logging`, not `print`, for anything that isn't CLI output.
- **C6** Tests are pytest functions with plain `assert`.
- **C7** A copyright/licence header is project-specific; company projects use
  ruff's `CPY` rule. Personal packages do not require one.

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

## 8. Open items

- Type checker (mypy or ty) not yet required.
- The `fix` job pushes straight to the branch; protected branches would need a
  bot token or a change of approach.
- `.gitattributes` text normalization (`* text=auto`) is not yet standard.
