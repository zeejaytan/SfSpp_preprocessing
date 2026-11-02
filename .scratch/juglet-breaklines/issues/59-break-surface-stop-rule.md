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

**Status:** in-progress
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
