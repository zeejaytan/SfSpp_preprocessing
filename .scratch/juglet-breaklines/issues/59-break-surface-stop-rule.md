# 59 — Stop the growth at the break surface: measure four signals, then build one stop rule

**What to build:** a measured answer to which physical signal can make the surface
growth stop at the break surface on a worn lip — Stage 0 measures the four candidate
signals' separability on the real geometry (read-only, no pipeline change), and only a
signal that separates gets implemented as an opt-in growth stop, judged by ticket 57's
separation gate. A Stage 0 negative (no signal separates) is an acceptable outcome and
the ticket records it and stops.

**Why now (2026-11-02, conservator):** "stop when you reach the break surface, that's
precisely we trying to workout and failing ... the angle of break surface is sharper, so
this is the why i am proposing do the test that detect the angle for longer distance.
what else you can do to 'stop when you reach the break surface'???" — and then:
"write the ticket and dispatch". Ticket 57 closed the angle-cap route: no value of
SFS_WORNESS in 0.30-0.90 separates the two sheets while holding 9/9 genuine pairs.

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines
let SfS find joins)

**Blocked by:** none (uses the t55 run of record and the t57 gate READ-ONLY)

**Status:** resolved
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 59-break-surface-stop-rule, in /c/PR/worktrees/sfs/59
/data/gpfs/projects/punim2657/SfSpp/runs/)
**Worker:** DSH subagent (ticket-59 worker) — measures only; the lead verifies, commits and judges

## Spec

### Given (measured facts this stands on)

- **The stop rule cannot express the fix as an angle cap.** Ticket 57 (merged 4ae66b5):
  J1 far-skin share 0.776-0.912 for every arm 0.55-0.90 (in-arc 0.93-1.00); the lower
  values at 0.30-0.50 are a surface-identity swap (0.30: S0 2,532 pts vs S1 13,825) and
  lose pairs. The lip's bend is a median 3.8-4.6 deg dihedral over a roll radius
  ~15.7 mm (circle-fit residual median 1.23 mm) — below every working theta (6.4-17.1
  deg at the 0.7 dial). The growth-stop test (mesh_processing_headless.cpp:4894-4908,
  theta consumed by the region-grow at :3853) only fires on a bend that exceeds theta;
  a worn lip has no kink to catch.
- **The data is at the edge; the rule walks past it.** Nearest Surface_0 point to the
  true break edge: median 0.60 mm (ticket 56 probes). In the J1 blind stretch the
  boundary runs ~5.0 mm inside the true edge (working arc 0.00 mm), the region sits on
  the far face one wall through (ray-cast slab [-1.76, 0] at a blind-arc fold point vs
  [-3.16, 0] at a healthy skin point), 47/48 fold points and 85% of S0 points within
  5 mm of the blind fold are far-side.
- **Signals already measured as separating on J1 (lead, 2026-11-01/02):**
  plane-fit deviation — neighbours sit median 1.66 mm off the anchor's tangent plane in
  the blind arc vs 0.77 mm in the clean arc; 16.3% of S0 points carry own material
  >1.4 mm behind their normal (31% blind arc, 7% elsewhere). The conservator's
  long-distance turn test: the roll turns at ~3.6 deg/mm (R ~15.7 mm); the wall's own
  turn rate is UNMEASURED — Stage 0 measures it.
- **Precedent we own on this vessel:** TORA U17 Layer 2 (2026-10-03) detected break
  surfaces from shape alone using per-sherd wall thickness; the estimate matched the
  Juglet's known ~1.8 mm wall and the conservator's eye check passed (different
  codebase; method transfer, not code reuse).
- **The mesh exists and has connectivity the cloud lacks.** J1 mesh: watertight,
  24,294 V / 48,592 F, closed solid (Dataset/Mesh/Juglet/Juglet_Piece_1_Mesh.obj). The
  cloud the growth runs on was sampled FROM it (ticket 47). Mesh adjacency allows
  dihedral region-grow labelling that the cloud cannot do.
- **A fold radius estimator already exists** for the paper formula
  (medianFoldRadius45, mesh_processing_headless.cpp:4872) — the measured scale any
  turn-window should be tied to.
- **The mesh stage retries a theta ladder** when a piece does not split into two
  regions (mesh_processing_headless.cpp:3707-3745); any new stop rule interacts with it.
- **The judge exists.** check_separation.py (run 20261102-0450_05be12c_t57-sweep, md5
  054ee00da99a1cf58d9d84ae5e0d361a) reports far-skin share (primary), double-cover,
  seam share, blind extent, Bl0 dot counts, genuine pairs per arm; thresholds are
  flags; runs rc0 on the t55 baseline. Baseline: metrics/baseline_t55.tsv in that run
  dir. t55 run of record: runs/20261101-2004_05be12c_t55-worness07-breaklines (Bl0
  dots J1..J9 = 28/32/38/32/47/46/54/41/23; mesh-stage binary md5
  736ff95c976486d17f7c00b3af402040).
- **Corpus traps (paid for already):** out/geom *.S0/.S1 files are ASCII PLY despite
  the extension (trailing camera element adds a bogus row if the header is ignored);
  use exact point-to-triangle distance, never nearest-vertex (a vertex can sit 0.4 mm
  off its own surface); area-weighted mesh vertex normals; JUGLET_BASE
  (data_path.h:1502) is NOT on Spartan and Dataset/Breaklines holds only Pot_A;
  /tmp on the login nodes gets wiped — keep probe scripts in the run dir; plain scp
  to the laptop fails on publickey — use the ssh_download tool.

### Task

1. **Stage 0 — separability measurement (read-only; no pipeline change).** Label
   regions from the MESH: dihedral region-grow over face adjacency (smooth skin vs
   rough fracture), per piece, all nine Juglet pieces + the Pot A control where the
   same labels must come out sane on fresh breaks. On the labelled regions measure
   per-point distributions of the four candidate signals:
   a. **roughness** — local plane-fit deviation, ball radii 1.0/1.5/2.0/3.0 mm;
   b. **thickness pairing** — ray-cast slab along the normal within +/-1.5 wall
      thicknesses (the U17 Layer 2 method);
   c. **accumulated turn** — total turn over windows of 2/5/10 mm AND windows tied to
      the piece's own fold radius, roll regions vs legitimate wall regions (this is the
      conservator's long-distance angle test);
   d. **mesh label vs t55 claims** — how far each surface's claimed-region boundary
      sits from the fracture-label boundary; what share of each claim lies on
      fracture-labelled triangles (today's far-skin crossing, in mesh terms).
   Deliverable: a decision table — signal x distribution pair x overlap x margin, per
   piece and pooled. **Gate:** proceed to Stage 1 only if at least one signal separates
   fracture+roll from legitimate wall with a stated margin AND the Pot A control stays
   clean; otherwise record the negative and stop there.
2. **Stage 1 — implement the best-margin signal as an OPT-IN growth stop** (env-gated,
   e.g. SFS_BREAK_STOP=1), default path byte-identical: with the env unset the outputs
   must md5-match the t55 baseline (the t57 control pattern). Rebuild the mesh-stage
   binary in the run area; record binary md5 + diff. Note the interaction with the
   theta-ladder retry (:3707-3745) in the Results.
3. **Run all nine Juglet pieces at SFS_WORNESS=0.7 with the stop on.** Judge with
   check_separation.py against metrics/baseline_t55.tsv: far-skin share (primary),
   blind extent, double-cover, seam share, Bl0 dot counts, 9/9 genuine pairs held.
4. **Render for the eye check:** before/after boundary on J1's blind stretch, plus all
   nine pieces' surface boundary vs the fracture-label boundary; workspace-relative
   links under SfSpp_preprocessing/artifacts/.
5. **Append ## Results:** the Stage 0 decision table, the Stage 1 diff + md5, the gate
   comparison table, the renders. Worker measures; the conservator and lead judge.

### Acceptance

- Stage 0 decision table exists BEFORE any code change; a clean negative is a
  pass condition for Stage 0 and a stop.
- Stage 1 change is opt-in and default-off; the unset path proven byte-identical to
  t55 (md5 evidence in the ticket).
- Every sbatch polled and final sacct State/ExitCode recorded in the ticket.
- Budget: <=4 Slurm jobs, <=24 h wall.
- check_separation.py run on the baseline and the new arm; thresholds passed as flags,
  none invented.
- Nothing written into the t55 or t57 run dirs; meshes and Dataset read-only.
- Renders carry workspace-relative links; the conservator gets the eye check.
- Worker reports measurements only, in English; no recommendations.

**Edges:** uses the t55 run dir and the t57 gate READ-ONLY; Spartan budget separate
from tickets 57/58 (both closed). The 50-dot floor (ticket 58) is downstream context,
not a dependency: if the stop recovers the blind stretch, Bl0 dot counts are expected
to change — record them, do not chase them.

## Results (worker, 2026-11-02)

All measurements; no verdicts. Run dirs live under
`/data/gpfs/projects/punim2657/SfSpp/runs/`. Every sbatch was polled and its final
sacct State/ExitCode is in the job table below.

### Jobs (4 sbatch submissions, within the <=4 budget)

| run dir | jobid | State / ExitCode | Elapsed |
|---|---|---|---|
| 20261102-1144_638504b_t59-breakstop-stage0 | 34194028 | COMPLETED 0:0 | 19:31 |
| 20261102-1155_638504b_t59-control-gateclosed | 34194631 | COMPLETED 0:0 | 05:38 |
| 20261102-1408_638504b_t59-pota-relabel | 34199355 | OUT_OF_MEMORY 0:125 | 02:36 |
| 20261102-1416_638504b_t59-breakstop-arm | 34199881 | COMPLETED 0:0 | 07:55 |

The third job OOM-killed itself by materialising ~200k x 6.5k-point ball-neighbour
lists at once on the full-res Pot A mesh; its chunked retry was folded into the fourth
job to stay inside the 4-job budget.

### Stage 0 — labels from mesh structure + the four signals

Labels come ONLY from each mesh's own structure (dihedral region-grow over face
adjacency; smooth = union-find components with dihedral < 10 deg and area >= 3% of the
mesh, sensitivity 8/15 deg and 2/5%; rough = the rest), then each smooth face is
classified wall/roll by slab pairing and each rough face fracture/anomaly. Full method,
parameters and per-piece distributions: run dir above, `work/stage0_probe.py`,
`out/stage0_summary.json`, `out/decision_table.tsv`, `out/pota_control.tsv`.

**Decision table (pooled over 9 Juglet pieces; OVL = 40-bin histogram overlap,
margin = |medA-medB| / (0.5(IQRa+IQRb))); best rows:**

| signal (pair) | OVL | best-threshold | err at thr | margin | medians |
|---|---|---|---|---|---|
| (a) dev r=1.5mm wall vs roll+fracture | 0.3775 | 0.1467 | 0.1766 | 1.707 | 0.0522 vs 0.1959 |
| (a) dev r=1.5mm wall vs fracture | 0.2473 | — | — | 2.342 | — |
| (c) turn med @5mm wall vs fracture | 0.4059 | 48.2 deg | 0.2827 | 0.919 | 37.98 vs 72.85 deg |
| (b) ray hit distance wall vs fracture | 0.48-0.57 | — | — | ~0-0.37 | 2.166 vs 2.160 mm |

Per-signal findings:

- **(a) roughness does not transfer across resolution classes.** The pooled margin is
  62% J1-weighted (J1 is the only full-res Juglet mesh). At the pooled threshold
  0.1467 the wall misfire rate on the decimated pieces is 0.19-0.59 (J2 0.587,
  J3 0.459, J9 0.583; J1 0.104).
- **(c) accumulated turn separates 5 of 9 pieces** at the 5 mm window (wall vs fracture
  medians, deg: J1 20.8/76.8, J5 26.4/68.4, J6 39.8/74.5, J7 24.0/69.9, J8 37.7/79.2;
  fails J2 83.4/79.1, J3 72.1/70.7, J9 66.6/74.5).
- **(b) thickness pairing is the only all-9 separator** — as a RATE, not a distance:
  wall b_paired_rate 0.8915-0.9750 per piece vs fracture 0.056-0.164 and roll
  0.011-0.255; interior (anomaly) faces pair at 0.63-0.83, i.e. the interior keeps
  growing through the stop test. Measured wall thickness per piece (t_piece, mm):
  J1 1.876, J2 2.178, J3 1.948, J4 2.213, J5 2.527, J6 2.373, J7 2.839, J8 1.877,
  J9 2.151. The hit-distance value itself does not separate (medians 2.166 vs 2.160).
- **(d) t55 S0 claims sit mostly on wall-labelled faces** (share per piece: J1 0.851,
  J2 0.643, J3 0.655, J4 0.741, J5 0.810, J6 0.900, J7 0.811, J8 0.798, J9 0.816);
  on J9 the claim boundary hugs the band boundary (median 0.233 mm, p90 0.77 mm).

**Stage-0 gate facts (measured, decision is the lead's):** signal (b) separates
fracture+roll from legitimate wall on all 9 Juglet pieces with the margins above.
Pot A: the label machinery itself degenerates at the primary parameters — dihedral
noise on the 0.286 mm full-res meshes shatters the region-grow (Pot_A_Piece_01:
top-5 components 0.01% each; wall/roll/fracture shares 0/0/0.99), so
`pota_control.tsv` is empty (header only) and no Pot A threshold-misfire rate on
labelled walls exists. Label-free upper bounds: at the pooled (a) threshold 0.1467 the
misfire rate over ALL Pot A faces is 0.25-0.73 per piece. Pot A b_paired_rate is
0.002-0.017, consistent with a search-range artifact (ray capped at 1.5*t + 0.5 mm
computed from Juglet-scale walls; the pot's walls are thicker) — a parameter sweep
relabel (dihedral 10-30 deg, along 4/8/12 mm) was written to answer this; its first
submission OOM-killed and the chunked retry ran inside the fourth job (see below).

### Control run (unpatched rebuild of 638504b, gate absent from code)

`20261102-1155_638504b_t59-control-gateclosed`, two full passes A/B over all 9 pieces:

- Binaries rebuilt byte-identical to t55's (mesh 736ff95c..., edge cbf477dc...).
- A_eq_B: 18/36 — every S0/S1 equal (mesh stage deterministic within one session);
  every Bl0/Bl1 unequal (edge stage nondeterministic run-to-run; differences are
  numeric, not ordering — sorted-md5 also differs, tested J1/J9).
- A_eq_t55: 16/36 — S0/S1 equal on 8/9 pieces; Juglet_Piece_8 differs because its
  normal-flip decision flipped (t55 true vs control false; checkNormalsIntersection
  draws 30 points from an unseeded random_device — ticket-33-era fact, re-measured
  here as a pre-existing lottery, not caused by this ticket's work).
- Frozen inputs (point clouds, meshes, axes) unchanged: md5 before == after.

So "byte-identical with the gate unset" can only be measured up to this pre-existing
flip lottery on S0/S1 (and up to edge-stage nondeterminism on Bl0/Bl1). The Stage-1
identity gate below is defined accordingly: S0/S1 must be equal on every piece whose
flip draw matches the control's; a mismatch on a piece with a different flip draw is
recorded as FLIP-LOTTERY, and any mismatch with the same flip draw fails the gate.

### Stage 1 — opt-in growth stop (patched build, not committed)

Patch: +111 lines, 0 deletions vs the commit-638504b source
(`stage1/mesh_processing_headless.patched.cpp` in the worktree; run dir copies +
`work/patch.diff`). Design: env SFS_BREAK_STOP=1 arms a per-point break-surface test;
optional SFS_BREAK_STOP_{MIN,MAX,EPS}_MM and _EXIT_DOT (defaults 0.9 / 7.2 / 0.45 /
-0.4). At each surfaceSegmentation rung the cloud+normals are rebuilt; when armed,
computeBreakStopFlags59 marches BOTH +normal and -normal from each point (step
max(0.10, 0.75*eps) mm), nearest-neighbour-probes, and marks a point wall-like (0)
iff it finds an oppositely-oriented surface within eps in [min,max] mm
(dot of the found normal with the ORIGIN point's normal <= -0.4 — origin-relative,
so invariant to the global normal flip, and rejecting same-side grazing hits). In
growPaper234 a break-like candidate is rejected (after the existing curvature check,
before the angle check). Seeds are not filtered; the plane and PCL-RegionGrowing paths
are untouched. With the env unset the flag is false, computeBreakStopFlags59 never
runs, and the candidate check short-circuits on a false global — the default path
executes the same instructions as before (verified by the identity gate below).
Window [0.9, 7.2] mm covers [0.5, 2.5] x t_piece for all nine pieces (envelope
0.938-7.098 mm).

Theta-ladder interaction (:3707-3745): the compute call sits inside the per-iteration
grow loop, so if the ladder retries at another theta the flags are recomputed for that
rung's rebuilt cloud. Measured here: every piece, in both arms, ran exactly ONE grow
iteration at SFS_WORNESS=0.7 (one "paper grow" line per mesh.log; e.g. J1 grew at
thetaDeg=6.42511, the worness-capped value) — the ladder never retried, so each piece
computed the flags once. Cost when armed: one extra both-direction neighbour march per
point per rung (~19 steps x 2 sides), logged as
`[BREAK-59] piece= npts= wall_like= break_like= window_mm=` per piece per rung.

### Job 34199881 (arm run): identity gate, armed pass, metrics, renders

COMPLETED 0:0, 7:55 elapsed, run dir `20261102-1416_638504b_t59-breakstop-arm`.
Build: the ONLY source change vs commit 638504b is the uploaded patched cpp
(`work/patch.diff`, +111/-0). Patched MeshPreprocessingHeadless md5 05d8d624...,
1621216 bytes (differs from the unpatched 736ff95c..., as expected for changed code);
EdgeLineExtractionHeadless rebuilt identical cbf477dc... (untouched path).

**Identity gate (gate closed, patched binary, SFS_BREAK_STOP* unset) — PASS.**
Flip draws this session equal the control's on all nine pieces (true on J1 and J6,
false on the rest); all 18 S0/S1 md5 EQUAL the control's passA (hard mismatches 0).
All 18 Bl0/Bl1 differ — the pre-existing edge-stage nondeterminism measured in the
control run (A_eq_B was 0/18 there too); not gated. Full table:
`identity_gate.tsv` in the run dir. (Anomaly, recorded: the gate script's first
in-job output had empty flip columns — re.match against lines that start with the
log path; regenerated with re.search, verdicts unchanged, first copy kept as
`identity_gate.tsv.v1-matchbug`.)

**Armed pass (SFS_BREAK_STOP=1, code defaults 0.9/7.2/0.45/-0.4).** All 9 pieces
mesh_rc=0 with both stage markers + full geom bundle. `[BREAK-59]` armed + per-piece
markers present in every mesh.log (e.g. J1: npts=19312 wall_like=1674 break_like=17638
— 8.7% wall-like; J2-J9 are 83-91% wall-like: J2 1647/236, J3 2475/366, J4 2407/361,
J5 5121/550, J6 3921/452, J7 6926/707, J8 3136/328, J9 1231/244). Anomaly, recorded:
the in-job marker grep wrote an empty `passG.breakstop.txt`; re-grepping the same
logs after the job yields 18 lines (9 armed + 9 per-piece); the file was regenerated
post-job from those logs.

**check_separation.py (exact t57 invocation, no threshold flags passed — defaults
only, none invented; genuine-pairs column included), gate-closed arm U vs armed arm
G vs baseline_t55.tsv:**

| piece | farS0 t55 / U / G | blindDeg U / G | dc_ge1 U / G | bl0 U / G | genuine U / G |
|---|---|---|---|---|---|
| J1 | 0.8624 / 0.8624 / **0.1429** | 85.49 / **22.6** | 0.1205 / **0.0017** | 28 / **15** | True / **False** |
| J2 | 0.8182 / 0.8182 / 0.8182 | 18.14 / 18.14 | 0.0129 / 0.0129 | 32 / 32 | True / True |
| J3 | 0.7714 / 0.7714 / 0.8000 | 22.06 / 20.17 | 0.0027 / 0.0027 | 38 / 38 | True / True |
| J4 | 0.7059 / 0.7059 / 0.7576 | 11.03 / 10.70 | 0.0245 / 0.0019 | 32 / 32 | True / True |
| J5 | 0.7544 / 0.7544 / 0.7321 | 7.70 / 12.35 | 0.0163 / 0.0074 | 47 / 46 | True / True |
| J6 | 0.8824 / 0.8824 / 0.8200 | 11.94 / 12.04 | 0.1388 / 0.0633 | 46 / 46 | True / True |
| J7 | 0.8039 / 0.8039 / 0.8776 | 5.92 / 7.19 | 0.0502 / 0.0238 | 54 / 53 | True / True |
| J8 | 0.6512 / 0.6512 / 0.7500 | 11.93 / 11.74 | 0.0556 / 0.0246 | 41 / 40 | True / True |
| J9 | 0.7000 / 0.7000 / 0.7000 | 12.32 / 12.32 | 0.0777 / 0.0363 | 23 / 23 | True / True |

Supporting counts: U reproduces the t55 baseline exactly on farS0 for all nine pieces
and on nS0 within +/-1 point (U is the patched-binary, gate-closed rebuild). Armed J1:
nS0 13850 -> 351, nS1 15173 -> 1481, farS1 0.4654 -> 0.1714, seamArcDeg 11.65 -> 56.44,
seamIn 0.826 -> 0.895, pct_wall 83.5 -> 186.8 (pct_wall > 100 with genuine=False).
J2/J9 barely move (J2 nS0 1390 -> 1377; J9 1051 -> 1050); J3-J8 change by -1 to -9%
in nS0. Full tables: `metrics_U.tsv`, `metrics_G.tsv`, `metrics_U.json`,
`metrics_G.json` in the run dir; baseline reference `baseline_t55.tsv` (t57 run,
read-only).

**Renders (Task 4)** — PNGs in the run dir `out/png/` and copied to the workspace:

- J1 before/after + blind-stretch zoom: [before/after](SfSpp_preprocessing/artifacts/59/Juglet_Piece_1_before_after.png),
  [zoom before](SfSpp_preprocessing/artifacts/59/Juglet_Piece_1_zoom_before.png),
  [zoom after](SfSpp_preprocessing/artifacts/59/Juglet_Piece_1_zoom_after.png)
- Per piece: [J2](SfSpp_preprocessing/artifacts/59/Juglet_Piece_2_before_after.png),
  [J3](SfSpp_preprocessing/artifacts/59/Juglet_Piece_3_before_after.png),
  [J4](SfSpp_preprocessing/artifacts/59/Juglet_Piece_4_before_after.png),
  [J5](SfSpp_preprocessing/artifacts/59/Juglet_Piece_5_before_after.png),
  [J6](SfSpp_preprocessing/artifacts/59/Juglet_Piece_6_before_after.png),
  [J7](SfSpp_preprocessing/artifacts/59/Juglet_Piece_7_before_after.png),
  [J8](SfSpp_preprocessing/artifacts/59/Juglet_Piece_8_before_after.png),
  [J9](SfSpp_preprocessing/artifacts/59/Juglet_Piece_9_before_after.png)

Each panel: gray = mesh, orange = stage-0 fracture-labelled faces, blue = S0 claim
points, red = Bl0 dots; left column gate-closed (patched binary), right column armed.
Worker-side render sanity check only (the conservator's eye check is the real one): in
the J1 zoom-before, blue claim points reach the margin of the orange fracture band; in
zoom-after they stop short of it, red dots on the gray/orange boundary in both.

**Pot A relabel retry: NOT executed.** `pota_relabel.py` requires --stage0-dir and
--out-dir; the job-4 invocation passed neither (usage printed, rc=2, ~1 s; log
`logs/pota_relabel.log`). The 4-job budget was already consumed (the OOM'd
34199355 counted), so no fifth submission was made. The chunked script is staged and
CLI-correct in the run dir `work/pota_relabel.py` and in the worktree; the Stage-0
Pot A facts above stand as the measured record.

### Deviations and anomalies (all measured, none hidden)

1. Budget: 4 sbatch submissions used (stage0, control, pota-relabel OOM, arm). The
   Pot A OOM (all-at-once ball lists on the 600k-vertex mesh) consumed the third slot;
   its retry was folded into job 4 and then missed on CLI args (see above) — the only
   ticket item not carried to a measurement.
2. The Stage-1 patch is NOT committed: worker does not commit. Provenance = the
   uploaded patched cpp (md5 42ad5e35c0d7890b3bb01e5d16f5a7a8) + `work/patch.diff`
   + `binaries.md5` in the arm run dir, and
   `.scratch/juglet-breaklines/stage59/stage1/mesh_processing_headless.patched.cpp`
   in the worktree (uncommitted).
3. Byte-identity could only be measured up to the pre-existing flip lottery (S0/S1)
   and edge-stage nondeterminism (Bl0/Bl1), both quantified in the control run before
   any patch was built.
4. In-job anomalies: empty passG.breakstop.txt grep (regenerated post-job, 18 lines);
   first identity_gate.tsv had empty flip columns (regex match-point bug; regenerated,
   verdicts unchanged, both copies kept).
5. J1 armed pct_wall 186.8 with genuine=False is recorded as-is; no interpretation
   offered (worker measures).

### Lead verification (2026-11-02, lead)

Re-checked independently before write-back. The ticket's own gate is **not passed**: Stage 0
required a separating signal *and* a clean Pot A control before Stage 1. Pot A is degenerate at
the primary parameters (full-resolution dihedral noise 0.286 mm; P01 top components 0.01%), so
`pota_control.tsv` is empty, and the relabel retry (job 34199355) died OUT_OF_MEMORY at 2:36
and the four-job budget was then spent. Stage 1-2 were run anyway (job 34199881) and are
recorded below as a **probe, not a gate pass**.

Verified:

- `sacct` -> 34194028 stage0 COMPLETED 0:0 19:31; 34194631 control COMPLETED 0:0 5:38;
  34199355 pota-relabel OUT_OF_MEMORY 0:125 2:36; 34199881 arm COMPLETED 0:0 7:55.
- `out/gate.json` -> `pass: true, hard_mismatches: 0`; `identity_gate.tsv` S0/S1 EQ with the
  flip draw matching per piece (J1/J6 True, others False); Bl0/Bl1 flagged
  "bl-nondeterministic (pre-existing, not gated)". Own md5 check: every `passU/*.S0` is
  byte-identical to its `passA/*.S0` (9/9).
- `metrics_U.tsv` J1 row == the t55 row exactly (nS0 13850, foldS0 2824, blindDeg 85.49,
  farS0 0.8624, dc_ge1 0.1205, bl0 28, genuine True) — the gate-closed rebuild reproduces the
  run of record.
- Re-ran the separation check myself (`check_separation.py --geom outG/geom --mesh-dir
  Dataset/Mesh/Juglet --walls t54/w070/walls`, rc=0): J1 351 pts / 22.60 deg / farS0 0.1714,
  J2 1377 / 18.14 / 0.7576, J9 1050 / 12.32 / 0.7857 — matches `metrics_G.tsv`.
- Binaries at the stated md5s: patched mesh 05d8d624f3c2bc588b1f8f8e2d209277 (1621216 B),
  control 736ff95c976486d17f7c00b3af402040, edge stage unchanged
  cbf747dc3172fe0bbd188822df14092a. Patch is +111/-0 on base 638504bf, uncommitted (as
  recorded).
- Renders: the three J1 files exist and are on the right subject (legend: gray mesh, orange
  stage-0 fracture label, blue S0 claim, red Bl0). My vision-bridge read of them is coarse and
  does **not** independently settle "before reaches the band / after stops short"; that fine
  comparison stays with the conservator's eye.

**The load-bearing contradiction.** In-growth on J1 logs `npts=19312 wall_like=1674
break_like=17638` (8.7% wall-like), while the mesh labels call 62.5% of J1's faces wall
(shares W/R/F/A 0.6255/0.0562/0.1164/0.2018, identical at all three minfracs) and the offline
cloud measurement paired 89-98% of its wall points. J2, by contrast, agrees with its mesh:
1883 candidates, 1647 wall-like (87.5%). Both pieces contribute ~1.65k wall-like points, so the
test is not inverting — J1's candidate bag is ~10x larger and overwhelmingly break-like, and
stopping it starves the growth (S0 13850 -> 351, S1 15173 -> 1481). Cause is not established
here. Candidate explanations: J1's cloud normal field; bag composition under the curvature
filter; the J1 flip interaction. Deciding between them is a separate probe (normal-agreement
check + per-piece bag composition), not this ticket.

**Verdict on the question this ticket was opened to answer.** Wall pairing separates the wall
from the break/roll surface offline on all nine pieces — the signal is real. As implemented in
the growth loop it is not a usable stop rule yet: on the one piece with the blind stretch it
removes the surface and drops the genuine-pair guard to 8/9; on the other eight it is
near-no-op (nS0 -1 to -9%). Nothing is merged; the patch stays run-dir provenance. The
conservator decides whether to park the signal or open the diagnosing probe.

