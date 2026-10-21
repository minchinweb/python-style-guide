# python-style-guide

Reference for setting up and maintaining my Python projects.

- [`STYLE.md`](STYLE.md) -- the numbered rules (formatting, dependencies,
  `pyproject.toml`, layout, code, CI).
- [`templates/`](templates/) -- starting files for a new library:
  `pyproject.toml`, `tasks.py`, `invoke.yaml`, `.editorconfig`,
  `.github/workflows/{check,test}.yml`.
- [`DEVIATIONS.md`](DEVIATIONS.md) -- how existing projects differ from the
  guide today (input for the audit skill).

## Starting a new project

1. Copy `templates/` into the new repo and rename `minchin.example`.
2. `uv sync`, then `uv run invoke check`.

## Updating an existing project

Use `DEVIATIONS.md` for the known gaps, then check against the rule numbers in
`STYLE.md`.
