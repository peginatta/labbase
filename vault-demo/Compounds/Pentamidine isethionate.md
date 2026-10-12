---
id: CMP-0011
type: compound
aliases: [pentamidina]
reference: true
smiles: "NC(=N)c1ccc(OCCCCCOc2ccc(cc2)C(N)=N)cc1"
salt_form: isethionate
cas: 140-64-7
---
# Pentamidine isethionate

SMILES is the free base; MW of the salt form to be confirmed.

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
