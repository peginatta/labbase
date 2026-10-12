---
id: STR-0001
type: strain
aliases: [L donovani, LV9]
species: Leishmania donovani
ncbi_taxon: 5661
who_code: MHOM/ET/67/HU3
passage_limit: 10
origin: Human, Ethiopia
---
# *L. donovani LV9*

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
