# TODO for Academic Research Test Runners

## Active Development

- **`dblp.py`** (Modularized & Actively Maintained):
  - ✅ **COMPLETED**: Added Jürgen Schmidhuber test case (`pid: "s/JuergenSchmidhuber"`)
  - ✅ **COMPLETED**: Modularized code with `dblp_utils.py` for better parameter reuse
  - Current: Tests Yann LeCun, Geoffrey E. Hinton, Yoshua Bengio, Jürgen Schmidhuber
  - Code reduced from ~217 lines to ~140 lines (35% reduction)

## Deprecated (Moved to `deprecated/` folder)

- **`pubmed.py`** (No longer maintained):
  - Status: Moved to `deprecated/pubmed.py`
  - Original TODO: Add Jennifer Doudna test case - **NOT IMPLEMENTED**
  - Reason: Focusing only on DBLP for active development

- **`zenodo.py`** (No longer maintained):
  - Status: Moved to `deprecated/zenodo.py`
  - Original TODO: Add Tim Berners-Lee test case - **NOT IMPLEMENTED**
  - Reason: Focusing only on DBLP for active development

## Notes

The modularization effort focused exclusively on `dblp.py` to create a clean, parameter-reusable architecture. Other academic research test runners have been deprecated and moved to the `deprecated/` folder for reference purposes only.
