# 57 — Worness dial at fine steps: which value buys clean surface separation

**What to build:** a swept measurement of `SFS_WORNESS` over 0.30–0.90 in 0.05 steps
(plus the unset default), refined at 0.01 steps around any transition, scoring every arm
for **surface separation quality** — is either surface's region sitting on the wrong face
of the wall — together with the existing genuine-pair guard. Plus one reusable read-only
audit script so separation becomes a checkable gate, not a one-off probe.

**Why now (2026-11-02, conservator's decision):** the J1 blind-stretch diagnosis showed
that at 0.7 the split itself crosses the break — Surface_0's points sit on the far face of
the wall (one wall thickness through the pottery) for the whole 91.4° dead stretch. The
conservator accepted the diagnosis, asked that the dial be tested for clean separation,
and asked for fine steps ("0.05 or smaller") because the bend the growth wrongly follows
is only ~4°, so the useful transition may sit between coarse dial values.

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines
let SfS find joins)

**Blocked by:** none (56 resolved; 55's run of record is the baseline arm)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 57-worness-fine-sweep-surface-separation, in /c/PR/worktrees/sfs/57
**Worker:** unassigned

**Conservator decisions feeding this ticket:**
- 2026-11-01: SFS_WORNESS=0.7 is the recommended documented value (ticket 54, ledger row 12).
- 2026-11-02: run the sweep; fine steps 0.05 or smaller near the transition; the dial must
  be judged on whether the two surfaces separate cleanly, not only on pair counts.

## Spec

### Given (measured facts this stands on)

Baseline arm = t55 run of record `20261101-2004_05be12c_t55-worness07-breaklines`
(Spartan `/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines`,
step 3 + step 4, all nine pieces, SFS_WORNESS=0.7). On J1 in that run:

- S0 13850 / S1 15173 points, each exactly on mesh triangles (point-to-triangle 0.000 mm);
  mesh `/data/gpfs/projects/punim2657/Dataset/Mesh/Juglet/Juglet_Piece_1_Mesh.obj`
  (24294 verts / 48592 faces, watertight closed solid).
- Fold (S0 coverage boundary, vertex-coverage tolerance 0.6 mm): 2824 edges; union rim
  (S0∪S1 boundary): 2527 edges.
- Blind arc 717 fold points = 91.4° of the ring; seam share inside 87% vs outside 54%.
- In the blind arc, 47 of 48 sampled fold points have their S0 3 mm-ball median offset
  −1.66…−1.84 mm along the local mesh normal = one wall thickness (wall 1.76 mm there):
  S0's region is on the far face. 85% of S0 points within 5 mm of the blind fold are on
  the far side.
- At the working-arc lip, S0 and S1 share points: 37/37 of S1's near-rim points coincide
  with S0 points at distance 0.00 mm. Global double-cover ≈ 12% of triangles.
- The frontier in the blind arc runs 5.0 mm inside the true broken edge (working arc:
  0.0 mm). Dots fire nowhere in the blind arc (detector sees material on all sides).
- 0.7 was adopted because it gives 9/9 genuine wall pairs (J8's pair at 0.9 is
  spacing-bound junk). Any arm that loses that is reported, not silently averaged.
- Dial semantics (ticket 54, merged 77f50ad): precedence SFS_PAPER_THETA > SFS_WORNESS >
  SFS_GROWTH_FORMULA/CAP; 0 < w ≤ 1 → theta = min(paper formula, w × measured crossing);
  unset = paper no-op; bad value = FATAL rc 2. Binary md5 736ff95c976486d17f7c00b3af402040.

### Task

1. **Validate the metric scripts on the baseline arm first.** Re-implement the separation
   metrics as standalone scripts in the run area (not in src); run them on the t55 0.7
   outputs and reproduce the Given numbers for J1 (47/48 far-skin fold points, 85% far
   share, 37/37 coincident lip points, 12% double-cover, 2824/2527 edge counts) before
   sweeping. Metric definitions:
   - *far-skin share (per surface):* fold-edge midpoints of that surface's coverage; for
     every k-th midpoint take the area-weighted mesh vertex normal of the nearest mesh
     vertex; median signed offset of the surface's points within 3 mm along that normal;
     a fold point counts far when the median < −0.8 mm; report the share and the offsets.
   - *double-cover share:* points of S0 with an S1 point within 0.6 mm / |S0|, and
     triangle-level share (faces whose 3 vertices are all claimed by both).
   - *seam share:* fold points where mesh vertices 0.4–3.0 mm outward (in-plane, away from
     the surface's local centroid) are ≥50% covered by the other surface.
   - *blind-stretch extent:* longest ring arc (smoothed seam indicator, window 10) above
     0.6, in degrees, plus dots-fired angular coverage from `edge.log` `[VOTE-247]` lines.
   - *dots:* per-piece `Breakline_0` dot count; flag pieces below 50 (the assembler's
     `main.cpp` near line 86 floor).
   - *genuine pairs:* the t54 pairing logic (t54 run `20261101-1613_83edd76` harness); 9/9
     genuine wall pairs is the guard, per arm.
2. **Stage A sweep.** Arms: SFS_WORNESS ∈ {0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60,
   0.65, 0.75, 0.80, 0.85, 0.90} plus the default (unset) arm — 0.70 is already measured
   (baseline). Per arm: step 3 (mesh→surfaces) then step 4 (surfaces→breaklines) for all
   nine pieces, t55 harness commands and directory layout, one run directory per arm
   (`runs/<ts>_<git7>_t57-w<value>`). Time one arm first; batch the rest ≤4-way parallel
   inside one job; hard budget ≤ 4 Slurm jobs and ≤ 24 h wall total. Every sbatch gets
   `scripts/slurm_poll.sh` and its final sacct State/ExitCode recorded below.
3. **Stage B refinement.** Only if Stage A shows a transition (far-skin share drops
   materially between neighbouring values): sweep ±0.10 around the transition at 0.01
   steps (≤ 10 arms) to locate the flip; same metrics.
4. **Deliver `check_separation.py`** (read-only): takes a run's geom dir (+ mesh dir),
   prints per piece far-skin shares, double-cover, seam share, blind extent, dot counts;
   optional thresholds as flags exiting nonzero when exceeded. Thresholds themselves are
   NOT invented in this ticket — this ticket produces the table the thresholds will be
   read from.
5. **Write the table and the verdict per arm** into this ticket (append `## Results`):
   arm × piece × {far-skin S0, far-skin S1, double-cover, seam, blind°, Bl0 count, pairs},
   and a one-line verdict naming which value (if any) removes the far-skin crossing while
   holding 9/9 pairs and dot counts.

### Acceptance

- Baseline reproduction line present (script vs Given numbers, J1).
- Every arm row carries job id + sacct State/ExitCode.
- The 9/9 pairs guard reported per arm; losses named per piece.
- `check_separation.py` runs clean on the t55 dir and on at least one sweep arm.
- No source changes to the pipeline; scripts and tables live in run dirs / ticket only.
- Lead verification: the lead re-runs `check_separation.py` on the baseline arm and one
  sweep arm and recomputes one piece's far-skin share independently.

### Edges

- Depends on t55 run of record staying intact (nothing under it deleted).
- Spartan checkout: `git pull --ff-only` only; on divergence stop and report.
- Do not rebuild the binary; md5 must stay 736ff95c976486d17f7c00b3af402040.
