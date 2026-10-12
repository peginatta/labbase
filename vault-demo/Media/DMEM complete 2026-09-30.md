---
id: MED-0001
type: media_batch
recipe: "[[DMEM complete]]"
prepared_on: 2026-09-30
prepared_by: Lucía
volume_mL: 500
expiry: 2026-10-28
lots: [FBS 2F114, "Penicillin–Streptomycin 2875550"]
sterility: passed
---
# DMEM complete 2026-09-30

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
