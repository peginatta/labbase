---
id:
type: item
aliases:
tags:
category:
supplier:
catalog_no:
unit:
tracking:
reorder_at:
storage_C:
hazards:
created: "{{date}}"
---
# {{title}}

<!-- item: Something bought (medium, buffer, serum, antibiotic, solvent, consumable). Bottles/boxes of it are `stock` notes. -->

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
