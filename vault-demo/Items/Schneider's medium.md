---
id: ITM-0008
type: item
aliases: [Schneider, Schneider's, Schneider's Drosophila Medium]
category: medium
supplier: "[[Gibco]]"
unit: mL
tracking: counted
reorder_at: 500
storage_C: 4
---
# Schneider's Drosophila Medium

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
