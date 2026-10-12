---
id: CMP-0012
type: compound
aliases: [Pentostam, SSG]
reference: true
cas: 16037-91-5
---
# Sodium stibogluconate

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
