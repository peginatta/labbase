---
id:
type: strain
species:
ncbi_taxon:
who_code:
parent:
reporter:
markers:
plasmid:
passage_limit:
origin:
biosafety_level:
created: "{{date}}"
---
# {{title}}

<!-- strain: A parasite strain or line (e.g. L. infantum JPCM5, a luciferase reporter line). -->

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

## Boxes that contain it
```base
filters:
  and:
    - type == "box"
    - file.hasLink(this.file)
views:
  - type: table
    name: Boxes that contain it
    order:
      - file.name
      - label
      - where
```
