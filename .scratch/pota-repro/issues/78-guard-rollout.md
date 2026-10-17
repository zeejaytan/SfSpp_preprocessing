# 78: Guard roll-out to doubled-contour pots

**What to deliver:** forward-cone guard + split-then-select + inner-loop select applied wherever doubled contours recur (E/I/J forests dwarf ORIG) — per-pot gate recovery toward ORIG scale.

**Answers:** E1

**Blocked by:** 75 (landed, jobs 33292678/33292704/33292722 COMPLETED: SEL arm gate GREEN on C01 — 16pts, med 1.18mm, 100% <2mm, ZERO jumps, no reordering; C_G E2E 2/2+1/1; residual miss outside C01) + 67 (two-loop check: fresh count ~=2x ORIG + parallel-loop r-h marks doubled contours) + 39 (E/I/J forests dwarf ORIG — roll wherever the check fires).

**Status:** ready-for-agent

**Starting position:** run the two-loop check per pot (fresh count ~=2x ORIG + parallel-loop r-h), then apply the 75 recipe (forward-cone guard + split-then-select BEFORE sequencing + inner-loop select via Surface_0/1 standoff, no ORIG) wherever it fires. Prep-side scratch copies. Zero ORIG points in any fix; ORIG evidence-only.

**Rules:** land per pot with re-walked rims gated toward ORIG (median + coverage + jumps->0, NO reordering) + E2E at/above that pot's best fresh tally x3 same-binary + controls green in same runs; renders (eye-check) + a Needs-eye staged pair per the visual-evidence lane rule on the first pot that moves; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats >=3 per condition; no gate relaxation without a mechanism.

- [ ] Two-loop check per pot (E/I/J + others)
- [ ] Guard recipe wherever the check fires, one pot at a time
- [ ] Gate + E2E rerun x3 per pot or measured why-not
- [ ] Job IDs + sacct states
