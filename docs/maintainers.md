# Maintaining the lab vault — handover guide

For whoever looks after the lab's records next. You don't need to be a programmer.

## What you are maintaining

- **The vault** — a folder of Markdown notes, opened with Obsidian, stored in a private git
  repository on GitHub. *This is the data.* It stays readable in any text editor without any of
  the tools below.
- **`labbase`** — a small optional Python tool (this repository) that checks the vault for
  mistakes and does chores (IDs, box maps, templates). If it ever stops working, the vault is
  still complete and usable; you just lose the automatic checks.

The rules of the vault are in its own `README.md`. The definition of every record type
(which properties, units, allowed values) is in `_schema/` — small text files you can edit.

## Daily life (everyone)

1. Open the vault in Obsidian. The *Obsidian Git* plugin pulls others' changes and saves yours
   every few minutes. Nobody types git commands.
2. Create notes with *Insert template* (templates live in `_templates/`), leave `id:` empty.
3. Use a vial → remove its position from the stock note and lower `vials_left`.
   Last one → `state: finished` (never delete the note).
4. Check the *Needs attention* table in `_views/Inventory.base`.

## Weekly (the maintainer, ~5 minutes)

```bash
cd path/to/lab-vault
git pull
uv run --project path/to/labbase labbase fill-ids .   # give new notes their IDs
uv run --project path/to/labbase labbase render .     # redraw box maps
uv run --project path/to/labbase labbase check .      # fix what it lists (also in _reports/check.md)
git add -A && git commit -m "Weekly maintenance" && git push
```

## Changing what a record type contains

1. Edit `_schema/<type>.yaml` (add a property, its `kind`, unit in the name, `help`).
2. Run `labbase templates` so new notes get the property, and `labbase render` so Obsidian
   knows its type (date, number…).
3. Existing notes don't need changing; add the property when you have the value.
4. Run `labbase check`.

## Installing the tool on a new computer

1. Install `uv`: see https://docs.astral.sh/uv/ (one command).
2. `git clone` this repository, then `uv sync` inside it.
3. `uv run pytest -q` should pass. Then `uv run labbase check path/to/lab-vault`.

## If something goes wrong

- **A note shows "Properties can't be read"** — a typo in the YAML at the top (often a missing
  quote around a `[[link]]`). Open it in source mode and compare with a template.
- **Someone overwrote something** — every change is in git history; Obsidian Git's
  *Open file history* or GitHub's *History* button shows and restores old versions.
- **Two people edited the same note at once** — git merges most cases; if not, Obsidian Git
  shows a conflict with both versions in the note; keep the right lines and delete the markers.

## History of this project

- 2026-10: a web app (FastAPI + SQLite) was built first, then deliberately replaced by this
  files-first design so the data outlives any software and any maintainer. The web app is kept
  at git tag `webapp-v0` for reference only.
