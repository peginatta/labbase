---
id:
type: cell_line
species:
ncbi_taxon:
kind:
cell_type:
source:
cellosaurus:
host_strain:
medium:
differentiation:
passage_limit:
biosafety_level:
created: "{{date}}"
---
# {{title}}

<!-- cell_line: Host cells — a cell line (THP-1, RAW 264.7) or primary cells (BMDM). -->

## Stocks
```base
filters:
  and:
    - type == "stock"
    - content == this
    - state != "finished"
views:
  - type: table
    name: Stocks of this
    order:
      - file.name
      - box
      - location
      - positions
      - vials_left
      - expiry
```

## Boxes that contain it
```base
filters:
  and:
    - type == "box"
    - file.hasLink(this.file)
views:
  - type: table
    name: Boxes that contain it
    order:
      - file.name
      - label
      - where
```
