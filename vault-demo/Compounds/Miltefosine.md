---
id: CMP-0009
type: compound
aliases: [hexadecylphosphocholine, Impavido, MF]
reference: true
smiles: "CCCCCCCCCCCCCCCCOP(=O)([O-])OCC[N+](C)(C)C"
formula: C21H46NO4P
mw_g_mol: 407.57
cas: 58066-85-6
---
# Miltefosine

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
