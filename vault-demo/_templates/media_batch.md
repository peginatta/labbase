---
id:
type: media_batch
recipe:
prepared_on:
prepared_by:
volume_mL:
expiry:
lots:
sterility:
created: "{{date}}"
---
# {{title}}

<!-- media_batch: One preparation of a media recipe. Its bottles are a `stock` note (content = this batch). -->

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
