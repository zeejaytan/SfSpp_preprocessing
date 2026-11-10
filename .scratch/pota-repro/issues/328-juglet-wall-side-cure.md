# Ticket 328 — Cure the Juglet wall-side inversion in the edgeline construction; every true join must be seen

**Status:** ready-for-agent (dispatch only after 327 is results-in; the Depends line is load-bearing)
**Answers:** E1
**Depends on:** 327 (the filing rule + file:line, the inversion mechanism, the proven cure direction)
**Blocks:** none
**Worker:** unassigned
**Budget:** large (8 failed acceptance runs; waiting costs none)

> **In one line.** With 327's rule and inversion mechanism bound, make the face→slot filing put the
> interior wall in slot 0 **by construction on the Juglet too** — one measurable rule, no piece IDs, the way
> 296 made it by construction for pots — and prove the correspondence stage now sees every true join:
> normal dots positive and strict-gate inliers > 0 on **all nine** touching pairs at GT, with the pot corpus
> untouched by a byte.

## What is already known

- **The construction precedent**: 296 (merged `0050313`): "the interior slot is by construction, not a
  per-piece swap" — proved on its pot 8/8 seat + 15/15 joins. The Juglet is the first object where that
  construction inverts (327 binds where and why).
- **The stopgap precedent** (81/210): per-piece slot-exchange surgery S0↔S1 + Bl_0↔Bl_1 — data-level, fast,
  and explicitly NOT what this ticket should land as the primary cure (the conservator's direction is the
  edgeline processing itself). It remains a measured fallback if the construction cure is proven infeasible,
  and only with the numbers that show why.
- **327 (once results-in)**: the census, the filing rule at file:line, the per-piece quantity that flips on
  2/6/9, the diagnostic swap's normal dots. Fill from its Comments; do not re-derive.
- **The five pairs that fail today** (326 bar 1): 1-2, 1-9, 2-5, 7-9, 6-7 (cross-wall normals); the four
  passing pairs are same-wall.
- **Loader gate to watch**: the assembler's 50-point loader gate tripped pot F06's 45-point interior loop in
  ticket 81 — check every Juglet interior loop's point count against it after the cure.

## What to deliver (stop on the first bar that fails and report it)

1. **The rule.** One measurable per-piece property (candidates: parent-surface radial label as in 175, mean
   radius about the piece axis, per-wall density) that (a) files interior in slot 0 on **all nine** Juglet
   pieces, and (b) agrees with the pot corpus wherever it is tested — at minimum re-run the filing on the
   pot(s) 296 proved and show their slots do not change. One code path; no piece IDs, no per-piece constants,
   no small-object flag.
2. **Cure arms, one variable each.** (a) **Construction**: fix the filing where 327 bound it so interior
   lands in slot 0 on the Juglet by the same construction that works on pots. (b) **Stopgap**: slot-exchange
   surgery on the three pieces (81/210 recipe) as a separate arm. Land the construction arm if it passes;
   land the stopgap only with the measured reason the construction arm failed.
3. **Correspondence bar (primary).** GTPAIR re-run at GT after the cure (326 harness): **all nine touching
   pairs dot_med_d3 ≥ +0.7, strict-gate inliers > 0 on each**; full before/after table per pair.
4. **Juglet E2E, two repeats** (the assembler is non-deterministic — Pot E gave 30/31+57/62 and 31/31+62/62
   from byte-identical inputs), GT-axes arm per the 326 template
   (`20261110-0320_41494d0_t320b-juglet/submit.sbatch`), report pieces seated and joins found honestly.
   Seam length may still cap pairs 2-9/3-5 (seams 3-6 samples against 7 needed — 326 bar 1): if seams remain
   the blocker after the normals pass, say exactly that; **do not touch the seam gate here — that is 326's
   territory.**
5. **Pot corpus untouched.** No bundle writes (list `Dataset/` + `original_samples/` before/after). If
   any generation code changed: byte-identity per 325's standard — `scripts/run_benchmark_172.py --cap 6
   --seeds 10 --step 10` byte-compared against
   `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323` (172 files); ANY
   differing file stops the arm; report the differing term + margin, never nudge thresholds.
6. **Renders** into `SfSpp_preprocessing/artifacts/pota328/renders/`: cured crack line on the inner wall
   per piece (before/after), plus E2E renders; workspace-relative Markdown links in the write-back.

## Must not

- No ORIG/GT points into the fix; the GT is the oracle, evidence-only.
- No per-piece hardcoding; no piece-ID switches; no small-object flags. The rule must be measurable per piece.
- No seam-gate, matching-gate or assembler changes (ticket 326 owns those).
- No gate relaxation without a mechanism; report blockers verbatim.
- Never `git worktree add/remove`; no commits/pushes; Comments-only ticket edits; end with exactly one
  `**End state:**` line; sacct-direct polling; no idle-polling PENDING jobs.
- Spartan compute only; runs under
  `spartan:/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t328<tag>/` with `run.json`,
  `submit.sbatch`, `logs/`, `out/`.

## Inputs

- 327's Comments (census, filing rule file:line, inversion mechanism, diagnostic numbers) — the ticket this
  one depends on.
- Juglet bundle + GT + 326 harness paths as in 327.
- Construction precedent: `.scratch/pota-repro/issues/296-seat-a-pot-and-prove-the-interior-slot.md`,
  `175-two-walks-two-slots.md`. Stopgap recipe: `81-swap-cure.md`, `210-swap-reseat-fresh.md`.
- E2E template: `20261110-0320_41494d0_t320b-juglet/submit.sbatch` (SIF `sfs_main/sfs_pristine_assembly.sif`,
  `-DJUGLET_ORIG`, `juglet_orig_block.inc`, FLOOR=20, NP=9); axes byte-identity reference above.
