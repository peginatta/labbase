---
id: CEL-0003
type: cell_line
aliases: [THP1]
species: Homo sapiens
ncbi_taxon: 9606
kind: line
cell_type: Monocyte (acute monocytic leukemia)
source: ATCC TIB-202
cellosaurus: CVCL_0006
medium: "[[RPMI-1640 complete]]"
differentiation: "PMA (e.g. 50 ng/mL, 48 h) — adjust"
passage_limit: 25
---
# THP-1

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
