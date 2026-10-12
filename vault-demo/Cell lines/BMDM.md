---
id: CEL-0001
type: cell_line
aliases: [BMDMs, BMM, bone marrow macrophages]
species: Mus musculus
ncbi_taxon: 10090
kind: primary
cell_type: Bone-marrow-derived macrophage
source: Own isolation
host_strain: BALB/c
medium: "[[DMEM complete]]"
differentiation: "M-CSF or L929-conditioned medium, ~7 days — adjust"
---
# BMDM

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
