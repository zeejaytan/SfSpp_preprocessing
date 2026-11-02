# 63 — Why the orientation pass flips one whole sheet past a patch-size threshold

**What to build:** the measured mechanism for the sheet flip ticket 62 located (sound at
k <= 12 / radius <= 1.0 mm, ~42 % flipped at k = 19 / radius 1.4 mm, on J1 only), and the
answer to whether the safe patch size must adapt to any physical attribute of the sherd or
pot. Analysis only: no tracked source changes, no default changes, nothing adopted. The
adopt-or-park decision on radius 1.0 mm is the conservator's and is NOT part of this ticket.

**Answers:** U19, E1

**Blocked by:** 62 (its Stage-1 replica and run directories are this ticket's instrument and
baseline)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-03)
**Branch:** 63-orientation-flip-mechanism, in /c/PR/worktrees/sfs/63
**Worker:** unassigned

## Spec

### Given (measured facts this stands on)

1. Ticket 62 Stage 1 located the fault: a sharp threshold **inside the orientation pass**,
   not in the plane fit and not wall bridging. On J1 (replica, agrees with the pipeline at
   k=19: 41.88 % vs 41.63 %, S0 93.33 % vs 93.23 %): flipped 0.24/0.24/0.22/0.19 % at
   k=6/8/10/12, **41.88 % at k=19**; radius 0.8 mm 0.25 %, 1.0 mm 0.21 %, **1.4 mm 42.06 %**
   (bare) / 41.56 % (with the shipped 5..20 clamp). J2 and J7 are flat 0.26-0.85 % at every
   setting. Cause NOT measured — that is this ticket.
2. The default path: `CGAL pca_estimate_normals` with `nb_neighbors = max(5, min(20, n/1000))`
   (`mesh_processing_headless.cpp:680`), then `CGAL::mst_orient_normals` at `n24orientK`
   (`:806-809`). J1's growth call has n=19312, so k=19 — just past the cliff.
3. Wall bridging is refuted: 0 % of points on J1/J2/J7 have a k-th neighbour beyond the wall
   at any k (J1 k=19 max 1.63 mm against a 1.876 mm wall); J1's crossing fraction 0.26-0.55 %
   is LOWER than J2 (0.93-1.42 %) and J7 (0.42-1.00 %).
4. The flip is one connected sheet decided once: the graph is one component at every scale
   except the bare 0.6 mm ball (1024 components); J1's flipped points form 9-13 groups with
   99.61-99.69 % in the largest; within S0, 2-4 groups with 99.96-99.99 % in the largest.
5. Only J1 flips. Walls: J1 1.876, J2 2.178, J7 2.839 mm — the cliff (between 1.0 and 1.4 mm)
   is not a fixed fraction of any of them, and J2/J7 never flip at any size.
6. Instruments and baselines already on Spartan:
   - t62 Stage 1: `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0028_ca520fe_t62-normalfix`
     — `work/stage1_bridging.py` (the replica to instrument: PCA patch fit + MST orientation,
     edge weights 1-|ni·nj|, seed at max-z oriented toward +z, as CGAL does), `out/stage1_bridging.tsv` /
     `.json`, figure `out/stage1_bridging.png` (md5 f6ab510257612c96a8dc62d94a21018f).
   - t61: `runs/20261102-1744_f1e876d_t61-soundfield` — `outU/normals/<piece>_call1.ply`, the
     k=19 field the stop consumed.
   - t62 Stage 2: `runs/20261103-0035_ca520fe_t62-normalfix-s2` — outF/outFA normals at radius
     1.0 mm (the sound field).
   - Meshes: the same `Dataset/Mesh/<pot>` paths the t62 scoring job used (exact strings in
     its `submit.sbatch` / logs). J1 mesh md5 b447066c29181fe7ba987439c22c5d9c.

### Build (three stages, in order)

**Stage 1 — instrument the orientation walk (J1, J2/J7 as controls).** Extend the Stage-1
replica into a recording walk: same graph, same weights, same MST, same seed; record for
every MST step the edge taken, its weight, both endpoints' arrows against the mesh (dot
products), and the running flipped share. **Calibrate first:** the instrument must reproduce
J1 ≈ 41.9 % flipped at k=19 (within 2 points) and soundness at k=12 and radius 1.0 mm, and
flat J2/J7, before any conclusion is drawn. Then answer, with numbers:

- **H1 (seed):** the seed's own arrow is wrong, or near-parallel to the surface (|dot| to
  mesh small), at large patches and right at small ones.
- **H2 (bridge):** between sound and flipped settings the MST GAINS edges connecting the two
  sheets (endpoints on opposite sheets by the S0/S1 labels; endpoint arrows near-perpendicular).
  Locate those edges on the sherd: distance to the fold/rim crease set and the dihedral across
  them (t59's stage-0 region labels and fold points are available in its run dir).
- **H3 (smoothing):** at larger patches the crease-region arrows rotate toward agreement
  BEFORE the flip appears — the crease becomes transparent to the walk with no new edges.

Distinguish H2 from H3 by diffing the MST edge sets and weights between a sound setting
(k=13 or radius 1.0 mm) and k=19: new edges ⇒ H2; same edges with rotated endpoint arrows ⇒ H3.

**Stage 2 — cross-pot field probe at shipped defaults.** Does any piece of another pot flip
at the default? Run the mesh stage with everything unset for **Pot A (all 8 pieces**,
full-res meshes, median spacing 0.286 mm**)** and **up to 8 Pot D pieces** (decimated,
0.39-0.59 mm — the other density class; pick pieces with released clouds), then count the
growth-call arrows' backwards share against each mesh (t61/t62's majority-sign method).
Report per piece. Any piece over 5 % is a second natural experiment: record it, and run the
Stage-1 instrument on it if budget allows.

**Stage 3 — verdict.** State which hypothesis held, or that none did and what was excluded;
state the cliff's physical meaning (what quantity, in mm or degrees, separates sound from
flipped); answer the adaptivity question: is there a measured physical predictor of the
cliff, or is the practical guard a per-pot arrow gate (field check before trusting the
chain)? No adoption recommendation.

### Gates

1. **Calibration:** instrument reproduces the replica's J1 flip at k=19 within 2 points and
   soundness at k=12 / radius 1.0; J2/J7 flat. On failure: stop and report — conclusions
   about the pipeline are not permitted from an uncalibrated instrument.
2. **Corpus read-only:** md5 of every mesh/cloud read, before and after; an empty diff file
   in the run dir proves it.
3. **No tracked source changes, no default changes.** Probe scripts live in `work/` in the
   run dirs. Any build is a read-only build of the unmodified tree.
4. Every sbatch polled to completion; final sacct State/ExitCode recorded in the ticket.
5. **Budget: <= 4 jobs, <= 3 h wall total.** If the instrument cannot be calibrated within
   2 jobs, stop and report — do not spend Stage 2's budget.
6. Claims from the instrument are labelled **replica**; only the cross-pot probe and quoted
   pipeline log lines are pipeline claims.

### Runs and traps

Run dirs `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t63-<tag>/` per the
repo convention (`run.json`, `submit.sbatch`, `logs/`, `out/`); append-only `index.tsv`
rows with `verdict` and `human_note` left EMPTY (the lead fills them). Spartan python:
`/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`. Use **Windows ssh** for spartan
from Git Bash (Git Bash's own ssh has no key); poll jobs with `sacct` directly.

### Worker rules

Run the ticket end to end from this file. Append a `## Results` section to THIS file with
jobs/sacct/index rows, calibration numbers, the H1/H2/H3 verdict with measurements, the
cross-pot table, the propagation figure (one picture the conservator can read: J1 with the
wrong sign's entry point and crossing path coloured, sound vs flipped patch size side by
side), a not-measured list, and a per-piece + overall verdict with NO adoption
recommendation. Do not edit `Status:`, do not commit, do not touch other tickets.

### Verdict language

Name the claim type: a mechanism finding is a claim about the instrument unless reproduced
in the pipeline's own output; the cross-pot probe is a direct pipeline measurement. State
the weight: how many pieces, how many runs.
