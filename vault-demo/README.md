# Lab vault — how it works

This folder **is** the lab's database. Every record is a plain text file (Markdown) that you can
read with Obsidian, any text editor, or a script — today and in 20 years. Nothing here needs a server.

## The rules (short version)

1. **One note per thing.** A compound, a strain, a cell line, a freezer, a box, a stock of vials,
   a notebook entry — each is one `.md` file in its folder.
2. **The top of each note (Properties) holds the facts**, one per line: `species: Homo sapiens`,
   `passage: 8`. Write below the properties whatever you like (observations, protocols, photos).
3. **Link with double brackets:** `[[THP-1]]`, `[[−80 °C Freezer A]]`. Renaming a note in Obsidian
   updates every link automatically.
4. **Numbers carry their unit in the property name** and stay plain numbers:
   `volume_uL: 100`, `conc_mM: 10`, `mw_g_mol: 407.57`, `temperature_C: -80`.
5. **Each note has an `id`** (`CEL-0001`, `STK-0012`) for labels, spreadsheets and other labs.
   Leave it empty when you create a note — the `labbase fill-ids` tool fills it in.
6. **Never delete history.** When the last vial is used, set `state: finished` and keep the note.

## What goes where

| Folder | Type | One note per… |
|---|---|---|
| `Locations/` | `location`, `box` | room, freezer, fridge, shelf, rack, box (boxes are 9×9, positions A1…I9) |
| `Stocks/` | `stock` | **batch of physical containers** made or received together: one freezing of cells/parasites, one set of compound aliquots, bottles of one lot |
| `Compounds/` | `compound` | chemical (reference drugs, series compounds) |
| `Strains/` | `strain` | parasite strain or line |
| `Cell lines/` | `cell_line` | host cell line or primary cell type (THP-1, RAW 264.7, BMDM) |
| `Media/` | `media_recipe`, `media_batch` | recipe; one preparation of it |
| `Items/` | `item` | bought reagent/consumable (DMEM, PBS, FBS…) |
| `Suppliers/` | `supplier` | company or collaborator |
| `Notebook/` | `note` | experiment / observation / plan |

**"What it is" vs "the tubes":** `[[THP-1]]` (a `cell_line` note) describes the cells once.
Each freezing — "THP-1 p8, frozen 2026-01-15 by Marc, 5 vials in box *THP-1*, positions A1–A5" —
is a `stock` note pointing to it. Using a vial = remove its position from `positions` and lower
`vials_left`.

## Statuses (computed — never type them)

- **OK**
- **LOW** — you set `state: low`, or the total is below the item's `reorder_at`
- **STALE** — nobody updated `last_checked` for 30 days
- **EXPIRED** — past `expiry`
- **OUT** — `state: finished` or nothing left

## Where the rules are written down

`_schema/` has one small file per record type listing its properties, which are required, allowed
values and units. `_templates/` has a template per type (Obsidian: *Insert template*). `_views/`
has table views (Obsidian Bases): freezer contents, expiring soon, low/stale.

## The `labbase` tool (optional)

Not needed to read or write the vault. People who have it can run:

- `labbase check` — finds mistakes: broken links, two vials in the same box position,
  `vials_left` not matching positions, missing required properties, expired/stale stocks.
- `labbase fill-ids` — gives new notes their `id`.
- `labbase render` — redraws the box maps inside box notes.

## History

The vault is a git repository: every change is kept with who and when. In Obsidian the
*Obsidian Git* plugin saves and syncs automatically.
