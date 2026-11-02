# 65 — Get a cleanly separated surface on J1

**What to build:** the reason J1's growth does not separate cleanly along its break edge, and —
only if a cause can be proved — the smallest default-off change that makes it. "Clean" is defined
by the frozen scorer (`check_separation.py`), not by eye: Surface_0 must be one sheet that stops
at the break, so that the gap between the two surfaces is small **and** the boundary follows the
rim **all the way round**. J1 is the only one of the nine Juglet pieces that fails either half.
Diagnosis first; a null result is a valid ending and must be stated as one.

**Answers:** U19, E1

**Blocked by:** 63 (its instrumented walk is the instrument for stage 2a), 62 (its radius-1.0 cell
is the best baseline we have)

**Status:** ready-for-agent
**Working in:** —
**Branch:** 65-cleanly-separated-surface-on-j1, via `ticket_start.sh` at dispatch
**Worker:** —

## Spec

### Given (measured facts this stands on)

1. **The ruler is frozen.** `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep/check_separation.py`
   (read its docstring, lines 1-60, before anything else). Four numbers matter here and their
   definitions may not be re-invented:
   - **blind stretch** (deg): largest angular gap in Surface_0's boundary-fire dots around the
     break-edge ring. Degrees only — the "717 fold points" figure elsewhere is derived, never a
     measurement.
   - **far-skin share** (`farS0`): share of Surface_0's fold midpoints whose points sit on the far
     side of the wall (median offset < -0.8 mm along the mesh normal). Low is good.
   - **reverse coverage** (`f2r_le1` / `r2f_le1`): the two directions of "is the boundary where
     the rim is". `f2r_le1` = fold midpoints within 1 mm of a boundary point; `r2f_le1` = rim
     midpoints with a boundary point within 1 mm; `ring_cov_deg5` = degrees of the ring that have
     any boundary point at all.
   - **genuine pair**: median NN S1->S0 between 70-105 % of the piece's wall thickness AND median
     perpendicular residual <= 0.05 mm. This only says two surfaces sit a wall apart. **On J1 it is
     true and still wrong** — do not treat it as success.

2. **J1 today, best configuration known** (radius 1.0 mm, `SFS_NORMAL_MODE=radius
   SFS_NORMAL_RADIUS_MM=1.0`, worness 0.7; cell F of `runs/20261103-0035_ca520fe_t62-normalfix-s2`,
   tables in `work/lead-fast/frontier/{label_edge,reverse,union_edge}.tsv`):
   blind 68.38 deg (worst of nine; the other eight are 5.51-18.64), farS0 0.6729 (worst of nine;
   others 0.6923-0.8824), `f2r_le1` 0.6665 (others 0.9448-1.0), `r2f_le1` 0.4211 (others
   0.4578-0.6267), **ring coverage 250 of 360 deg** (others 315-360) — i.e. 110 deg of J1's rim has
   no boundary point anywhere near it. Median boundary-to-rim distance 0.46 mm, but 26 % of fold
   midpoints are more than 2 mm off and the worst is 6.12 mm. The count-mode baseline (t55,
   `runs/20261101-2004_05be12c_t55-worness07-breaklines`) reads blind 85.49, farS0 0.8624,
   `f2r_le1` 0.449, worst 8.545 mm, coverage 360 deg (a long jagged boundary that reaches every
   sector).

3. **What the radius fix did and did not do.** It removed the orientation flip (J1 flipped 41.63 %
   -> 0.2 %, ticket 62) and halved the median boundary error (1.274 -> 0.460 mm), and it made the
   boundary *shorter and more local* — which is why coverage fell 360 -> 250 deg. So the fault is
   no longer normals; it is **which points the growth claims**.

4. **J1's remaining defect is not wall bridging or orientation.** Those are measured and clean at
   radius 1.0 (t62/t63). The two things still wrong are geometric: the boundary sits off the break
   by a few millimetres on a third of the rim, and a third of the rim is missing from the boundary
   altogether.

5. **The surface is genuinely worn there.** Median normal turn against a geodesic window on J1:
   9.07 deg at 2 mm, 20.76 at 5 mm, 38.48 at 10 mm — about **3.8 deg/mm sustained to 10 mm**
   (t59 stage-0 signals, `runs/20261102-1144_638504b_t59-breakstop-stage0/out/stage0_summary.json`).
   The other eight turn 23-52 deg inside 2 mm then flatten. Implied round-over radius ~**13.8 mm**
   against 3.4-4.7 mm on the other eight, on a 65 mm vessel whose own curvature is ~19 deg per
   10 mm. A worn lip is physically a diffuse edge: any method may be limited to placing the line
   to a few millimetres, and a worn lip also cannot mate tightly. **That limit is not assumed here
   — it must be measured, and distinguished from a boundary that simply stops too early.**

6. **Worness is not the lever.** Swept 0.30-0.90 (t57): no value cleans J1 while holding all nine;
   J1 farS0 stays 0.776-0.912 across 0.55-0.90, and 0.30-0.50 swaps the surface identities. Treat
   `SFS_WORNESS` as a control, not a candidate fix.

7. **Dot counts are not evidence.** The same count-mode arm scored 28 dots in the t55 run and 58 in
   the t57 repeat; the mesh split is deterministic (S0 md5 stable), the edge stage is not. Any
   gate that reads Bl0 counts must first say which run it came from; better, do not use them.

8. **The 50-dot floor is the authors' own exclusion rule**, not a bug to lower (t58,
   `papers/text/sfspp-2502.13986v1.md:329`). SFS++ excludes short-breakline pieces rather than
   seating them, so "make J1's breakline longer" is not a route to a seated J1.

9. **Pot A is the control**: 8 pieces, thick walls (2.5-4.0 mm), 9/9 genuine pairs, none of them
   wearing this problem. Any change must leave Pot A within the usual tolerance.

10. **Instruments already on Spartan** (all verified present on 2026-11-03):
    - scorer: `runs/20261102-0450_05be12c_t57-sweep/check_separation.py`;
    - t59 region labels (wall/roll/fracture/anomaly per face) + true rim:
      `runs/20261102-1144_638504b_t59-breakstop-stage0/out/labels/<piece>.npz` (keys
      `V F labels core hit_dist hit_dot devs ball_radii lab_sens0 lab_sens1 vlab t_piece`;
      `labels` int8 0=wall 1=roll 2=fracture 3=anomaly; J1 = 35464/4276/4117/4735 over 48592
      faces; probe source `work/stage0_probe.py`);
    - t63 instrumented orientation walk: `runs/20261103-0211_249906a_t63-orientwalk/work/orient_walk.py`
      (through-wall MST edge count + flip share on the pipeline's own dumped points);
    - wall thickness: `runs/20261101-1613_83edd76_t54-worness-dial/out/wall40/<piece>_wall.json`;
    - t62 frontier probe kit (working imports, panels, tables):
      `runs/20261103-0035_ca520fe_t62-normalfix-s2/work/lead-fast/frontier/`
      (`t62_frontier.py` shows `sys.path.insert(...); import check_separation as cs`, and the arms
      list; `t62_labedge.py`, `t62_rev.py`, `t62_plot.py` are the three tables and the figure);
    - geometry bundles to read: `runs/.../t55.../out/geom` and
      `runs/20261103-0035_ca520fe_t62-normalfix-s2/outF/geom` (`<P>.{S0,S1,Bl0,Bl1}`);
    - meshes `/data/gpfs/projects/punim2657/Dataset/Mesh/Juglet` (J1 md5
      b447066c29181fe7ba987439c22c5d9c);
    - the per-piece pipeline driver to adapt:
      `/c/PR/SfSpp_preprocessing/.scratch/juglet-breaklines/stage55/instruments/run_cell55.sh`
      (stage -> mesh stage -> export -> edge stage) and the submitter beside it (`submit55.sh`,
      twelve laptop-side gates).

### Build

Work in this order. Each stage ends in a number you can be wrong about. **Do not skip stage 1 to
get to a fix**: three earlier attempts to fix J1 by knob died because the defect had not been
located.

**Stage 0 — reproduce and localise (no new pipeline run).** Re-run the scorer and the three
frontier tables for J1 against the frozen bundles, and confirm you reproduce the Given numbers
(j1 blind 68.38, farS0 0.6729, f2r 0.6665, r2f 0.4211, coverage 250). If you do not, stop and
report the discrepancy rather than proceeding on a number you cannot reproduce. Then localise: for
J1 only, bin the rim ring into 10-deg sectors and report, per sector, (i) the boundary-to-rim
distance distribution, (ii) whether a boundary point exists at all, (iii) the local wall thickness
and t59 label mix (wall/fracture/roll), (iv) the local normal-turn rate. **The deliverable is a
per-sector table plus one figure** showing the rim, the S0 boundary, and the sectors that fail,
from a viewpoint that resolves 1 mm (a bad viewpoint is a bad measurement: state the camera
placement and the in-plane scale). This alone answers "which part of J1 is broken" and it is
cheap.

**Stage 1 — characterise the boundary: what, physically, is the S0 boundary on J1?** In the worst
sectors, ask whether the boundary is (a) a genuine stop at the break, (b) a slice through the
sheet where the growth stopped claiming wall, or (c) an artefact of the split (the pixels near the
seam assigned to the other sheet). Test each with the existing labels: the boundary's own t59
label mix; whether points just outside the boundary are claimed by S1 (double-cover table,
`dc_ge1` is 0.1205 on J1 at t55 — check the radius-1.0 value); and whether the boundary follows a
smooth curve across the sheet rather than the rim. **Gate 1:** every failing sector is assigned
to (a), (b) or (c), with the measurement that decides it, and the split of failing rim across the
three. If some sectors are genuinely (a) — a worn, diffuse edge — say so and quantify the
irreducible error there.

**Stage 2 — test the candidate causes, cheapest first.** Only the causes stage 1 implicates.
Candidates, with the prediction each makes (a cause that makes no falsifiable prediction is not a
candidate):

- **2a — detachment / wall claim.** If the failure is (b) or (c), the growth is deciding the wall
  face belongs to the other sheet. Prediction: on J1, wall-labelled points adjacent to the
  boundary are claimed by S1 at a higher rate than on the other eight, and the failing sectors are
  the thin ones (J1's thinnest smooth wall is **1.463 mm** vs 1.585 J2 / 1.980 J7; ticket 63).
  Measure with the t63 walk and the labels. If this is the cause, the fix is a claim rule, not a
  threshold.
- **2b — the split/termination rule.** If the failure is (b), the sheet is being cut by the
  clustering's own termination, not by the geometry. Locate the code path that ends the growth and
  show which condition fires first on J1 and not on the other eight. Read the source before
  guessing: `mesh_processing_headless.cpp` (growth and merge from ~:4940 onward; worness ladder
  :4845-4910; surface export :4993-5030).
- **2c — the worn-edge regime.** This one already has a measured answer: worness 0.30-0.90 cleans
  nothing (t57). Re-run one point only if a new mechanism demands it; do not sweep again.
- **2d — something not on this list.** Allowed and welcome, provided it comes with its own
  falsifying test.

**Gate 2:** one named cause (or an explicit "no single cause found"), the prediction it made, and
whether the prediction held. A cause whose prediction fails is reported as refuted, not reframed.

**Stage 3 — the smallest change, default-off, measured on all nine plus Pot A.** Only if stage 2
produces a cause whose prediction held. Constraints: unset behaviour byte-identical; no default
change; no retuning of the frozen scorer's constants; the change is small enough to review in one
sitting. Measure with the same scorer on all nine Juglet and Pot A 8, against both baselines (t55
count-mode and t62 cell F radius 1.0).

**Gate 3 (the only definition of "cleanly separated" this ticket accepts):** J1 blind <= 20 deg,
`r2f_le1` >= 0.90 and ring coverage >= 340 deg, farS0 >= 0.85, worst boundary error <= 2 mm; the
other eight stay within 0.08 mm on median boundary error and hold 9/9 genuine pairs; Pot A shows
no harm. **If stage 3 cannot clear gate 3, say so plainly and record what J1's floor is** — the
measured irreducible error at the worn sectors — because that number is what the assembler
question actually needs.

### Report back (the worker's write-up)

Append a `## Results` section to this ticket: the per-sector table, the figure path, the cause
with its prediction and verdict, every job id with its `sacct` State/ExitCode, and **one short
plain-language paragraph** a conservator can read: what was wrong with J1, whether it is fixed,
and if not, how wrong the best result is in millimetres of misplacement on the pot. Name which
claim you are making — "the method fails on J1", "the measurement was broken", or "the reference
is wrong" — do not blur them. Add no `Status`/`Branch` edits, no commits, no merges;
`verdict`/`human_note` in `runs/index.tsv` stay empty for the lead.

### Gates and budget

- Corpus read-only; `inputs.diff` empty; the unset arm byte-identical.
- Every `sbatch` polled with `scripts/slurm_poll.sh <JOBID>`; final `sacct` State/ExitCode in the
  ticket.
- Budget: <= 6 jobs, <= 5 h wall total. Stage 0/1 need **no** new job — they read frozen outputs;
  say so before submitting anything.
- Heavy work on Spartan compute nodes, never the laptop or the login node; small scoring runs may
  share a held allocation (`scripts/gpu_session.sh`).

### Traps (paid for already)

- SSH from this laptop: `C:/Windows/System32/OpenSSH/ssh.exe spartan` (Git Bash `ssh` has no key);
  poll `sacct` directly.
- Spartan python: `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3` (no pandas —
  aggregate in awk or fetch small TSVs to the laptop).
- sbatch files need Unix line endings (a DOS-ending sbatch was rejected once); `bash -n` and
  `py_compile` every script before it is submitted.
- Jobs must fetch the worktree commit before building; verify the commit hash in the job log
  against `git rev-parse HEAD`.
- A FAILED row in any TSV must carry the same field count as the header.
- `grep -a` on binary PLY/PCD; PLY header length varies — never parse it, record size+md5.
- Unset every `SFS_*` and `POT_NAME` between pieces.
- Single writer in `.scratch/`: run `python C:/PR/scripts/check_scratch_writer.py SfSpp_preprocessing`
  before editing, and only inside your own worktree.
- Do not re-tune the scorer's frozen constants, and do not compute "blind stretch times a density"
  to get a point count: the fold's angular density is far from uniform (36 ten-degree bins, mean
  78.4, sd 70.2, range 4-266).

### Out of scope

- Adopting radius 1.0 mm as a pipeline default (ticket 64 / the conservator's decision).
- Ticket 64's adaptive radius rule (built separately; this ticket must not depend on it).
- The full assembly run, and any judgement about whether J1 *should* seat.
- The edge stage's non-reproducibility (28 vs 58 dots): if it blocks a measurement, record it and
  route around it — fixing it is its own ticket.
- Changes to `check_separation.py` or the t55/t62 baselines.
