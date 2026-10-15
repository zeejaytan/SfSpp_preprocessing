# 11: Ablate patch segments on p2–p5, re-run E2E

**What to build:** the test of 06's prime suspect — whether the ticket-14 patch-rim segments on pieces 2–5 are what exploded the search forest (522 vs 124) and sank E2E to 4/8 + 3/15.

**Answers:** E1

**Blocked by:** 06-gate-e2e-rerun (evidence above).

**Status:** results-in — lead review 2026-10-15: all four acceptance items present; job 33061722 COMPLETED 0:0 per sacct (execution confirmed); scored numbers rest on worker reads (logs + render worker-local, unseen by lead). Verdict: patches NOT the killer — load-bearing for gate, poison for search. Next: genuine p2 rim fix.

**Background (from 06, jobs 33051437/33054720/33055873):** gate 15/15 on fresh _0 rims; E2E fresh 4/8 + 3/15 vs ORIG 8/8 + 15/15 same binary; correct core {1,6,7}; 4,5,8 flung; 2,3 unplaced. Patch-augmented rims on p02–p05 are byte-different vs the Sept-28 bundle that assembled 8/8+15/15; p01,p06–p08 identical. Spartan leftovers to reuse: `pota06_fresh/`, `pota06_bundle/SfS_pp/`, `sfs_main/pota06_verify_33054720/`.

- [ ] Rebuild the fresh bundle with ticket-14 patch segments removed on p2–p5 (nothing else changed), re-run gate probe + E2E at k=5/b=3 with the same-binary ORIG arm alongside
- [ ] Report: gate x/15, E2E x/8 + x/15 fresh vs ORIG, hypothesis-forest size fresh vs ORIG, per-piece placement table
- [ ] Verdict with numbers: patch segments are / are not the E2E killer. If E2E still short, name the next suspect from the per-pair evidence (not a guess)
- [ ] Laptop poll per sbatch with final sacct State/ExitCode in ticket; Comments-only edits; no commits; E1 update proposal in Comments

## Comments (worker, 2026-10-15)

2026-10-15 POTA-11 run (assembly job 33061722, COMPLETED 0:0 in 6:47 per sacct; Spartan checkout 14ccae6, bundle built from pota06 leftovers): ablated ticket-14 patch points on p2–p5 by truncating Breakline_0 clouds to pre-patch lengths (p02 619→48, p03 484→146, p04 240→140, p05 317→135; kept points byte-identical, last segment end re-set, WIDTH/POINTS updated; only those 4 files differ vs pota06_bundle). Gate probe (task3_gate_probe logic, strict d<2mm & n·n>0.85): ablated **11/15** — failing pairs are exactly the 4 touching piece 2 (1-2, 2-4, 2-5, 2-8 at 0 strict inliers; min_d 19.95/3.07/77.58/1.18mm) vs patched 15/15 whose weakest pairs (1-2: 3, 2-8: 2 inliers) came from patch rims. E2E same binary (run_pota11_assembly.sbatch = run_pota06_assembly with FRESH_DS→pota11_bundle): fresh ablated **7/7 + 11/11** (assembler silently drops piece 2 at load — log reads P02 Breakline_0 then jumps to P03 with no surface reads and no error; placed {1,3,4,5,6,7,8}, all 11 non-p2 GT edges correct) vs ORIG **8/8 + 15/15** reproduced in the same job. Forest: fresh **312** (pruned 85) vs ORIG 124 (pruned 70), down from patched 522/57. Render: artifacts/pota11/pota11_p02_before_after.png (p02 XY, equal aspect, mm; kept 48 traced 141.5mm blue vs removed 571 traced 890.5mm red) + counts/traced table (p01 193/365.9, p02 48/141.5, p03 146/275.9, p04 140/265.1, p05 135/255.7, p06 137/260.3, p07 63/116.1, p08 56/106.2mm). **Verdict: patch segments are NOT the E2E killer — they are load-bearing for the gate but poison for the search.** Removing them drops gate 15/15→11/15 yet lifts the placeable 7-piece subassembly from 3/15 to a perfect 11/11 with forest 522→312. Piece 2 is unplaceable either way (guard-kept by design; its wall rim is a 48-pt stub ending in a 3-pt segment the loader silently drops). **Next suspect (evidence, not guess): piece-2's wall rim itself** — per-pair gate 0/4 strict without patch and the silent load-drop; full 8/8 needs a genuine p2 rim fix. E1 proposal for lead: fresh chain reproduces author input format + gate on placeable seams (11/11 edges, 7/7 sherds sans piece 2), not yet the full 8/8+15/15 reassembly; piece 2 remains the blocker. No commits.
