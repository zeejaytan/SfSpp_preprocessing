# Fork vs upstream — preprocessing audit (our changes)

This document replaces the Nov-2025 `COMPREHENSIVE_CODE_DIFFERENCES.md`
(assembly repo root) **for our changes**. That doc's headless-adaptation
analysis (its §§1–2, categories A–K) is still the accurate record of the
*cluster-lineage* layer and is cited, not duplicated, below. Everything
this fork changed after the vendoring snapshot — and the Sep-2026
Juglet-enablement work that entered *through* that snapshot — is
attributed and classified here. Ticket:
`.scratch/juglet-breaklines/issues/19-fork-vs-upstream-preprocessing.md`
(Answers E1; audit only, no code changed).

## Pinned baselines

- Upstream: `DominicoRyu/SfSpp_preprocessing`, `upstream/main` @
  `d5ee6865ab1e585d18175670a0cd834e846d4490` (fetch ref 2026-10-01;
  `250306_v2`). Re-pinned at audit time: `git rev-parse upstream/main`
  returns this SHA, so upstream has not moved.
- Ours: `origin/HEAD` at audit time =
  `9f33d0918d8c59217051c50e34828f4fb6a8e114`
  ("Ticket 19: fork-vs-upstream preprocessing audit" — the doc commit
  itself is the audit; source SHAs below are unaffected by it).
- Live source is `original_nurbs_preprocessing/` (all our build scripts —
  `build_all.sh`, `build_seam.sh`, `build_ticket04.sh` — compile there).
  Upstream keeps `edgeline_extraction.cpp` + `mesh_processing.cpp` at root;
  ours live as `*_headless.cpp` under `original_nurbs_preprocessing/`.
  Pairwise comparison below is upstream-root-file ↔ our-headless-file.

## Attribution method (attribution BEFORE classification)

Three layers, separated mechanically, not by judgement:

1. **Upstream** — `upstream/main` (`d5ee6865`).
2. **Cluster lineage** — everything up to the vendoring commit `3095064`
   ("Vendor the pipeline source from the nested clone"). This includes the
   ~20 research commits *and* is the snapshot the headless files entered
   through — so a hunk present at `3095064` is *provisionally* cluster,
   then corrected by step 3.
3. **Ours, two entries** —
   (a) `git diff 3095064 HEAD` on the source (18 files, all under
   `original_nurbs_preprocessing/`; every hunk maps to a ticket commit,
   listed per hunk below);
   (b) **ours-via-vendoring**: the seven `patches/juglet_*.patch` files
   (commits `f5db0cd`, `a41a91e`, `dafacd5`, `1e5bd33`, `3278653`,
   pre-vendoring Sep-2026 ticket-02/Step-1 work) whose content is baked
   into the `3095064` baseline. `patches/SOURCE_ANCHOR.md` is the
   contemporaneous record: it names the seven patches, their markers, and
   states walk-K=2 is deliberately absent (refuted, `92f9712`). Each
   marker was verified present (or absent, for K=2) in HEAD source.

`git blame` on the headless files cannot see through the vendoring
snapshot, which is why the patch files — not blame — are the attribution
instrument for layer 3(b).

## Cluster-layer summary (not re-litigated)

Upstream-root → `3095064` headless, in brief (details: Nov-2025 doc §§1–2,
still accurate for these):

- Headless build: VTK includes out, container paths (`Temp/` not `../Temp/`,
  `Dataset/` prefixes), `POT_NAME`/`NURBS_OUTPUT_BASE` env routing in
  `data_path.h`, headless CMake targets. No paper behavior.
- Adaptive pipeline stages with no paper equivalent: adaptive
  sphere-marching radii, `adaptiveDensifyBreakline` (2.0mm-to-200-cap form),
  adaptive walk K (`max(5,min(50,n/10))`, upstream used fixed K=50 —
  upstream `edgeline_extraction.cpp:565`), adaptive boundary/outlier radii
  (meters-assumed form), single-file argv plumbing, `SFS_SMOOTHNESS_DEG`
  env plumbing with Nov-2025 defaults.
- Paper-adjacent cluster choices: region-growing defaults 4.5°/1.5 are
  **upstream's own** (`mesh_processing.cpp:1735-1736`), not ours; the
  `substr(0,14)` name truncation is upstream's (`:683`); the 0.12 rim
  curvature gate is upstream's (`:2382`); Euclidean decorative path, retry
  loop (`smoothnessAngleThreshold -= 2`, `:1355`), and
  `getBreakLineForDecorativeParts` (computed and dropped) are upstream's.
- MATLAB: 26/28 shared `.m` files byte-identical to upstream; the 2
  differences (`compute_cao_error.m` cross-product dims,
  `run_potsac.m` integer-half + adaptive step) are cluster commit
  `ff40fc9`. The 9 extra `.m` files are cluster NURBS helpers.

Where the cluster layer affects paper behavior it is said so inline below;
otherwise it stands as summarized.

## Per-file hunk table — ours

Layer key: **O** = our ticketed commit (`3095064..HEAD`); **V** = ours via
vendoring (patch file + marker verified in HEAD); **C** = cluster lineage;
**U** = upstream. Classification key: **PM** PAPER-MATCH (implements
§IV-B1 as written) · **DM** DEVIATION-measured (differs, ticket + numbers)
· **RB** ROBUSTNESS-no-behavior (guard/logging/loud-failure; sane-input
behavior unchanged or the changed behavior was the bug) · **IN** INFRA ·
**UA** UNATTRIBUTED.

Paper citations are to `C:\PR\papers\text\sfspp-2502.13986v1.md`
(`papers/text/sfspp-2502.13986v1.md`): L151 region growing
(τθ=4, τκ=1, nb=10) · L153 merging "until no further merges are possible"
· L155 two largest clusters + decorative separation · L160 classification
ray test · L164 edge line (PCL boundary estimation, B-spline, KD-tree
noise filter, 1.9mm equidistant resample, CCW ordering vote, corner
segmentation) · L173 PotSAC both surfaces · L177 rim criteria (σ≤1.0mm,
Δ≤0.1mm, ≥20 pts) · L179/194 Savitzky-Golay + Gaussian(7, σ=2.0) ·
L329 fragments <50 points excluded from datasets.
Ticket-16 citations are to
`.scratch/juglet-breaklines/issues/16-paper-compliance-audit.md` ("16").

### File 1: `original_nurbs_preprocessing/edgeline_extraction_headless.cpp`
(12 hunks, `git diff 3095064 HEAD`, `@@` headers quoted verbatim)

| # | Hunk (`@@`) | Layer | Class | Ticket / paper-line |
|---|---|---|---|---|
| E1 | `@@ -29,6 +29,17 @@` includes (`edge_line_ordering.h`, `boundary_radius_override.h`, `boundary_filter.h`) | O (`3ce060e`, `495523a`, `17a3b7f`) | IN | include-only; no behavior |
| E2 | `@@ -701,66 +712,67 @@` resample call: fixed 2.0 → `SFS_RESAMPLE_MM`-overridable, default **1.9** | O (`235657b`) | DM | 16 dev 4, now FIXED. Paper L164 d=1.9mm. Measured ticket 06: old form inflated a 3.6mm fragment to 200 points; new form resamples `round(perimeter/spacing)` uniform arc-length |
| E3 | `@@ -772…` + `@@ -803…` densify body rewritten (mm throughout, no [30,200] clamp, `max(2,…)`, fragment warning) | O (`235657b`) | DM | 16 dev 4, now FIXED (same ticket/numbers as E2; two hunks, one change) |
| E4 | `@@ -803…` walk bodies moved to `edge_line_ordering.cpp` (verbatim incl. adaptive K + commented alternative) | O (`3ce060e` + removals `627fe4d`,`a113517`) | RB | 16 dev 2 (walk still NN, still no vote — unchanged). Move proven behavior-preserving: 8/9 pieces byte-identical re-run, 9th segment-header nondeterminism per `SOURCE_ANCHOR.md`; `scripts/diagnostics/verify_extraction.py` enforces remainder-identity |
| E5 | `@@ -964…` T11 radius-override hook (env absent → adaptive value untouched) | O (`495523a`, `ee1b327`) | RB | diagnostic hook; default path provably unchanged. 16: not a paper behavior (no hunk unknown to 16 — see cross-check C3) |
| E6 | `@@ -992…` unclustered-load guard (missing/empty → proceed unimproved, loud) | O (`4511415`; comment says SFS-T07, commit sits in the T17 corruption cluster — label nit, attribution unaffected) | RB | empty-input guard; same-output on sane input. Previously SIGABRT exit 134 left 4/18 breaklines silently missing |
| E7 | `@@ -1021…` filter wired through shared seam; `boundary.pcd` reload **deleted**; empty-filter loud fallback; sequence the filtered cloud | O (`17a3b7f`, `561c9ce`, `1267c32`) | PM | 16 dev 3, now FIXED. Paper L164 KD-tree noise/outlier filter. Radius = boundary radius ×8/6 ([2,20] clamp kept); neighbors 3/6 by cloud size |
| E8 | `@@ -1457…` traced-length log + <9.5mm fragment warning (stdout; format untouched for the assembler) | O (`235657b`) | RB | logging only. Deliberately not a file comment: assembler header parser is position-sensitive |
| E9 | `@@ -2025…` segments-print pointer-arithmetic fix (`+` → `<<`) | O (`d6474e9`) | RB | was UB/OOB read; sane-input output now prints the true count |
| E10 | `@@ -2067…` KNN loop bounded by found count (`k < nn_indices.size()`) | O (`d6474e9`) | RB | segfault fix (Juglet piece 2, exit 139); identical on clouds ≥20 pts; 1.8mm gate unchanged. Previously masked by ≥30-pt clamp inflation |
| E11 | `@@ -3401…` append fracture patch rims as extra Breakline_0 segments (Breakline_0 only) | O (`734f27f`, `ecd610d`) | DM | 16 "ours, no paper basis" (patch-rim appending, +4 pairs 11→15/15). No paper step emits fracture rims. 30-pt floor (first try 8 let fragments through — caught by reading the log) |
| E12 | `@@ -3629…` main(): skip pieces with missing Surface files (loud) + T04 interior-first vote block | O (`565d9e0` guard; `4513f00`,`054a697` vote) | RB (guard) + PM (vote) | Guard: missing surfaces now EXPECTED output, skip loudly. Vote: paper L160 (both configurations, max satisfying wins) + 16-known ours-only caveats: 5mm eps, ≥10% size guard, ≥2.0 margin (provisional, 8 sherds) |

### File 2: `original_nurbs_preprocessing/mesh_processing_headless.cpp`
(8 hunks)

| # | Hunk (`@@`) | Layer | Class | Ticket / paper-line |
|---|---|---|---|---|
| M1 | `@@ -14,6 +14,7 @@` `#include <pcl/kdtree/kdtree_flann.h>` | O (`734f27f`) | IN | include for M3 only |
| M2 | `@@ -655…` `setClusterTolerance(2)` → `1.5` | O (`734f27f`) | DM | Upstream/cluster stage is paper-silent (no Euclidean tolerance in §IV-B1). Measured laptop: 2.0 fuses unclustered to 1426+1+1 on Pot_A piece 2; 1.5 yields 64 clusters, top six 1100+ pts; per-patch rims reach 2-4/2-5 seams by distance |
| M3 | `@@ -1128…` persist decorative rims (`Decorative_<t>.pcd`, mesh normals via 1-NN) instead of dropping | O (`c5643c4`, `734f27f`) | DM | Upstream computed and dropped them (third such dead end). Paper L155 notes decorative separation; no paper step routes fracture rims to the breakline. Additive: no existing output changes. xyz-only fallback logged |
| M4+M5 | `@@ -1348…` + `@@ -1472…` `mergeClusters` convergence loop (cap 10, per-pass log; criteria UNCHANGED) | O (`223108e`, `7e290d3`, `457e097`, `05f4fea`) | PM | 16 dev 7, now FIXED. Paper L153 "repeats until no further merges are possible". Measured no-op: Pot_A gate-identical, Juglet rerun confirms second pass merges nothing |
| M6 | `@@ -1779…` save raw pre-fit clusters (`tmpSurfaceCluster_Raw_*.ply`) | O (`8b17591`) | RB | diagnostic writes beside fitted outputs; separates split-loss from fit-inset for ticket 15 |
| M7 | `@@ -1854…` retry-loop `break` removed (single-cluster result retries loosened, ≤30) | O (`565d9e0`) | RB | Upstream loop's evident purpose; the break caused stale-temp inheritance (Juglet 3/9 carried 2/8's surfaces byte-identically). First-try-success path unchanged |
| M8 | `@@ -2095…` stale temp-surface cleanup before segmenting (4 fixed names) | O (`565d9e0`) | RB | no-op on clean runs; converts silent inheritance into loud missing output with the copy-time exists-check |

### File 3: ours-via-vendoring (in `3095064` baseline, attributed by patch file)

| # | Content (patch → marker verified in HEAD) | Layer | Class | Ticket / note |
|---|---|---|---|---|
| V1 | mm sphere-marching radii (`0.015/0.010/0.005` → `15.0/10.0/5.0`; floor `0.0005` → `0.5`; mm log line) — `juglet_edgeline_sphereradii.patch`, `juglet_edgeline_spheremin.patch` | V (ticket 02, `f5db0cd`) | DM | Cluster stage is paper-silent (no sphere-marching in §IV-B1); differs from upstream meters-assumed behavior. Unit-correctness: old radii read as sub-micron → empty boundary → `writeASCII: no data` abort (Juglet pieces 1–2). Patch notes "also changes Pot_A" |
| V2 | bbox-sheet boundary radius (mm, 6×spacing, [1,15]) + shared `g_boundary_radius_mm` + outlier radius reuse (×8/6, [2,20]) + 3/6 neighbors — `juglet_boundary_radius.patch` | V (ticket 02 / Step-1, `3278653` era) | DM | Same reference as V1. Old form pinned radius at the 15mm clamp then read 0.015 as 0.015mm → no neighbors ever found. E7 (T05) later reuses this radius through the shared seam |
| V3 | no write-convert (`convertToMM=false` at CompleteBreakline write) — `juglet_edgeline_nowriteconvert.patch` | V (ticket 02, `f5db0cd`) | DM | ×1000 write bug on an already-mm cloud. Unit-correctness vs upstream |
| V4 | single-file argv filter honoring (`specific_mesh_file` substring match) — `juglet_mesh_filter.patch` | V (Step-1, `d5b1b3b` era) | RB | previously no-op fall-through; full-pot runs (no argv) unchanged; enables per-piece reruns |
| V5 | `SFS_SMOOTHNESS_DEG` / `SFS_CURVATURE_THRESH` env tuning, Nov-2025 defaults kept — `juglet_mesh_thresholds.patch` | V (Step-1) | RB | defaults preserve behavior; consumed by ticket-12 sweeps (default optimal, both directions hurt or crash) |
| V6 | `[GROW-DIAG]` growing-input diagnostics — `juglet_mesh_diag.patch` (`dafacd5`) | V (Step-1) | RB | stdout only (HEAD `:1751`,`:1775`) |
| V0 | walk K=2 (`SFS_WALK_K_LOCAL`) — `juglet_edgeline_walkk_headless.patch` | V, REFUTED (`92f9712`) | — | **absent** from source (verified: no marker in HEAD; adaptive K stands). Patch file kept as record only. 16 dev 2 unaffected |

### File 4: `CMakeLists.txt` (root) vs `original_nurbs_preprocessing/CMakeLists.txt`

- Root `CMakeLists.txt` (upstream→HEAD: `cmake_minimum_required` 3.1→3.5,
  `tiny_obj_loader` include dir, headless/legacy targets, `ObjToPcd`): all
  **C**, untouched by our tickets (no `3095064..HEAD` hunk). IN.
- Vendored `CMakeLists.txt` (`3095064..HEAD`, +84/−1): T01 ordering TU +
  CTest seam (7 tests, 3 known-broken via DISABLED property only),
  T04/T05/T11/T14 `target_sources` wiring. **IN** (wiring + tests; the
  behavior lives in the classified hunks above). Commits `3ce060e`
  series, `4513f00`, `17a3b7f`, `495523a`, `734f27f`, `2716475`,
  `08584ff`.

### File 5: `data_path.h` (root) and `original_nurbs_preprocessing/data_path.h`

- Both: `../`-relative → container-relative paths, `POT_NAME` /
  `NURBS_OUTPUT_BASE` env routing. All **C** (no our-ticket hunk in
  either). IN. (Ticket 16 gap B — `Surface_F` expected by name in the
  *assembly* repo, never produced here — is unchanged by our tickets:
  the mesh stage still emits two named walls with the fracture zone in
  `unclustered.ply`, which is exactly what T14 mines.)

### File 6: `AxisExtraction/*.m`

- 26 of 28 name-shared files byte-identical upstream ↔ vendored.
  The 2 differences (`compute_cao_error.m` cross-product replication;
  `run_potsac.m` integer-half fix + adaptive POTSAC step): **C**
  (`ff40fc9`). Per-paper note: the adaptive step changes *which points*
  are sampled (fixed 1:10 → density step), not the solver; ticket 16's
  MATLAB addendum stands.
- 9 extra `.m` files (cluster NURBS helpers: `refine_axis.m`, `tmult.m`,
  `read_surfaces_nurbs.m`, `extract_axis_nurbs.m`,
  `extract_all_nurbs_pieces.m`, `extract_and_compare_results.m`,
  `generate_final_comparison.m`, `load_root_dir.m`,
  `catch_actual_error.m`): **C**. IN.
- Root `AxisExtraction/` (56 entries incl. 8 `Pot_A_*_NURBS_Axis.xyz`
  outputs + debug/verify scripts) vs vendored `AxisExtraction/` (37):
  34 identical, 3 differ (`run_potsac.m`, `extract_axis.m`,
  `read_surfaces.m`) — the root copies are the newer cluster state and
  the live ones: md5s re-verified at audit time against ticket 16's pins
  (`extract_axis` `cc4fa5af`, `read_surfaces` `443e6355`, `run_potsac`
  `7822954e`, `compute_pottmann_axis` `b8630781`,
  `compute_axis_of_symmetry` `37eff04b`, `refine_axis` `1f8d2d16` — all
  match). See unattributed list, item A1, for the vendored-side staleness
  disposition.

### File 7: root duplicate `.cpp` files (stale, unbuilt)

`edgeline_extraction_headless.cpp`, `mesh_processing_headless.cpp`,
`edgeline_extraction.cpp` (+ `_backup`, `_curvature_fixed`) at repo root
are cluster-era copies (last touched `6e39837` and earlier), hash-distinct
from the live vendored files, and compiled by no current script
(`build_all.sh` builds `original_nurbs_preprocessing/build` only).
**C**, IN (dead weight; not removed in this audit ticket — removal is a
one-line future commit, flagged not done).

## New-file inventory (ours)

| File | Ticket | What / paper relation |
|---|---|---|
| `original_nurbs_preprocessing/edge_line_ordering.{h,cpp}` | 01 | NN-walk extracted verbatim (adaptive K kept) so tests compile production code. RB (see E4). Header documents the measured defect (59→9 pts, 6% rim) and corrects two of our own misquotes |
| `original_nurbs_preprocessing/surface_classify.{h,cpp}` + `ticket04_interior_first.cpp` | 04 | Paper L160 classifier (ray/axis closest-approach, both configurations, max-wins) + file-exchange glue. PM, with 16-known ours-only caveats (5mm eps, guards). Self-copy bug history (`054a697`) inside |
| `original_nurbs_preprocessing/boundary_filter.{h,cpp}` | 05 | Paper L164 filter as a shared seam (production = test). PM. `keepOrganized=false` so removals vanish (NaNs would poison the walk) |
| `original_nurbs_preprocessing/ticket14_patch_rims.cpp` | 14 | Fracture-rim appender (30-pt floor, normals required, loud skips). DM (see E11/M3) |
| `original_nurbs_preprocessing/boundary_radius_override.h` + `boundary_radius_hook.cpp` | 11 | Inert-unless-set diagnostic hook. RB (see E5) |
| `original_nurbs_preprocessing/tests/` (3 test `.cpp`, `tests/README.md`, `tests/data/juglet_boundary_59.txt`) | 01/04/05 | CTest seam: ordering (2 pass + 3 DISABLED-known-broken), classify (3 pass), filter (2 pass). IN. Fixture is worst-of-18 real Juglet cloud (ticket 08 scope correction recorded in README) |
| `scripts/diagnostics/*.py` (`verify_extraction`, `diagnose_walk`, `compare_pot_boundary_clouds`, …) | 01/08 | Mechanical verification (move-identity, coverage/MST metrics). IN |
| `build_all.sh`, `build_seam.sh`, `build_seam_inner.sh`, `build_ticket04.sh`, `build_with_hook.sh`, `run_ticket0{1,4}_*.sh`, `run_pota_fresh*.sh`, `run_*sweep*.sh`, `run_*ablation*.sh`, `run_union_experiment.sh`, `capture_piece2_boundary.sh`, `tidy_verify.sbatch`, `vendor_check.sbatch` | 01–17 | Build/run/gate scripts. IN (extent gate in `run_juglet_preprocessing.sbatch` is an output gate, not source) |
| `patches/juglet_*.patch` (8 files; walk-K refuted) | 02/Step-1 | Applied-state record for the vendored baseline; no longer applied by any live script against tracked source (old sbatch patch loops targeted the untracked nested tree). IN |
| `original_nurbs_preprocessing/{edgeline_extraction,mesh_processing}.cpp`, `_backup`, `_curvature_fixed`, `tools/`, `tiny_obj_loader.h`, `.m` debug scripts at root | — | Vendored/cluster reference copies, not compiled by live scripts. C, IN |

## Ticket-16 cross-check

Every paper-behavior hunk above traces to a 16-known deviation or a
16-known ours-only addition, with three *status changes* (fixes landed
after 16) and one *scope note*:

- 16 dev 1 (descriptors): corrected by 16 itself to downstream-with-
  different-smoothing (assembly repo). No preprocessing hunk touches it. ✓
- 16 dev 2 (no CCW vote): unchanged — E4 moves the walk, nobody
  reimplements the vote; 16's accept-stance (2026-09-30, unspecified
  algorithm) stands. ✓
- 16 dev 3 (dead filter): **FIXED by E7** post-16. ✓ (16 needs no edit,
  but its deviation list is stale here — lead may append.)
- 16 dev 4 (2.0mm-cap resampling): **FIXED by E2+E3** post-16 (default
  1.9, true equidistant). ✓ same note.
- 16 dev 5 (rim criterion): unchanged, upstream-inherited (0.12 gate is
  upstream `:2382`). ✓
- 16 dev 6 (region params): unchanged, upstream-inherited + ticket-12
  measured-optimal. ✓
- 16 dev 7 (single-pass merge): **FIXED by M4+M5** post-16 (converges;
  measured no-op both pots). ✓ same note.
- 16 "ours, no paper basis": T04 guards (E12 — 16 already records the
  caveats), T14 patch rims (E11/M2/M3), Euclidean path/adaptive
  K/radius/clamps (C/V-layer, 16 lists them). One new detail 16 never
  pinned: the **30-point** patch-rim floor vs paper L329's **50-point**
  fragment exclusion. Not a contradiction: L329 excludes fragments from
  *datasets*; T14 *adds* ≥30-pt rims as extra segments without touching
  existing ones. Recorded here so the next reader does not have to
  re-derive it.
- 16 gaps A (base compiled out) / B (`Surface_F` never produced):
  assembly-repo scope; preprocessing side unchanged (File 5 note). ✓
- Cross-check findings (16-unknown, therefore findings per the ticket —
  both disposed here, no new ticket): **C1.** V1–V3 mm-unit fixes are
  ticketed (02/Step-1, SOURCE_ANCHOR) and measured (Juglet aborts) but
  invisible to 16, whose audit never names the sphere-marching/boundary
  stages. Accepted here: paper-silent cluster stages, unit-correctness,
  predates 16. **C2.** Devs 3/4/7 fixes postdate 16 — informational;
  16's list is stale in exactly these three places.

## Unattributed list

- **A1 (accepted with reason, not re-ticketed):** the *vendored*
  `original_nurbs_preprocessing/AxisExtraction/{run_potsac,extract_axis,read_surfaces}.m`
  are an older snapshot than the live root `AxisExtraction/` copies
  (missing the adaptive POTSAC step, SFS-format save block, `Pot_`
  naming + equal-count truncation). Attributed (vendoring snapshot
  `3095064` of the then-nested tree), divergent by staleness, harmless:
  the root copies are what ticket 16 pinned (md5s re-verified above) and
  what the MATLAB jobs consume; nothing builds against the vendored
  copies. If the vendored tree is ever built from, re-sync these three
  files first.
- No other unattributed hunk was found: every `3095064..HEAD` source
  hunk maps to a ticket commit above; every baseline-embedded ours hunk
  maps to a patch file; everything else is upstream or cluster per the
  section above. The E6 `SFS-T07` comment label (commit is T17-era
  `4511415`) is a one-word mislabel, not an attribution gap — left for
  the owning ticket, not filed.

## Numbers for the lead

20 our-hunks in the two pipeline files (12 edge + 8 mesh): PM 4
(E7, E12-vote, M4, M5), DM 5 (E2, E3, E11, M2, M3), RB 9
(E4, E5, E6, E8, E9, E10, M6, M7, M8), IN 2 (E1, M1).
Ours-via-vendoring: DM 3 items (V1, V2, V3), RB 3 (V4, V5, V6),
1 refuted-absent (V0). New-file units: PM 2 (vote, filter), DM 1
(patch-rim appender), RB 1 (T11 hook), IN (tests, scripts, CMake wiring,
patch records). Cluster layer: summarized via Nov-2025 doc, re-verified
at 6 upstream-anchored points (walk K=50, tolerance comment, 0.12 gate,
4.5/1.5 defaults, `substr(0,14)`, Euclidean/decorative/retry presence).
