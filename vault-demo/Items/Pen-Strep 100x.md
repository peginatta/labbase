---
id: ITM-0006
type: item
aliases: [P/S, pen strep, "Penicillin–Streptomycin (100×)"]
category: antibiotic
supplier: "[[Gibco]]"
unit: mL
tracking: confirmed
storage_C: -20
---
# Penicillin–Streptomycin (100×)

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
