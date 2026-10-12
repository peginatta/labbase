---
id: CMP-0010
type: compound
aliases: [aminosidine, paromomicina]
reference: true
salt_form: sulfate
cas: 1263-89-4
---
# Paromomycin sulfate

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
