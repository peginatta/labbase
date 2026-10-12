---
id: ITM-0005
type: item
aliases: ["PBS 1×, pH 7.4 (no Ca²⁺/Mg²⁺)"]
category: buffer
supplier: "[[Gibco]]"
unit: mL
tracking: confirmed
storage_C: 4
---
# PBS 1×, pH 7.4 (no Ca²⁺/Mg²⁺)

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
