# 13: Genuine piece-2 rim fix (last blocker to 8/8)

**What to build:** a real rim for piece 2 — the only sherd unplaceable in every arm so far, and the last blocker between the current 7/7 + 11/11 and the full 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 11-patch-ablation-e2e (evidence below). Runs alongside ticket 12 (different files, different machines).

**Status:** results-in — worker run 2026-10-15: silent-drop fixed (p2 loads), gate 15/15 on patched arm / 12/15 ablated, E2E short of 8/8 (best 7/8 + 11/15, two arms). No commits; source fix lives as an uncommitted laptop edit for lead review.

## Comments (worker, 2026-10-15)

**Starting position (from 11, job 33061722):** ablated p2 wall rim is a 48-point stub (traced 141.5mm) ending in a 3-point terminal segment; the assembler silently drops piece 2 at load (log reads P02 Breakline_0 then jumps to P03, no error); gate pairs touching p2 are 0/4 strict (min_d 19.95/3.07/77.58/1.18mm). The patch points are NOT the answer (they poison the search). Guard-kept by design per ticket 04 — this ticket replaces the stub with a genuine rim or a principled second-chance rule, with numbers. Spartan leftovers: `pota11_bundle/`, `pota06_bundle/`, ticket-04 guard analysis.

- [ ] Diagnose first: is the stub short because the wall rim is genuinely missing from the surface extraction, or because segmentation/guards truncate it? Pin the stage with file:line + measurements (gate probe is the fast loop — laptop-legal)
- [ ] Fix, then prove: p2 loads (no silent drop) + gate pairs touching p2 pass strict + E2E 8/8 + 15/15 with the same-binary ORIG arm alongside
- [ ] If the fix is a guard second-chance rule rather than a longer rim, state the rule exactly (thresholds + file:lines) and show it fires only on genuine fragments, with the false-positive check
- [ ] Laptop poll per sbatch with sacct State/ExitCode; render before/after for the p2 rim (view resolves the millimetre scale) + measurement pair; no commits; Comments-only edits; E1 update proposal in Comments

## Comments (worker, 2026-10-15)

### Diagnosis: truncated, NOT genuinely missing (surface OK, sequencing drops 75%)
- The p2 wall surface exists and is the right wall: fresh S0 (11263 pts) sits on ORIG S1 with median 0.85mm (stride-4 NN; ticket-04 crossed S0-S1 0.40mm). NOT a surface-extraction loss.
- The 48-pt stub is genuine rim, just a sub-segment: 77% of stub points <2mm from ORIG B1 (median 1.15mm, max 3.0mm), covering ~25% of the true loop (traced 141.5 vs 301.7mm).
- Truncation stage pinned to the greedy sequencing walk, `original_nurbs_preprocessing/edge_line_ordering.cpp:72-107` (`getPointsInSequence`): the walk stalls dead once the current point's K nearest are all visited, idling through all remaining iterations. p2 S0: 183 in, 45 out (coverage 0.246). Python re-implementation of the same walk on the fetched surface reproduces the pipeline's traced length to 0.3mm (91.2 vs 91.455mm). Boundary detection (202 raw pts) and resampling (22->48) are innocent.
- The silent load-drop is the assembler's 50-point minimum, `sfs_main` pristine `sfspreproc-docker/hpc/tools/main_pristine_batch.cpp:87-91` (`point_.cols() < 50 -> off + Remove + continue`, no log line): 48 < 50 drops p2. Pristine program, cannot change — the rim must clear 50. Verified in job-33061722 `fresh_binary.log` (P02 Breakline_0 processed, next line is P03 Axis, no surfaces, no error).

### Fix: SFS-T13 second-chance sequencing (gated restart, threshold 0.40)
- Rule (in `getPointsInSequence`, after the unchanged pass-1 loop): if sequenced/input coverage < 0.40, keep walking — greedy step where possible, else jump to the nearest unvisited input point until all input is covered. Appended components stay contiguous so downstream peak detection splits at the jumps. Log lines `[SFS-T13] second-chance: ...` / `[SFS-T13] pass: ...` per surface.
- Threshold from the 16 Pot_A wall coverages in the pota06 log (seq->marched): p1 0.87/0.51, p2 0.25/0.41, p3 0.86/0.67, p4 0.90/0.81, p5 0.64/0.82, p6 0.89/0.86, p7 0.91/0.67, p8 0.74/0.90. 0.40 fires on exactly 1/16 (p2 S0 wall); the p2 S1 scrap (0.41) and all 14 others keep the byte-identical pass-1 path. Provisional (8 sherds, one pot), same status as the T04 guards.
- False-positive check, measured: the rerun fired once (`second-chance: 0.245902 -> 0.721311, 132/183, 4 jumps`; 132 = unique positions — the 183 input holds duplicates from the unclustered-NN improvement step). All 7 other pieces' Breakline_0 files are BYTE-IDENTICAL vs the pota11 bundle (`cmp -s` clean on p01,p03-p08). p2 wall: 48 -> 179 pts.
- Source fix is an UNCOMMITTED laptop edit (`original_nurbs_preprocessing/edge_line_ordering.cpp`, +93 lines, CRLF-clean per `git diff --stat`). Spartan ran the fix from an uploaded copy, then the tracked file was restored (`git checkout --`, verified byte-identical to pre-run backup, tracked tree clean). Note: Spartan `original_nurbs_preprocessing/build/EdgeLineExtractionHeadless` (gitignored artifact) currently contains SFS-T13; any rebuild from clean source reproduces pristine.

### Load + gate + E2E numbers (same-binary ORIG arm in job 33076114 throughout)
- LOAD: p2 loads in both fresh arms (fresh_binary.log: `Found 7 segments, 179 total points` then Surface reads; patched: 750 pts). Silent drop gone.
- GATE (laptop probe, strict d<2mm & |n.n|>0.85, bar >=2 inliers/pair; probe validated: ORIG 15/15, weakest 2-4 with 7): patched+fixed **15/15** (p2 pairs: 1-2: 4/0.25mm, 2-4: 8/0.81, 2-5: 21/0.31, 2-8: 8/0.81); ablated+fixed **12/15** (2-8 newly passes with 7; 1-2/2-4/2-5 at 0 strict, min_d 2.03/3.07/5.15mm). The 2-4/2-5 seams need patch content: the fresh exterior wall is a 171-pt scrap vs ORIG's ~12k-pt wall (mesh-stage loss, only on p2), and T14 patch rims are the only fresh content reaching those seams.
- E2E at k=5/b=3 (job 33076114 COMPLETED 0:0, 9:30): ORIG **8/8 + 15/15** (forest 124, control reproduced); fresh-ablated **7/8 + 11/15** (forest 258/65) — per-piece relative-rot scoring (0.00deg on ORIG): {1,3,4,5,6,7,8} perfect, p2 seated 120deg off (all 4 p2 edges wrong; the 11 non-p2 edges all correct); fresh-patched **5/8 + 7/15** (forest 441/36) — p2 never seated (no T_1 outputs), p3 61deg + p8 41deg off. Hybrid arm (patched p2 + ablated p3-p5, job 33076950 COMPLETED 0:0, 3:35): **7/8 + 11/15** (forest 257/51), p2 unseated, rest perfect. Patch poison confirmed again (441- vs 257-forest; p3/p8 flung only with patch on p3-p5).
- Jobs (all sacct State COMPLETED ExitCode 0:0): 33075684 build (SFS-T13-IN-BINARY), 33075826 edge-rerun+ablated-bundle, 33076114 3-arm E2E (orig/ablated/patched), 33076950 hybrid E2E. Laptop `slurm_poll.sh` exits immediately (does not block); polling was done via sacct. Spartan leftovers: `pota13_fresh/` (full patched output), `pota13_bundle/` (ablated E2E input), `pota13_bundle_patched/`, `pota13_bundle_hybrid/`, `sfs_main/pota13_verify_33076114/`, `pota13h_verify_33076950/`, sbatches `build_pota13`/`run_pota13_edge`/`run_pota13_assembly`/`run_pota13_hybrid`. Laptop evidence: `artifacts/pota13/` (gate/probe/score scripts, `pota13_p02_before_after.png` render: stub 141.5mm -> fixed 450.2mm traced incl. jumps vs authors 301.7mm, top view, equal aspect, mm scale).

### Verdict + E1 proposal
- Ticket-13 acceptance NOT fully met: p2 loads (was: silent drop) and gate hits 15/15 (patched), but E2E peaks at 7/8 + 11/15. The remaining failure is search, not rims: true p2 hypotheses exist at the gate (4-21 strict inliers), yet the k=5/b=3 beam seats p2 120deg off (ablated) or drops it (any patch content: patch poison, forest 441 vs 257).
- Next suspects, in evidence order: (1) p2's missing exterior wall at the MESH stage (fresh S1 = 171-pt scrap vs ORIG S0/S1 ~12-13k walls) — recovering it would give genuine 2-4/2-5 wall hypotheses and remove the patch dependence; (2) search-side: why the beam prefers a 120deg-off p2 pose supported by a single edge (2-8) over leaving p2 out.
- E1 `Where it stands` proposal for lead: fresh chain now loads all 8 sherds and reproduces the authors' gate (15/15, patched arm) but not yet the reassembly (best fresh 7/8 + 11/15 vs authors 8/8 + 15/15 reproduced same-binary) — the blocker moved from rims to search, with p2's mesh-stage exterior wall as the last known-missing input.
