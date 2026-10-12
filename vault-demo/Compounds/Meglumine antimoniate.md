---
id: CMP-0008
type: compound
aliases: [antimoniato de meglumina, Glucantime]
reference: true
cas: 133-51-7
---
# Meglumine antimoniate

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
