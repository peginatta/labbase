---
id: STR-0003
type: strain
aliases: [JPCM5, L infantum]
species: Leishmania infantum
ncbi_taxon: 5671
who_code: MCAN/ES/98/LLM-877
passage_limit: 10
origin: Dog, Spain
---
# *L. infantum JPCM5*

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
