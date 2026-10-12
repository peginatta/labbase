---
id: STR-0004
type: strain
aliases: [Friedlin, L major]
species: Leishmania major
ncbi_taxon: 5664
who_code: MHOM/IL/80/Friedlin
passage_limit: 10
origin: Human, Israel
---
# *L. major Friedlin*

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
