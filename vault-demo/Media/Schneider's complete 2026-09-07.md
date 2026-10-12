---
id: MED-0004
type: media_batch
recipe: "[[Schneider's complete]]"
prepared_on: 2026-09-07
prepared_by: Lucía
volume_mL: 500
expiry: 2026-10-05
lots: [FBS 2F114, "Penicillin–Streptomycin 2875550"]
sterility: passed
---
# Schneider's complete 2026-09-07

Example data — replace with the real records.

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
