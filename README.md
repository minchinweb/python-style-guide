# python-style-guide

Reference for setting up and maintaining my Python projects.

- [`STYLE.md`](STYLE.md) -- the numbered rules (formatting, dependencies,
  `pyproject.toml`, layout, code, CI).
- [`templates/`](templates/) -- starting files for a new library:
  `pyproject.toml`, `tasks.py`, `invoke.yaml`, `.editorconfig`,
  `.github/workflows/{check,test}.yml`.

`DEVIATIONS.md` (how my local projects differ from the guide) is generated on
each machine by `/python-style:survey` and is git-ignored, since it names
private projects.

## Using it

The [`python-style`](https://github.com/minchinweb/claude-skills) Claude Code
plugin bundles this guide (as a submodule) with two skills:

- `/python-style:audit` -- audit and fix one project, or start a new one.
- `/python-style:survey` -- summarize many projects into `DEVIATIONS.md`.

```
/plugin marketplace add minchinweb/claude-skills
/plugin install python-style@minchinweb-skills
```

## Starting a new project

1. Copy `templates/` into the new repo and rename `minchin.example`.
2. `uv sync`, then `uv run invoke check`.
