---
id:
type: compound
code:
series:
reference:
smiles:
formula:
mw_g_mol:
salt_form:
cas:
pubchem_cid:
source:
created: "{{date}}"
---
# {{title}}

<!-- compound: A chemical entity (reference drug, series compound). Physical stocks are `stock` notes. -->

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
