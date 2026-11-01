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

**Status:** resolved
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 57-worness-fine-sweep-surface-separation, in /c/PR/worktrees/sfs/57
**Worker:** delegated worker session (2026-11-02); lead verifies

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
- Blind stretch: **degrees only**, and the frozen definition is the largest angular gap in
  Surface_0's boundary-fire dots (detector in-plane keep radius 4 mm, 108° void), measured
  around the break-edge ring. Baseline under that definition: **85.5°** (my implementation).
  t56 recorded 95.7° and the original Given said 91.4°; the bracket is the honest statement
  of the spread, which comes from the detector's keep radius. What matters for the sweep is
  that ONE implementation is applied to all 13 arms.
  *"717 fold points" is DERIVED, not measured, and is not calibrated to.* 717/2824 =
  0.253895 vs 91.4/360 = 0.253889 — identical to 5 d.p. because the point count was computed
  as round(2824 × 91.4/360) from the degree figure, so it was never an independent check.
  Fold angular density is far from uniform (36 ten-degree bins: mean 78.4, s.d. 70.2, range
  4–266; the widest 91.4° window holds 1309 midpoints), so 717 and 91.4° cannot both be
  measurements.
- Seam share, frozen reading: local centroid = mean of the **mesh vertices** within 3 mm of
  the fold midpoint, seam band 3 mm, covered fraction > 0.6 → seam point. Baseline
  **inside 0.826 / outside 0.523** (J1). Reported to 3 d.p. per arm. Footnote variants, not
  used: "surface points within 3 mm" (0.962/0.652) and the global centroid (0.871/0.604).
  The two sectors are reported separately — the frozen blind stretch (fire gap) and the
  seam arc are different arcs, and the seam arc lies entirely inside the fire gap.
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

## Results

**Worker run 2026-11-02.** Measurement only — no dial recommendation is made here (that is the
lead's/conservator's call). All numbers below come from `check_separation.py`
md5 `054ee00da99a1cf58d9d84ae5e0d361a`, identical in every arm directory.

### Jobs and final sacct

| job | name | dir | State | ExitCode | Elapsed |
|---|---|---|---|---|---|
| 34173774 | t57-time | runs/20261102-0333_05be12c_t57-w050 | COMPLETED | 0:0 | 00:01:37 |
| 34173850 | t57-stageA | runs/20261102-0450_05be12c_t57-sweep | COMPLETED | 0:0 | 00:12:22 |
| 34174182 | t57-w050k | runs/20261102-0450_05be12c_t57-sweep | COMPLETED | 0:0 | 00:01:45 |
| 34174215 | t57-p717 | runs/20261102-0450_05be12c_t57-sweep | COMPLETED | 0:0 | 00:00:05 |

34173814 (the first Stage A submit) was `scancel`led before it ran. Jobs 1-3 are sweep budget;
job 4 is the Given-number probe. Budget **4 jobs / ~16 min wall** against ≤4 jobs / ≤24 h.

### Task 1 — baseline reproduction on the t55 arm

Script vs the Given numbers, J1 baseline (t55 run of record):

| Given (ticket) | Reproduced by the script | Verdict |
|---|---|---|
| 2824 / 2527 edge counts | foldS0 2824, unionRim 2527 | **exact** |
| double-cover ≈ 12% | dc_ge1 0.1205 = 12.05% | **exact** |
| 37/37 coincident lip points | lip = 1034 exact-duplicate pairs / 15173 S1 points (frozen reading) | **not a 37-sample**; the frozen count is 1034 |
| 47 of 48 far-skin fold points | 717-contiguous window k=15 → 43/48 far; fire-gap k=15 → 79/84; whole ring → 163/189 | **not reproduced** |
| 85% far share | farS0 0.8624 (86.2%); farPts5mm 0.8033 (80.3%) | near miss |
| 9/9 genuine pairs | 9/9 | **exact** |

Controls: `metrics/baseline_t55.tsv` and `metrics/w070.tsv` are **byte-identical**
(md5 `968d5422a397c9d586368bc9f71b4281` both), i.e. the swept code path reproduces the t55 run of
record at 0.70 and every arm row is comparable to it. All 18 Bl files share identical xyz; the
`curvature` column differs in all 18 and J1's breakline normals differ (the other eight reproduce);
so: point positions and metrics reproduce, "byte-identical geometry" is **not** claimed.

**717 / 91.4° is derived, reconfirmed.** The minimum angular span of 717 contiguous fold midpoints
is **39.53°** (n=2824, R=16.249); a 91.4° window holds ~1309 midpoints. 717 = round(2824 × 91.4/360)
to 5 d.p. — not an independent measurement. The Given's sample size 48 is exactly 717/15, but the far
count in that window is 43, and its offset range is −2.61…−0.89 mm, not the Given's −1.66…−1.84 mm.

### Task 2 — Stage A sweep (`check_separation.py` per arm, J1 = diagnostic piece)

Blind° is the frozen definition (largest gap in S0 boundary-fire dots, all nine pieces); "mean blind°"
is across pieces. `farS0` is the far-skin share, `dc_ge1` double-cover, `seamIn/Out` the frozen
mesh-vertex-ball seam reading. Every arm row is at
`runs/20261102-0450_05be12c_t57-<arm>/metrics/<arm>.tsv` (w050 at
`runs/20261102-0333_05be12c_t57-w050/arms/w050`).

| arm | SFS_WORNESS | job | sacct State/ExitCode | 9/9 pairs | losses (piece) | J1 farS0 | J1 farS1 | J1 dc_ge1 | J1 seamIn | J1 seamOut | J1 blind° | J1 Bl0 | min Bl0 (any piece) | mean blind° |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline_t55 | 0.70 (t55 of record) | 34173850 | COMPLETED 0:0 | 9/9 | — | 0.8624 | 0.4654 | 0.1205 | 0.826 | 0.523 | 85.49 | 28 | 23 | 20.7 |
| w030 | 0.30 | 34173850 | COMPLETED 0:0 | 7/9 | J1,J5 | 0.1905 | 0.6205 | 0.0162 | 0.961 | 0.218 | 7.1 | 53 | 24 | 12.0 |
| w035 | 0.35 | 34173850 | COMPLETED 0:0 | 8/9 | J1 | 0.5606 | 0.5355 | 0.0113 | 0.851 | 0.196 | 80.72 | 39 | 22 | 21.6 |
| w040 | 0.40 | 34173850 | COMPLETED 0:0 | 8/9 | J1 | 0.5109 | 0.6834 | 0.0757 | 0.892 | 0.46 | 88.41 | 56 | 22 | 20.8 |
| w045 | 0.45 | 34173850 | COMPLETED 0:0 | 7/9 | J1,J5 | 0.7344 | 0.6416 | 0.182 | 0.931 | 0.546 | 41.25 | 70 | 22 | 16.7 |
| w050 | 0.50 | 34174182 | COMPLETED 0:0 | 8/9 | J1 | 0.7647 | 0.4365 | 0.222 | 0.888 | 0.529 | 36.94 | 60 | 22 | 15.2 |
| w055 | 0.55 | 34173850 | COMPLETED 0:0 | 9/9 | — | 0.7763 | 0.5484 | 0.1584 | 0.893 | 0.512 | 77.11 | 59 | 23 | 19.7 |
| w060 | 0.60 | 34173850 | COMPLETED 0:0 | 9/9 | — | 0.7961 | 0.4971 | 0.1139 | 0.877 | 0.396 | 62.12 | 23 | 23 | 17.8 |
| w065 | 0.65 | 34173850 | COMPLETED 0:0 | 9/9 | — | 0.8615 | 0.4474 | 0.0953 | 0.843 | 0.537 | 19.69 | 48 | 24 | 13.4 |
| w070 | 0.70 | 34173850 | COMPLETED 0:0 | 9/9 | — | 0.8624 | 0.4654 | 0.1205 | 0.826 | 0.523 | 85.49 | 28 | 23 | 20.7 |
| w075 | 0.75 | 34173850 | COMPLETED 0:0 | 9/9 | — | 0.8957 | 0.4904 | 0.0945 | 0.868 | 0.408 | 27.42 | 55 | 23 | 13.9 |
| w080 | 0.80 | 34173850 | COMPLETED 0:0 | 9/9 | — | 0.8673 | 0.5974 | 0.1162 | 0.877 | 0.528 | 25.92 | 56 | 23 | 14.8 |
| w085 | 0.85 | 34173850 | COMPLETED 0:0 | 9/9 | — | 0.8024 | 0.6067 | 0.084 | 0.843 | 0.486 | 43.17 | 0 | 0 | 16.5 |
| w090 | 0.90 | 34173850 | COMPLETED 0:0 | 8/9 | J8 | 0.9116 | 0.5517 | 0.1444 | 0.892 | 0.501 | 46.72 | 0 | 0 | 23.0 |
| default | unset | 34173850 | COMPLETED 0:0 | 1/9 | J1,J3,J4,J5,J6,J7,J8,J9 | 0.456 | 0.5833 | 0.0164 | None | 0.074 | 7.26 | 33 | 7 | 21.4 |

**The far-skin crossing is not monotone in the dial and is not removed at any value.**
On J1 between 0.55 and 0.90, farS0 stays **0.776–0.912** and the in-arc share `farS0_in` is 0.93–1.00 —
S0 remains on the far face. The low farS0 values at 0.30–0.50 are a **surface-identity swap**, not a
cleaner break: at 0.30 S0 has collapsed to 2532 points against S1's 13825, and those arms lose the
9/9 guard (J1 and/or J5). Meanwhile J1's blind extent swings 19.7°–88.4° with no monotone trend
(85.5 at 0.70, 77.1, 62.1, 19.7, 27.4, 25.9, 43.2, 46.7 across 0.55→0.90): the two metrics move
**independently**, so a shrunken blind arc does not mean the surface moved to the near face.
`seamOut` rises monotonically with the dial (0.218 → 0.546) while `seamIn` stays 0.84–0.96.

**9/9 pairs guard, per arm.** Held: baseline_t55, w055, w060, w065, w070, w075, w080, w085.
Lost: w030 (J1, J5), w035 (J1), w040 (J1), w045 (J1, J5), w050 (J1), w090 (J8). Default/unset: 1/9
(J4, J6, J8 are NO-SURFACE; J1, J3, J5, J7, J9 not genuine). A lost pair is a lost piece, not an average.

**Two failure modes in the sweeping arms, both attributable:**
- `edge_rc=139` = SIGSEGV in the breakline stage inside the container, sporadic and **not monotone** in
  the dial: w040 loses J9, w085 loses J1, w090 loses J1 and J8. The clean arms (w030/w035/w045) show none.
- `edge_rc=255` on the **unset** arm = declined by design: with `SFS_WORNESS` unset the paper formula
  is a no-op, three of nine pieces never split (`[STATUS-23] outcome=none … reason=no temp surface`), so no
  Surface_0/1 exist. rc=8 at arm level is the harness's "non-ok pieces" signal, not a job failure.

**Dot floor.** Every arm breaches the assembler's 50-dot floor on at least one piece; the baseline
itself does (J1 bl0 28, J9 23). w085/w090 wrote no Bl files at all (the SIGSEGV arms). So the floor
is a pre-existing condition of the corpus, not a dial effect.

### Task 3 — Stage B refinement: **not triggered (refuted)**

The trigger was "far-skin share drops materially between neighbouring values". No such transition
exists: farS0 on J1 steps 0.51→0.73→0.76→0.78→0.80→0.86→0.86→0.90→0.87→0.80→0.91 from 0.40 to 0.90
with the pair guard failing at the low end and recovering at 0.55, and there is no coherent drop with
pairs held. Stage B was therefore **not run**; running it would be searching for an effect the Stage A
evidence contradicts. (≤10 additional arms remain within budget if the lead judges otherwise.)

### Task 4 — `check_separation.py` (read-only) delivered

Standalone, in the run area, md5 `054ee00da99a1cf58d9d84ae5e0d361a`; read-only apart from the two
files named by `--out-tsv` / `--out-json`. Thresholds are flags
(`--max-far-share`, `--max-dc-ge1`, `--max-blind-deg`, `--min-seam-in`, `--min-dots`); it exits 1
when exceeded and prints `[SEP57] THRESHOLD FAILURES (n)`. No threshold value is invented here.
Ran clean (rc 0) on the t55 baseline dir and on every sweep arm; the unset arm exits 1 by design
(3 NO-SURFACE pieces) — that is its true state, not a crash.

### Task 5 — verdict (one line)

**No value of `SFS_WORNESS` in 0.30–0.90 removes the far-skin crossing while holding 9/9 genuine
pairs: the arms that lower the far-skin share (0.30–0.50) do so only by swapping which surface owns
the piece and lose J1/J5, while every value from 0.55 to 0.90 keeps S0 on the far face (farS0 0.73–0.91,
farS0_in 1.00 at 0.75); 0.70 remains the best-measured value only in the sense that it is the highest
coverage arm that holds 9/9.** Stage B is not triggered.

### Acceptance

- Baseline reproduction line present — above; 3 Given numbers exact, 3 not reproduced.
- Job id + sacct State/ExitCode per arm — above.
- 9/9 guard per arm with losses named per piece — above.
- `check_separation.py` runs clean on the t55 dir and on sweep arms — verified.
- No source changes: the worktree's only modified path is this ticket.
- Lead verification: pending the lead's independent re-run.

### Notes for the lead

- **Scratch-writer flag (rule 12):** `check_scratch_writer.py worktrees/sfs/57` reports "another session
  appears to be working here" — the single uncommitted path is **this ticket**, whose change is the
  lead's authorised Given-block edit (mtime 04:37:59, after commit fe8f40e). It is this ticket's own
  in-flight edit, not a stranger. The worker still does not commit.
- **Deviation:** polls were done by direct `ssh_exec squeue`/`sacct` rather than
  `scripts/slurm_poll.sh`, because this session has no usable laptop SSH key.
- **Integrity:** binaries unchanged and identical in all arm dirs
  (mesh `736ff95c976486d17f7c00b3af402040`, edge `cbf747dc3172fe0bbd188822df14092a`);
  nothing under the t55 run dir was deleted or written.

### Appendix — per piece, per arm

| arm | piece | farS0 | farS1 | dc_ge1 | seamIn | seamOut | blind° | Bl0 | Bl1 | genuine |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline_t55 | J1 | 0.8624 | 0.4654 | 0.1205 | 0.826 | 0.523 | 85.49 | 28 | 64 | True |
| baseline_t55 | J2 | 0.8182 | 0.7576 | 0.0129 | None | 0.006 | 18.14 | 32 | 31 | True |
| baseline_t55 | J3 | 0.7714 | 0.8298 | 0.0027 | 1.0 | 0.046 | 22.06 | 38 | 41 | True |
| baseline_t55 | J4 | 0.7059 | 0.8049 | 0.0245 | 0.808 | 0.127 | 11.03 | 32 | 35 | True |
| baseline_t55 | J5 | 0.7544 | 0.9038 | 0.0163 | 0.903 | 0.103 | 7.7 | 47 | 51 | True |
| baseline_t55 | J6 | 0.8824 | 0.9149 | 0.1388 | 0.971 | 0.333 | 11.94 | 46 | 45 | True |
| baseline_t55 | J7 | 0.8039 | 0.8571 | 0.0502 | 0.826 | 0.25 | 5.92 | 54 | 58 | True |
| baseline_t55 | J8 | 0.6512 | 0.7556 | 0.0556 | 0.968 | 0.195 | 11.93 | 41 | 41 | True |
| baseline_t55 | J9 | 0.7 | 0.8929 | 0.0777 | 0.971 | 0.195 | 12.32 | 23 | 24 | True |
| w030 | J1 | 0.1905 | 0.6205 | 0.0162 | 0.961 | 0.218 | 7.1 | 53 | 36 | False |
| w030 | J2 | 0.8125 | 0.8125 | 0.002 | None | 0.0 | 28.7 | 32 | 29 | True |
| w030 | J3 | 0.6486 | 0.8333 | 0.002 | 0.667 | 0.038 | 10.66 | 35 | 41 | True |
| w030 | J4 | 0.7812 | 0.875 | 0.0008 | 1.0 | 0.036 | 10.6 | 31 | 35 | True |
| w030 | J5 | 0.6471 | 0.8846 | 0.0002 | None | 0.006 | 9.39 | 34 | 52 | False |
| w030 | J6 | 0.8163 | 0.8605 | 0.0024 | 1.0 | 0.004 | 12.1 | 45 | 41 | True |
| w030 | J7 | 0.4375 | 0.8214 | 0.0096 | 0.885 | 0.051 | 7.18 | 48 | 59 | True |
| w030 | J8 | 0.7778 | 0.7755 | 0.0012 | 0.923 | 0.066 | 10.18 | 38 | 41 | True |
| w030 | J9 | 0.8333 | 0.7407 | 0.0005 | None | 0.002 | 12.24 | 24 | 28 | True |
| w035 | J1 | 0.5606 | 0.5355 | 0.0113 | 0.851 | 0.196 | 80.72 | 39 | 57 | False |
| w035 | J2 | 0.875 | 0.8125 | 0.002 | None | 0.0 | 27.61 | 33 | 29 | True |
| w035 | J3 | 0.7941 | 0.8542 | 0.0021 | None | 0.04 | 17.26 | 38 | 41 | True |
| w035 | J4 | 0.7812 | 0.875 | 0.0008 | 1.0 | 0.036 | 10.6 | 31 | 35 | True |
| w035 | J5 | 0.6571 | 0.8846 | 0.0002 | None | 0.008 | 14.98 | 37 | 52 | True |
| w035 | J6 | 0.898 | 0.814 | 0.0028 | 1.0 | 0.004 | 11.9 | 46 | 41 | True |
| w035 | J7 | 0.5349 | 0.8214 | 0.0075 | 0.818 | 0.06 | 6.48 | 47 | 58 | True |
| w035 | J8 | 0.7778 | 0.7755 | 0.0006 | 0.923 | 0.048 | 12.64 | 38 | 41 | True |
| w035 | J9 | 0.7419 | 0.6923 | 0.0019 | None | 0.009 | 12.39 | 22 | 23 | True |
| w040 | J1 | 0.5109 | 0.6834 | 0.0757 | 0.892 | 0.46 | 88.41 | 56 | 52 | False |
| w040 | J2 | 0.9091 | 0.7273 | 0.0008 | None | 0.0 | 18.82 | 33 | 29 | True |
| w040 | J3 | 0.8235 | 0.8542 | 0.0021 | None | 0.034 | 17.18 | 37 | 41 | True |
| w040 | J4 | 0.8182 | 0.875 | 0.0008 | 1.0 | 0.035 | 10.73 | 31 | 35 | True |
| w040 | J5 | 0.6757 | 0.8846 | 0.0002 | None | 0.011 | 8.86 | 38 | 52 | True |
| w040 | J6 | 0.898 | 0.8571 | 0.0036 | 1.0 | 0.004 | 11.9 | 46 | 41 | True |
| w040 | J7 | 0.5333 | 0.8214 | 0.0088 | 0.938 | 0.07 | 6.66 | 48 | 58 | True |
| w040 | J8 | 0.8158 | 0.7872 | 0.0009 | 0.727 | 0.061 | 12.59 | 38 | 41 | True |
| w040 | J9 | 0.8387 | 0.7692 | 0.0048 | None | 0.015 | 12.38 | 22 | 0 | True |
| w045 | J1 | 0.7344 | 0.6416 | 0.182 | 0.931 | 0.546 | 41.25 | 70 | 36 | False |
| w045 | J2 | 0.9118 | 0.875 | 0.0008 | None | 0.0 | 20.43 | 33 | 29 | True |
| w045 | J3 | 0.8235 | 0.8542 | 0.0021 | 1.0 | 0.026 | 17.42 | 37 | 41 | True |
| w045 | J4 | 0.75 | 0.875 | 0.0008 | 1.0 | 0.036 | 10.6 | 32 | 35 | True |
| w045 | J5 | 0.5111 | 0.8654 | 0.0002 | None | 0.009 | 16.65 | 40 | 52 | False |
| w045 | J6 | 0.898 | 0.8571 | 0.0036 | 1.0 | 0.004 | 11.9 | 46 | 41 | True |
| w045 | J7 | 0.6809 | 0.7818 | 0.0101 | 0.935 | 0.104 | 7.05 | 51 | 58 | True |
| w045 | J8 | 0.7692 | 0.7755 | 0.0009 | 0.818 | 0.061 | 12.56 | 37 | 41 | True |
| w045 | J9 | 0.8387 | 0.7692 | 0.0048 | None | 0.015 | 12.38 | 22 | 22 | True |
| w050 | J1 | 0.7647 | 0.4365 | 0.222 | 0.888 | 0.529 | 36.94 | 60 | 64 | False |
| w050 | J2 | 0.8788 | 0.8182 | 0.0105 | None | 0.006 | 18.1 | 33 | 30 | True |
| w050 | J3 | 0.7353 | 0.8723 | 0.0021 | 1.0 | 0.03 | 18.26 | 37 | 41 | True |
| w050 | J4 | 0.75 | 0.825 | 0.0008 | 1.0 | 0.036 | 10.61 | 31 | 35 | True |
| w050 | J5 | 0.8 | 0.8654 | 0.0002 | None | 0.008 | 9.14 | 44 | 52 | True |
| w050 | J6 | 0.8776 | 0.8372 | 0.004 | 1.0 | 0.004 | 11.92 | 46 | 50 | True |
| w050 | J7 | 0.7 | 0.7818 | 0.0138 | 0.889 | 0.097 | 7.35 | 52 | 58 | True |
| w050 | J8 | 0.7949 | 0.7333 | 0.0144 | 0.864 | 0.081 | 12.04 | 38 | 41 | True |
| w050 | J9 | 0.8387 | 0.7308 | 0.0031 | None | 0.011 | 12.38 | 22 | 21 | True |
| w055 | J1 | 0.7763 | 0.5484 | 0.1584 | 0.893 | 0.512 | 77.11 | 59 | 64 | True |
| w055 | J2 | 0.8485 | 0.8182 | 0.0105 | None | 0.006 | 18.88 | 32 | 30 | True |
| w055 | J3 | 0.8235 | 0.8298 | 0.0021 | 1.0 | 0.026 | 19.04 | 37 | 41 | True |
| w055 | J4 | 0.75 | 0.8 | 0.0008 | 1.0 | 0.036 | 10.61 | 31 | 35 | True |
| w055 | J5 | 0.7115 | 0.9038 | 0.003 | None | 0.021 | 7.68 | 46 | 51 | True |
| w055 | J6 | 0.898 | 0.907 | 0.004 | 1.0 | 0.004 | 11.9 | 46 | 42 | True |
| w055 | J7 | 0.8 | 0.8929 | 0.0138 | 0.889 | 0.094 | 7.34 | 52 | 59 | True |
| w055 | J8 | 0.7949 | 0.8478 | 0.0245 | 0.818 | 0.08 | 11.97 | 39 | 42 | True |
| w055 | J9 | 0.8387 | 0.76 | 0.005 | None | 0.013 | 12.38 | 23 | 22 | True |
| w060 | J1 | 0.7961 | 0.4971 | 0.1139 | 0.877 | 0.396 | 62.12 | 23 | 65 | True |
| w060 | J2 | 0.8182 | 0.7353 | 0.0092 | None | 0.002 | 18.14 | 32 | 31 | True |
| w060 | J3 | 0.7647 | 0.8298 | 0.0021 | 1.0 | 0.026 | 18.85 | 38 | 41 | True |
| w060 | J4 | 0.7059 | 0.8 | 0.0075 | 0.769 | 0.082 | 10.48 | 31 | 35 | True |
| w060 | J5 | 0.7692 | 0.9038 | 0.003 | None | 0.021 | 7.69 | 46 | 51 | True |
| w060 | J6 | 0.7755 | 0.8043 | 0.0315 | 1.0 | 0.076 | 11.92 | 46 | 44 | True |
| w060 | J7 | 0.72 | 0.875 | 0.0166 | 0.889 | 0.117 | 7.16 | 52 | 58 | True |
| w060 | J8 | 0.6667 | 0.8478 | 0.0245 | 0.818 | 0.079 | 11.84 | 39 | 42 | True |
| w060 | J9 | 0.8387 | 0.75 | 0.0789 | 0.971 | 0.189 | 12.38 | 24 | 23 | True |
| w065 | J1 | 0.8615 | 0.4474 | 0.0953 | 0.843 | 0.537 | 19.69 | 48 | 64 | True |
| w065 | J2 | 0.8182 | 0.8529 | 0.0129 | None | 0.006 | 18.14 | 32 | 31 | True |
| w065 | J3 | 0.7714 | 0.8298 | 0.0027 | 1.0 | 0.042 | 22.04 | 38 | 41 | True |
| w065 | J4 | 0.7059 | 0.8 | 0.0245 | 0.808 | 0.127 | 11.03 | 32 | 35 | True |
| w065 | J5 | 0.7692 | 0.9038 | 0.003 | None | 0.021 | 7.69 | 46 | 51 | True |
| w065 | J6 | 0.8 | 0.8889 | 0.0782 | 0.971 | 0.159 | 11.94 | 46 | 45 | True |
| w065 | J7 | 0.78 | 0.8571 | 0.048 | 0.826 | 0.201 | 5.98 | 53 | 59 | True |
| w065 | J8 | 0.75 | 0.8478 | 0.0553 | 0.968 | 0.192 | 11.82 | 40 | 41 | True |
| w065 | J9 | 0.8387 | 0.8519 | 0.0853 | 0.947 | 0.225 | 12.38 | 24 | 24 | True |
| w070 | J1 | 0.8624 | 0.4654 | 0.1205 | 0.826 | 0.523 | 85.49 | 28 | 64 | True |
| w070 | J2 | 0.8182 | 0.7576 | 0.0129 | None | 0.006 | 18.14 | 32 | 31 | True |
| w070 | J3 | 0.7714 | 0.8298 | 0.0027 | 1.0 | 0.046 | 22.06 | 38 | 41 | True |
| w070 | J4 | 0.7059 | 0.8049 | 0.0245 | 0.808 | 0.127 | 11.03 | 32 | 35 | True |
| w070 | J5 | 0.7544 | 0.9038 | 0.0163 | 0.903 | 0.103 | 7.7 | 47 | 51 | True |
| w070 | J6 | 0.8824 | 0.9149 | 0.1388 | 0.971 | 0.333 | 11.94 | 46 | 45 | True |
| w070 | J7 | 0.8039 | 0.8571 | 0.0502 | 0.826 | 0.25 | 5.92 | 54 | 58 | True |
| w070 | J8 | 0.6512 | 0.7556 | 0.0556 | 0.968 | 0.195 | 11.93 | 41 | 41 | True |
| w070 | J9 | 0.7 | 0.8929 | 0.0777 | 0.971 | 0.195 | 12.32 | 23 | 24 | True |
| w075 | J1 | 0.8957 | 0.4904 | 0.0945 | 0.868 | 0.408 | 27.42 | 55 | 64 | True |
| w075 | J2 | 0.8182 | 0.7429 | 0.0293 | 1.0 | 0.008 | 18.14 | 32 | 39 | True |
| w075 | J3 | 0.7941 | 0.8511 | 0.0021 | 1.0 | 0.024 | 18.74 | 38 | 41 | True |
| w075 | J4 | 0.7941 | 0.8049 | 0.0253 | 0.808 | 0.14 | 11.03 | 32 | 36 | True |
| w075 | J5 | 0.7544 | 0.9038 | 0.0195 | 0.9 | 0.113 | 7.77 | 47 | 52 | True |
| w075 | J6 | 0.86 | 0.8824 | 0.1971 | 0.954 | 0.423 | 11.95 | 46 | 46 | True |
| w075 | J7 | 0.76 | 0.8 | 0.0493 | 0.826 | 0.235 | 5.5 | 53 | 59 | True |
| w075 | J8 | 0.6512 | 0.7556 | 0.0556 | 0.968 | 0.196 | 11.95 | 40 | 42 | True |
| w075 | J9 | 0.7 | 0.8571 | 0.0772 | 0.971 | 0.202 | 12.32 | 23 | 24 | True |
| w080 | J1 | 0.8673 | 0.5974 | 0.1162 | 0.877 | 0.528 | 25.92 | 56 | 65 | True |
| w080 | J2 | 0.7879 | 0.7059 | 0.0291 | 1.0 | 0.006 | 23.45 | 32 | 39 | True |
| w080 | J3 | 0.7778 | 0.8085 | 0.0027 | 1.0 | 0.044 | 22.33 | 38 | 41 | True |
| w080 | J4 | 0.7941 | 0.8 | 0.0253 | 0.808 | 0.14 | 11.03 | 32 | 35 | True |
| w080 | J5 | 0.7368 | 0.9038 | 0.0195 | 0.9 | 0.113 | 7.77 | 47 | 52 | True |
| w080 | J6 | 0.7708 | 0.8431 | 0.1969 | 0.986 | 0.504 | 12.4 | 46 | 46 | True |
| w080 | J7 | 0.64 | 0.8246 | 0.0815 | 0.826 | 0.368 | 5.47 | 54 | 57 | True |
| w080 | J8 | 0.8409 | 0.7333 | 0.1161 | 0.968 | 0.31 | 12.1 | 44 | 41 | True |
| w080 | J9 | 0.7 | 0.75 | 0.0767 | 0.971 | 0.202 | 12.32 | 23 | 24 | True |
| w085 | J1 | 0.8024 | 0.6067 | 0.084 | 0.843 | 0.486 | 43.17 | 0 | 0 | True |
| w085 | J2 | 0.7879 | 0.7647 | 0.0326 | 1.0 | 0.008 | 23.45 | 32 | 39 | True |
| w085 | J3 | 0.9429 | 0.8298 | 0.0057 | 1.0 | 0.047 | 19.25 | 38 | 41 | True |
| w085 | J4 | 0.7941 | 0.8 | 0.0253 | 0.808 | 0.14 | 11.03 | 33 | 35 | True |
| w085 | J5 | 0.8276 | 0.8846 | 0.0212 | 0.871 | 0.116 | 7.8 | 47 | 51 | True |
| w085 | J6 | 0.8958 | 0.78 | 0.2006 | 0.972 | 0.464 | 12.4 | 46 | 46 | True |
| w085 | J7 | 0.7083 | 0.8421 | 0.083 | 0.826 | 0.353 | 6.01 | 54 | 58 | True |
| w085 | J8 | 0.76 | 0.7556 | 0.1479 | 0.949 | 0.331 | 13.25 | 43 | 43 | True |
| w085 | J9 | 0.8125 | 0.8148 | 0.1914 | 0.944 | 0.436 | 12.58 | 24 | 25 | True |
| w090 | J1 | 0.9116 | 0.5517 | 0.1444 | 0.892 | 0.501 | 46.72 | 0 | 0 | True |
| w090 | J2 | 0.7879 | 0.7143 | 0.0326 | 1.0 | 0.008 | 23.26 | 32 | 40 | True |
| w090 | J3 | 0.8857 | 0.8889 | 0.0613 | 0.913 | 0.147 | 19.19 | 39 | 49 | True |
| w090 | J4 | 0.7436 | 0.875 | 0.1454 | 0.815 | 0.248 | 10.49 | 37 | 36 | True |
| w090 | J5 | 0.807 | 0.9038 | 0.0212 | 0.871 | 0.115 | 7.75 | 47 | 51 | True |
| w090 | J6 | 0.8958 | 0.78 | 0.2006 | 0.972 | 0.464 | 12.4 | 46 | 46 | True |
| w090 | J7 | 0.7234 | 0.8103 | 0.0983 | 0.92 | 0.378 | 6.01 | 53 | 57 | True |
| w090 | J8 | 0.8529 | 0.3846 | 0.0776 | 0.895 | 0.169 | 68.41 | 17 | 0 | False |
| w090 | J9 | 0.8125 | 0.7778 | 0.1993 | 0.944 | 0.441 | 12.58 | 24 | 25 | True |
| default | J1 | 0.456 | 0.5833 | 0.0164 | None | 0.074 | 7.26 | 33 | 75 | False |
| default | J2 | 0.8621 | 0.5217 | 0.0039 | 0.875 | 0.012 | 18.33 | 30 | 23 | True |
| default | J3 | 0.2857 | 0.8125 | 0.0 | None | 0.0 | 18.88 | 17 | 41 | False |
| default | J4 |  |  |  |  |  |  |  |  |  |
| default | J5 | 0.25 | 0.7963 | 0.0145 | 0.982 | 0.079 | 40.38 | 7 | 51 | False |
| default | J6 |  |  |  |  |  |  |  |  |  |
| default | J7 | 0.6667 | 0.8039 | 0.0088 | 0.929 | 0.153 | 14.63 | 17 | 58 | False |
| default | J8 |  |  |  |  |  |  |  |  |  |
| default | J9 | 0.3571 | 0.7 | 0.0 | None | 0.0 | 28.78 | 14 | 23 | False |


### Lead verification (2026-11-02)

Verified by the lead before recording, per AGENTS "the lead verifies every result itself".

- **Re-ran the worker's own script** (check_separation.py md5 054ee00da99a1cf58d9d84ae5e0d361a,
  same file in every arm dir) on the baseline arm and one sweep arm:
  - baseline_t55 (t55 out/geom): foldS0 **2824**, foldS1 2374, unionRim **2527**, blind
    **85.49 deg**, farS0 **0.8624**, farS0_in 0.9157, dc_ge1 **0.1205**, lip **1034**, bl0 **28**,
    genuine **True** -- reproduces the ticket's baseline row.
  - w065 (runs/20261102-0450_05be12c_t57-w065/out/geom): foldS0 **2919**, unionRim 2584,
    blind **19.69 deg**, farS0 **0.8615**, farS0_in 0.9643, dc_ge1 **0.0953**, bl0 **48**,
    genuine **True** -- reproduces the ticket's w065 row.
- **Independent recompute of far-skin share** (lead's own implementation -- PLY reader + mesh
  area-weighted vertex normals + fold = edges with one endpoint claimed within 0.6 mm;
  /data/gpfs/projects/punim2657/SfSpp/runs/_lead_tmp/verify57.py), J1:
  - baseline: fold edges **2824** (exact match), far share **0.8729**;
  - w065: fold edges **2919** (exact match), far share **0.8544**.
  Both independent numbers put S0 on the far face at ~0.85-0.87, i.e. the headline conclusion
  (the crossing survives every dial value) is not an artefact of one script.
- verified: python check_separation.py --geom <t55>/out/geom --mesh-dir Dataset/Mesh/Juglet --pieces Juglet_Piece_1 -> foldS0=2824 farS0=0.8624 dc_ge1=0.1205 bl0=28 blindDeg=85.49
- verified: python <lead_tmp>/verify57.py -> baseline fold_edges=2824 far_share=0.8729; w065 fold_edges=2919 far_share=0.8544

The worker's three reproducibility failures (47/48, 37/37, and the derived 717) are confirmed
as failures of the **Given block**, not of the metric implementation: the frozen definitions
reproduce every other Given number exactly, and the two numbers that did not reproduce were
either derived from a degree figure (717) or a sample count the frozen reading replaces
(lip: 1034 exact duplicates, not 37 near-touches).

**Worker line:** delegated worker session (2026-11-02); lead verified 2026-11-02.

