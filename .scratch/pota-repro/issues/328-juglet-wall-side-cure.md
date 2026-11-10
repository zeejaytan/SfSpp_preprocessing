# Ticket 328 — Cure the Juglet wall side: file the interior face without trusting a broken axis, and re-sign the exported line

**Status:** ready-for-agent (327 is results-in; both halves of the cure are now measured)
**Answers:** E1
**Depends on:** 327 (results-in, merged 0868d14) — the filing rule, the two failure modes, and the swap's 3/5
**Blocks:** none
**Worker:** unassigned
**Budget:** large (8 failed acceptance runs; waiting costs none)

> **In one line.** 327 proved the defect is two independent faults upstream of the assembler: the mesh stage
> files the **outer** wall into slot 0 on pieces 2, 6 and 9 (a vote on normals against the axis line, which
> silently keeps the denser face when the vote degenerates), and the exported breakline carries a sampled
> surface normal that **flips sign inside one line**. Fixing only the filing gets three of the five failing
> joins; the other two (1-9, 6-7) need the line's normals re-derived against the wall it sits on. Do both,
> keep the ten pots byte-identical, and the correspondence stage must see all nine true joins.

## What is already known (327, verify-by-reproduction not re-derivation)

**(a) The split is exactly pieces 2, 6, 9** (`census_bar1.json`; r_mean S0/S1 mm 17.02/14.75, 16.93/14.59,
17.21/15.22; the other six inner). `Breakline_0` rides `Surface_0` on 9/9 (0.28-0.62 mm against 1.83-2.49 mm
to S1), so the choice is made in the **mesh stage** and the edgeline inherits it. Per-wall densities are flat
(0.543-0.560 pts/mm) — density does not explain the split.

**(b) The rule and where it fails.** `classifyAndOrderPaper234` (`mesh_processing_headless.cpp:3688`) votes
`satA = inFrac[0]*n0 + (1-inFrac[1])*n1` against `satB = (1-inFrac[0])*n0 + inFrac[1]*n1`, where `inFrac` counts
normals whose ray to the `SFS_AXIS_FILE` line meets it on the positive side (:3705-3718); it swaps only when
`satB > satA` strictly (:3725). It is called at :4008 **after** `std::sort(clusters..., myobject3)` — the
denser face first — so a degenerate vote keeps the exterior in slot 0. There is no check against geometry.
- **Wrong-side axis (pieces 2, 9):** the shipped DS axis is 87.8° and 73.3° off the GT axis; re-voting with
  the GT axis files them correctly (`interior_gt = face1`, inFrac_S0 0.000 / inFrac_S1 0.999 and 0.951).
- **Flipped normals (piece 6):** axis is fine (13.3°), yet the shipped slot 0 is the outer wall — its normals
  were negated upstream (it is the only piece whose mesh log prints `Normals flipped: true`; the negation is
  at `checkNormalsIntersection` :3144 / :4145-4164).

**(c) The swap alone is not enough** — job 34687732 (COMPLETED 0:0), copies only, 3 of 5 pass:
1-2 −0.896→+0.704, 2-5 −0.991→+0.948, 7-9 −0.674→+0.708, **but 1-9 −0.945→−0.039 (4/7 negative) and
6-7 +0.106→−0.183 (10/15 negative)**. Three sign variants (job 34690603) only reflect those numbers, and
negating 2/6/9 breaks the three that had passed: the sign is mixed **within** a line (piece 9's swapped-in
walk is 17% outward overall and −0.74..+0.07 at the section meeting piece 1; piece 7's own line swings
−0.80..+0.61). The exported line stores the sampled surface normal.

**(d) Precedents.** 296 (merged `0050313`): "the interior slot is by construction, not a per-piece swap",
proved 8/8 + 15/15 on its pot — the construction this ticket must extend to the Juglet. 81/210: per-piece
slot-exchange surgery (fallback arm only). 175: parent-surface separation. The axis half overlaps ticket 325
(the scale-free axis finder) but this cure must not depend on it being right.

## What to deliver (stop on the first bar that fails and report it)

1. **Filing that cannot be inverted by a bad axis.** Make the slot decision self-checking: the chosen
   interior face must satisfy an independent geometric test (e.g. smaller mean radius about the piece's axis,
   or the parent-surface wall label of 175) **and** the normal vote; on disagreement, say which wins and why,
   with numbers per piece. A degenerate vote must not fall back to size order. Same code path for pots and
   Juglet; no piece IDs, no per-piece constants, no small-object flag.
2. **Line normals re-derived against the wall.** The exported `Breakline_0` normals must point from the
   interior wall it lies on, per point, not be copied from the sampled surface. Show the per-point agreement
   with the wall's own normal (fraction correct, before/after per piece) and prove 1-9 and 6-7 stop reading
   as opposing rims.
3. **Correspondence bar (primary).** 326 harness at GT after the cure: **all nine touching pairs
   dot_med_d3 ≥ +0.7 and strict-gate inliers > 0 on each**; full before/after table. If a pair still fails,
   name the remaining mechanism with its numbers rather than nudging the bar.
4. **Juglet E2E, two repeats** (assembler is non-deterministic: Pot E gave 30/31+57/62 and 31/31+62/62 from
   byte-identical inputs), GT-axes arm per the 326 template, report seated pieces and joins honestly. Seam
   length may still cap 2-9 and 3-5 (3-6 samples against 7 needed) — if seams remain the blocker after the
   normals pass, say exactly that; **do not touch the seam gate (326 owns it)**.
5. **Pot corpus untouched.** No bundle writes (list `Dataset/` + `original_samples/` before/after). If any
   generation code changed: byte-identity per 325's standard — `scripts/run_benchmark_172.py --cap 6 --seeds
   10 --step 10` byte-compared with `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323`
   (172 files, 251 lines); ANY differing file stops the arm — report the differing term and margin, never
   nudge a threshold. Note the run-to-run spread: the mesh stage draws 30 unseeded ray-cast points
   (`mesh_processing_headless.cpp:1526-1527`), so compare against that piece's own measured spread where it
   is not zero (Pot H 02 moved 0.867 mm; Pot J 09 was exactly 0.000000 across four runs).
6. **Renders** into `SfSpp_preprocessing/artifacts/pota328/renders/`: cured line on the inner wall per piece
   with its normals drawn, before/after, plus E2E renders; workspace-relative Markdown links in the
   write-back; eye-check every one.

## Must not

- No ORIG/GT points into the fix; the GT is the oracle, evidence-only.
- No per-piece hardcoding, no piece-ID switches, no small-object flags.
- No seam-gate, matching-gate or assembler changes (ticket 326 owns those).
- No gate relaxation without a mechanism; report blockers verbatim.
- Never `git worktree add/remove`; no commits/pushes; Comments-only ticket edits; end with exactly one
  `**End state:**` line; sacct-direct polling; no idle-polling PENDING jobs.
- Spartan compute only; runs under
  `spartan:/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t328<tag>/` with `run.json`,
  `submit.sbatch`, `logs/`, `out/`.

## Inputs

- Ticket 327 (results-in): census, rule, failure modes, swap tables, renders
  (`C:/PR/worktrees/sfs/327-juglet-wall-side-cause` until closed; merged at 0868d14 on main).
- Juglet t66 bundle `20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom`; GT `Dataset/Juglet_GT`.
- 326 harness `C:/PR/worktrees/structure-from-sherds-pp/326/hpc/tools/diag326_pairs.cpp` (read-only).
- E2E template `20261110-0320_41494d0_t320b-juglet/submit.sbatch` (SIF `sfs_main/sfs_pristine_assembly.sif`,
  `-DJUGLET_ORIG`, `juglet_orig_block.inc`, FLOOR=20, NP=9).
- Precedents: `296-seat-a-pot-and-prove-the-interior-slot.md`, `175-two-walks-two-slots.md`,
  `81-swap-cure.md`, `210-swap-reseat-fresh.md`.
