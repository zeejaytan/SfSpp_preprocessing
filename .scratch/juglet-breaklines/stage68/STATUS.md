# stage68 STATUS (ticket 68: axis method, guard merge, densify arm)

Worker state file. LF only. Worker measurements, not lead-verified.

## Turn 1 (2026-11-03): Stage 0 + Part A start -- DONE, gate NOT met

- [x] STATUS scaffold
- [x] Stage 0 provenance
- [x] Stage 0 estimator survey (three estimators run, not just read)
- [~] Part A: nine axes estimated by every estimator; NONE meets the GT bar
- [x] commit worktree (stage68 scripts + this file only)

Nothing on Spartan was written. No Slurm job (0 of 4 budget). Dataset/, t66, t67 untouched (read-only
probe `probe68.sh`, then `scp` of 37 small files to the gitignored laptop landing zone
`SfSpp_preprocessing/artifacts/68/in/`). Candidate axis files written only to
`SfSpp_preprocessing/artifacts/68/axes/s{0,1,2}/` (PotSAC; scratch, not for use).

## Stage 0: provenance of Dataset/Axes/Juglet (2026-09-29 00:35)

- The files were COPIED, not generated, on 2026-09-29: SfSpp_preprocessing commit `8a30f977`
  (2026-09-29 00:37, "Juglet axes staged") says, in the ticket-16 addendum: "The MATLAB axis step DID
  run for the Juglet: all 9 axes sit in `Juglet_Dataset_20260916/SfS_pp/Axes/` (single-candidate, one
  line each, same format as Pot_A's) ... now staged at `Dataset/Axes/Juglet/`". Ticket 16 adds:
  "`Dataset/Axes/` is produced by MATLAB (`AxisExtraction/*.m`, PotSAC ...), not by the C++ pipeline."
- So the generator is the authors' MATLAB AxisExtraction (PotSAC = RANSAC over the Pottmann normal-line
  fit, then Cao LM refine), run on the 2026-09-16 Juglet bundle -- the bundle that U19 (:530-533) says
  does not survive. `Juglet_Dataset_20260916` is not at `/data/gpfs/projects/punim2657/` top level
  (probe68.sh: "No such file or directory"); not searched deeper (no recursive find under /data/gpfs).
- Consistent with that: our PotSAC port, seed 0, lands 10.2 deg from the old file on P2 (seeds 1/2:
  16.0/20.3) -- the same instrument family, run-to-run unstable.
- Open: which surfaces the Sep-16 MATLAB run read (pre-t47 vertex-dump era), and its seed.
  Piece 7's file has two lines (124 bytes; two PotSAC candidates).

## Stage 0: estimators surveyed (all run on the t66 arm-U S0/S1 walls)

Inputs: `runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom/Juglet_Piece_N.S{0,1}` (PLY ascii,
x y z nx ny nz curvature; 1,040-16,672 points per wall).

1. (b) `sfs_axes` (committed at repo root, this branch): Python port of the authors' MATLAB, proven equal
   to MATLAB on Pot A (pota-repro ticket 05, `tests/test_regression_pota.py` 8/8). Runs on laptop
   numpy 2.3.1; 1-9 s per piece. Ran PotSAC (step 1, MATLAB equal-count truncation, seeds 0/1/2) and
   plain Pottmann on all points.
2. (a) plain cylinder fit ("nperp"): direction minimising sum (n.d)^2 over both walls' unit normals
   (smallest eigenvector of N^T N). Deterministic, no seed.
3. (c) CSC lineage: not run this turn. `CSC/scripts/juglet_outline.py` (docs/lessons.md:467) fits the
   axis of the WHOLE juglet for outline work; it is not a per-sherd estimator.

## Part A results: GT gate, per-piece median folded angle (deg) to the other eight

Script: `fit68.py` (log `artifacts/68/fit68_run1.log`), `pott68.py` (log `artifacts/68/pott68_run1.log`).
Directions mapped by GT R (first 12 numbers of Juglet_Piece_N_T.txt, row-major 3x4).

| piece | old file | nperp | PotSAC s0 | s1 | s2 | Pottmann all | Pottmann S1 only |
|---|---|---|---|---|---|---|---|
| P1 | 26.8 | 19.1 | 47.7 | 58.5 | 37.6 | 28.5 | 27.4 |
| P2 | 77.3 | **16.1** | 46.9 | 44.1 | 50.8 | 43.8 | 41.8 |
| P3 | 29.9 | 14.6 | 61.5 | 52.4 | 50.8 | 41.3 | 22.6 |
| P4 | 27.1 | 14.0 | 65.9 | 72.0 | 76.3 | 59.4 | 53.4 |
| P5 | 55.2 | 43.4 | 52.7 | 44.0 | 54.5 | 33.2 | 23.2 |
| P6 | 18.7 | 13.8 | 52.7 | 59.9 | 36.9 | 29.4 | 20.6 |
| P7 | 24.0 | 70.8 | 68.3 | 45.7 | 39.5 | 30.7 | 23.0 |
| P8 | 18.0 | 18.3 | 83.2 | 69.2 | 69.9 | 44.3 | 38.2 |
| P9 | 63.6 | 53.2 | 54.0 | 61.5 | 40.3 | 76.9 | 75.6 |
| pieces <=10 / >25 | 0 / 6 | 0 / 3 | 0 / 9 | 0 / 9 | 0 / 9 | 0 / 9 | 0 / 5 |

- Bar (<=10 all) met by nothing. nperp is best (6 of 9 under 25, max of those 19.1), fixes P2
  (77.3 -> 16.1) but not P5 (43.4) or P9 (53.2), and breaks P7 (24.0 -> 70.8).
- PotSAC is seed-unstable on these sherds: same piece, three seeds, the axis moves 10-88 deg
  (P1 old-vs-new 49.5/45.7/66.1; P4 14.7/40.1/38.5). Pottmann S0-vs-S1 disagree 63.5 deg on P3,
  72.6 on P2.
- nperp eigenvalue ratio (how far normals are from all being perpendicular to one line; 0 = perfect
  cylinder): P1 0.157, P7 0.150, P5 0.081, P2 0.060, P3 0.052, P8 0.049, P9 0.038, P6 0.029, P4 0.027.
  P1 and P7 are doubly curved (neck/shoulder), where a cylinder model is wrong by construction.
- Two independent estimators agree on P1 (old vs nperp 9.0), P4 (2.8), P6 (6.1), P8 (1.9); yet those
  four still read 13.8-19.1 against each other in the GT frame. So either a ~15 deg floor is the
  estimator limit on 43-100 mm sherds, or the derived Juglet GT carries ~15 deg of attitude spread.
  Not separated this turn.

## Discrepancies to flag to the lead

- My old-file gate reads P1 26.8 / P2 77.3 / P3 29.9 / P4 27.1 / P5 55.2 / P6 18.7 / P7 24.0 / P8 18.0 /
  P9 63.6; the lead's t67 verification reads 23.1 / 77.2 / 29.3 / 25.0 / 55.0 / 17.1 / 23.1 / 15.6 / 63.5.
  Same ranking, differences 0.1-3.7 deg. Suspect: how the 2-line P7 file and the T-file layout were read
  (I take P7 line 1 and the first 12 numbers as row-major 3x4). Must be reconciled before any gate claim.
- `pott68.py` calls `refine_axis(vt, C)` with vt shape (6,), which the port rejects (matmul mismatch,
  "Returning initial axis estimate"), so the "pott_ref" column equals "pott": the Cao refine was NOT
  measured. My call bug, not a port bug; fix = pass vt[:, None].

## Estimator choice (worker's recommendation, for the lead)

Primary for next turn: **nperp (wall-normal cylinder fit), with the sfs_axes Pottmann line-complex as the
fallback on doubly-curved pieces** -- because it is the only estimator measured here that moves the
broken pieces in the right direction (P2 77.3 -> 16.1) and halves the hard fails (6 -> 3), it is
deterministic (the t67 axis gate and the matcher need a stable input; PotSAC moved 10-88 deg between
seeds), and it reuses existing code (the boot_axis.py idea, stage20). It does NOT meet the bar: P5, P7,
P9 fail. The honest reading so far is claim (1), method-limit on small sherds, with claim (3) (GT spread)
not excluded.

## Next turn

1. Reconcile the old-file gate with the lead's numbers (P7 two-line read, T layout).
2. Fix the refine call and measure Cao-refined Pottmann; try a profile-aware fit (normals as lines
   meeting the axis, robust IRLS over both walls, deterministic start = nperp) to address P1/P5/P7/P9.
3. Per-piece rule: pick the estimator by the nperp eigenvalue ratio (cylinder-like < ~0.06) -- decided
   from geometry only, never from the GT gate, to avoid fitting to the answer.
4. Only if a set reaches <= 25 deg on all nine (hard fail) stage it in a new run dir by substitution
   (t301 way) and rerun the t67 F20 panel (scripts in ../stage67/: submit67.sbatch, arm67.sh,
   stage67_inputs.py; floor 20, t66 lanes). If none does, rerun F20 with nperp anyway as a measured arm
   and report P5/P7/P9 as the open pieces.
