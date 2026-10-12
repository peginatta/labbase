---
id: CMP-0001
type: compound
aliases: [AmB, anfotericina B, Fungizone]
reference: true
formula: C47H73NO17
mw_g_mol: 924.08
cas: 1397-89-3
---
# Amphotericin B

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
