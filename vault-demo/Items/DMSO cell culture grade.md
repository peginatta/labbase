---
id: ITM-0002
type: item
aliases: [DMSO, cell-culture grade]
category: solvent
supplier: "[[Sigma-Aldrich]]"
unit: mL
tracking: confirmed
storage_C: 20
---
# DMSO, cell-culture grade

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
