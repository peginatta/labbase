---
id:
type: box
label:
parent:
slot:
rows: 9
cols: 9
temperature_C:
created: "{{date}}"
---
# {{title}}

<!-- box: A storage box with a grid of positions (A1 … I9 for 9×9). -->

## In this box
```base
filters:
  and:
    - type == "stock"
    - box == this
    - state != "finished"
views:
  - type: table
    name: In this box
    order:
      - file.name
      - content
      - positions
      - vials_left
      - passage
      - frozen_on
      - expiry
```

## Items in this box
```base
filters:
  and:
    - location == this
views:
  - type: table
    name: Items in this box
    order:
      - position
      - file.name
      - target
      - direction
      - status
```
