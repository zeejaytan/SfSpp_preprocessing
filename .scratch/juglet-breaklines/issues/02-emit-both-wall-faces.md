# 02: Fix the breakline trace so it covers the seam

**What to build:** the smallest change to `edgeline_extraction.cpp` that
makes Juglet breaklines usable to a 2 mm / agreeing-normal join gate,
**one variable at a time**, each re-measured.

**Answers:** E1

**Blocked by:** 01 (resolved — see its results)

**Status:** ready-for-agent — diagnosis complete, patch 1 refuted, source
now tracked

## Source state is committed and resettable (2026-09-26)

The applied preprocessing source was **untracked** (nested clone with its
own `.git`, invisible to the parent repo), so it could not be reset or
reproduced, and patch 1 was one `git checkout` from being
unrecoverable. Now committed and pushed:

- Branch **`nested-applied-2026-09-26`**, commit **`4c0b90b`**, files
  `edgeline_extraction_headless.cpp` + `mesh_processing_headless.cpp`,
  holding the seven 2026-09-25 patches as applied source. Patch 1 is
  deliberately absent (refuted, reverted).
- **Not `main`:** the nested clone and the parent repo are two divergent
  histories pushing at the same GitHub URL, and the remote's `main` is
  the parent lineage. A `main` push was correctly rejected and would have
  clobbered the repo everything depends on. Details and reset commands:
  `patches/SOURCE_ANCHOR.md`.
- **Still open:** the laptop clone has no `original_nurbs_preprocessing/`
  at all, so patches still cannot be verified laptop-side without
  copying the file off Spartan. Worth vendoring or submodule-ing — not
  actioned here.

**Needs-eye:** a `visual-qa` pair showing the traced rim against the true
seam, correct-vs-attempt, witnessed, before any claim of improvement is
recorded. The gate number alone does not close this ticket.

## Re-scoped 2026-09-26: the original premise was wrong

The ticket was written as "make the extractor emit both wall faces". It
already does — `Breakline_0` *and* `Breakline_1`, both genuine surface
traces (0.07–0.34 mm from their surface on 7 of 9 sherds). There is no
missing-face bug in our code. Worse, **the assembler reading both would
make things worse**, so that is not the fix either:

| breaklines given to the gate | true mates pass | false pairs pass |
|---|---|---|
| `_0` only (what the binary does) | 0/18 | 1/18 |
| `_1` only | 0/18 | 1/18 |
| both pooled | 1/18 | **4/18** |

Pooling lets an inner-face point match an outer-face point 0.17 mm away
with opposed normals. All four face-pairing conventions (`0↔0`, `1↔1`,
`0↔1`, `1↔0`) were tested: only **1/18** passes under *any* of them. Face
pairing is not the lever.

Output: `../structure-from-sherds-pp/artifacts/juglet_run1/`
(`both_breaklines_test`, `face_pairing_test`, `normal_convention_test`).

## DIAGNOSIS — the trace path, four defects

Path: `getInitialBoundary_UsingPCL_BoundaryAlgo` (line 629) →
`getPointsInSequence` (line 543) → BSpline resample (line 480) →
`writeBreaklinePCDWithSegments` (line 1042). The rim is found by **PCL
`BoundaryEstimation`** and the loop is then *walked*, not reconstructed.

### 1. The walk is non-local (K=50), so it derails and stops early

`getPointsInSequence` is a nearest-neighbour chain: from the current point
it fetches **K=50** nearest and appends the first not already used. The
intent is "step to the adjacent unused point"; with K=50 that is defeated
whenever 50 points are in reach — the walk hops across the rim interior,
consumes a nearby cluster, then stops because all 50 candidates are used
while the outer loop spins. `pointExistsInCLoud` tests **exact float
equality**, so near-duplicates count as new and the walk crawls.

Observed on the Juglet run's own intermediates: **59 boundary points
sequenced to 9** — a short arc, not a rim.

### 2. The traced "loop" has large internal discontinuities

Largest step between consecutive points, vs median step:

| sherd | max step | median | | sherd | max step | median |
|---|---|---|---|---|---|---|
| 5 `_0` | **24.4 mm** | 0.26 | | 6 `_0` | **16.6 mm** | 0.14 |
| 1 `_0` | **19.4 mm** | 0.30 | | 8 `_0` | **10.2 mm** | 0.12 |
| 4 `_0` | **10.0 mm** | 0.24 | | 7 `_0` | 5.2 mm | 0.58 |

Not loops — two arcs **jumped together**, which is what a derailed greedy
walk produces. Traced length vs the rim it should cover (2πR) runs
**0.27–2.15**: sherd 5 `_1` traces 27% of its rim; sherd 9 `_1` is a
degenerate **3.6 mm** curve carrying all 200 of its points.

### 3. The outlier filter is dead code

Line 741 computes `cloud_filtered = RadiusOutlierRemoval(…, 2.5 mm, 6)`,
writes it, prints its size — then **line 745 reloads the unfiltered
`boundary.pcd` over `boundaryCloud_Improved`** before sequencing. The
filter is never used. (On the Juglet it was a no-op anyway: 59 of 59
kept.)

### 4. The 200-point count is padding, and it hid all of the above

Every breakline file has exactly 200 points regardless of what was traced,
because the densifier pads. **The ticket-02 lesson repeating itself:** a
bundle passed "200 points per file" while containing a 3.6 mm fragment.
Point count has carried no information about trace quality.

### Also suspect, deliberately NOT yet tested

`boundary_est.setRadiusSearch(4)` with `setAngleThreshold(M_PI * 0.6)` =
**108°**. Very permissive; will flag interior concave features of a rough
eroded surface as "boundary", which fits the traced loop sitting radially
*inside* its own surface's extent on 5 of 9 sherds. Kept as a separate
variable so it is not confused with 1–4, which are established.

## PATCH 1 RESULT (job 31337092): **REFUTED — the K hypothesis was wrong**

Run to completion, intervention verified (all 8 markers present, `int
K = 2` in the source, `using K=2` on all pieces at runtime, zero
`using K=50` lines). It made things **markedly worse**.

| | old (adaptive K) | new (K=2) |
|---|---|---|
| true mates passing the gate | 0/18 | 0/18 |
| false pairs passing | 1/18 | **0/18** |
| closest true contact to a breakline point | **0.17 mm** | **11.74 mm** |
| sherd 4 trace extent | 10.0 × 12.9 × 14.0 mm | **0.09 × 0.19 × 0.22 mm** |
| unique points @0.01 mm (shard 4) | 200/200 | **46/149** |
| traced length / 2πR | 0.27–2.15 | **0.01–0.15** |

**The adaptive K was load-bearing, exactly as its comment claimed.** With
K=2 the nearest unused neighbour is almost always *another member of the
same tight cluster*, so the walk crawls through duplicates, one per
outer-loop iteration, and never leaves. The trace collapses to a
sub-millimetre blob. The large K was crudely but effectively letting the
walk **escape** the duplicate cluster by reaching a genuinely different
point.

**So the real defect is upstream of the walk: the boundary cloud is
duplicate-dominated.** `pcl::BoundaryEstimation` on a dense surface
returns large numbers of near-coincident points, and the NN-chain has no
notion of stepping *along* a curve. The fix is therefore not a smaller
K but a proper one:

1. **Cluster/dedupe the boundary cloud first** (radius ~ the surface
   spacing), *then* walk with a small K. Or replace the chain outright
   with an ordering that cannot stall — a 2D minimum spanning tree or a
   principal curve, which is what the function name
   (`_breakLineFromConcaveHull`) suggests it was meant to be.
2. Only then re-test K.

**The known-good bundle is untouched** — the run wrote to
`Juglet_Dataset_walkk1`, so `Juglet_Dataset_20260916` remains the
reference. The K=2 output is kept in `artifacts/juglet_bl_walkk/` as the
negative result, not as a candidate.

**Six submissions to run one experiment.** Five failed on my own script
errors (patch path, wrong source file, non-idempotent patch chain,
relative path after a successful build, redirect into a missing
directory, mesh staging collision). All died in under a minute before
any compute, all printed the cause. The experiment itself ran first
time. Cost: ~25 minutes of queue time and six chances to be wrong. **On
a held allocation this would have been one attempt** — recommend
switching for the next patch.

## Patch 1 was launched — and a build-target correction

**The defect was in a different file than first diagnosed.** The
assembler-facing `edgeline_extraction.cpp` has a hardcoded `K = 50`, but
that file **is not compiled** — `run_juglet_preprocessing.sbatch` builds
`EdgeLineExtractionHeadless` from `edgeline_extraction_headless.cpp`,
whose walk uses an *adaptive* `K = max(5, min(50, n/10))`. Same class of
defect (non-local walk, first-unused-among-K), different code. The
patch targets the headless file, and defect 3 (dead reload) is present
there too, at line 1032.

A first patch was written against the non-compiled file and **deleted
rather than shipped** — it would have applied cleanly and changed
nothing, which is the quietest possible way to produce a false null.

Patch 1 = `K: max(5, min(50, n/10)) → 2`, one hunk, marker
`SFS_WALK_K_LOCAL`, generated with `difflib` from the git blob so the
hunk count and line endings are exact (hand-written hunks were wrong
twice; the patch is **LF** because that is what Spartan checks out, and
it verifies at `patch --fuzz=0`).

Job 31336680 also: writes to a **separate output base**
(`Juglet_Dataset_walkk1`) so the known-good bundle survives a
regression; greps the marker in the source *before* building and again
in the runtime log (`using K=50` present ⇒ stale binary ⇒ void run);
and does **not** run the gate itself — scoring a re-extract from inside
the extracting job is how a broken input gets certified by its own
producer. The gate runs on the laptop afterwards.

## Fix order — one variable each, re-measure after every one

1. **K: 50 → 2** in `getPointsInSequence`, and stop appending when the
   immediate neighbours are exhausted so the walk terminates honestly
   instead of derailing. *The evidence points hardest here.*
2. **Close the loop explicitly** rather than trusting the walk to return.
3. **Delete the dead reload at line 745** (or move the filter ahead of
   sequencing).
4. **Stop padding to a fixed 200**, or record traced length beside point
   count so coverage is visible.
5. Only then, separately: the 108° angle threshold and the 4 mm radius.

**If step 1 alone does not move the gate number, say so — do not bundle.**
A bundle of fixes that works teaches nothing about which one did it, and
this repo already made that mistake once today.

## Discipline

- One variable per experiment; each lands as a versioned patch in
  `patches/`, named `juglet_edgeline_<what>.patch`, applied from the
  nested dir, **one hunk per file**. `patch` silently drops misordered
  hunks while exiting 0 — after every patch, verify the marker appears in
  the built binary's output.
- Never hand-edit the Spartan checkout's tracked files. Untracked data
  there is skip-worktree flagged; check `git ls-files -v | grep ^S` before
  a pull that touches those paths.
- Acceptance test is `python
  ../structure-from-sherds-pp/artifacts/juglet_run1/gate_probe_b0.py <bundle>`,
  not a render and not a point count.

## Acceptance

- Juglet true-mate pass rate at ground truth is materially non-zero, and
  quoted **per pair**, not as a total only.
- **Pot_A still 15/15.** If not, the change is Juglet-only and must be
  labelled so in the ticket and in E1.
- A witnessed `visual-qa` look at the seam, correct-vs-attempt.
- **The remainder recorded honestly:** which mates still fail, and whether
  the cause is wear, wall thickness, or both. "Fixed" is unavailable until
  the probe says so.
- If the probe passes and the assembler still finds nothing, **that is a
  finding, not a failure here** — hand it to
  `../structure-from-sherds-pp` with the numbers attached.

## Belongs to the other repo (recorded, deliberately not actioned)

Two sherds that mate share one fracture surface, so their normals are
**antiparallel** (dot ≈ −1) while `UnifiedPotteryValidation` demands
`dot > +0.85`; `robust_icp.cpp:396` already uses `abs(dot)` — the pipeline
contradicts itself. At ground truth `abs` lifts true mates **0/18 → 2/18**
with no extra false pairs. This was "refuted" earlier only at ~10 mm-off
refined placements, never at truth. It is an **assembler** change and
belongs in `../structure-from-sherds-pp`.
