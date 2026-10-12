---
id: STR-0002
type: strain
aliases: [JPCM5 luc, Li luc]
species: Leishmania infantum
ncbi_taxon: 5671
parent: "[[L. infantum JPCM5]]"
reporter: luciferase
markers: "example: G418"
passage_limit: 10
---
# *L. infantum JPCM5 Luc*

demo example — replace with real data

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
