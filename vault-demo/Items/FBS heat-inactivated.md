---
id: ITM-0003
type: item
aliases: [FBS, Fetal bovine serum, heat-inactivated, SFB, suero]
category: serum
supplier: "[[Gibco]]"
unit: mL
tracking: counted
reorder_at: 100
storage_C: -20
---
# Fetal bovine serum, heat-inactivated

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
