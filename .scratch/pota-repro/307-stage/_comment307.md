# Worker report — 307 (stage A + B + C), sfs307, 2026-11-05

All paths under `C:/PR/SfSpp_preprocessing` unless absolute. Git base: `e6adf69` ("307: dispatched to worker session sfs307"). Nothing committed, nothing pushed; the only working-tree change is `sfs_axes/potsac.py` (the `COST_PRUNE` switch, below).

## Provenance first (this decides which `.m` is "the authors'")

Two copies of the axis chain exist here and they are not the same:

| tree | commit | reading |
|---|---|---|
| `original_nurbs_preprocessing/AxisExtraction/` | `3095064` (2026-09-26, Zeejay Tan, "Vendor the pipeline source from the nested clone"); contents trace back to `405c048` (Sisung Liu, 2025-03-06, "250306_v1") | **the authors' code**, unmodified |
| `AxisExtraction/` | `ff40fc9` (2025-11-15, Zeejay Tan, "Local fixes: MATLAB bugs, headless build, path corrections, SFS format") | the working copy, **locally patched** |

`diff --strip-trailing-cr -r` between the two trees: every `.m` in the axis chain is identical **except `run_potsac.m`**. The single change is a locally inserted "ADAPTIVE" downsampling block (`AxisExtraction/run_potsac.m:18-27`), which the authors' file does not have. Ticket 304's claim that the under-5,000-point adaptive step "IS the authors' rule" is therefore **wrong**: it is a local fix. Everything below quotes the pristine tree.
