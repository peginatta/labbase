---
id: ITM-0001
type: item
aliases: [DMEM, high glucose]
category: medium
supplier: "[[Gibco]]"
unit: mL
tracking: counted
reorder_at: 1000
storage_C: 4
---
# DMEM, high glucose

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
