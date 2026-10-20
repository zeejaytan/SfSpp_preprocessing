# Revert the LIVE root copies (edge + mesh headless) to pristine + harness

GOAL: PRISTINE LIVE BINARIES. The review (2026-10-20) showed the B/M revert
surgery covered the vendored copies under original_nurbs_preprocessing/, but the
binaries the pipeline actually builds run from ROOT copies that still carry fork
behaviour. Bring the two live files back to author behaviour with the same keeps.

**Answers:** E1

**Blocked by:** none. Base is pristine-dchain@6da985d. dchain-port (206, done) touches
disjoint .scratch-only paths and rebases trivially afterwards.

**Status:** done

## Why these two files

Root CMakeLists builds EdgeLineExtractionHeadless from
`edgeline_extraction_headless.cpp` (named in 109 job scripts) and
MeshPreprocessingHeadless from `mesh_processing_headless.cpp` (72 job scripts).
Marker grep (2026-10-20): B-markers 4-6 hits in the live edge copies, M-markers
26 hits in the live mesh; live mesh differs from the reverted vendored copy by
312 changed lines. The vendored copies build only through the side makefile in
original_nurbs_preprocessing/ and are not what the main pipeline calls.

## Ground truth (spec)

The reverted vendored copies ARE the spec -- do not re-derive behaviour:
- `original_nurbs_preprocessing/edgeline_extraction.cpp` @0da8891 (B1-B10 reverted)
- `original_nurbs_preprocessing/mesh_processing_headless.cpp` @6da985d (M-reverts)

For each live file: diff it against the upstream pin (d5ee686) and against the
reverted vendored copy. Every behaviour delta you find in the live file that is
absent from the reverted copy gets reverted; every keep-class below stays.

## Behaviour to revert (orientation -- the reverted copies are authoritative)

Edge (B1-B10): B1 walk guards/foundK/pick/bound; B2 64-pt empty seeding;
B3 disabled PLY snap load + KD map; B4 curvature zeroing; B5 small-input guard;
B6 KNN found-bound; B7 diag scale-up + de-normalize; B8 CompleteBreakline XYZ-only
save; B9 SOR 50 (pristine 9); B10 empty synthesis. Harness kept in the vendored
revert: viz #if0s, DBG prints, custom segment-header PCD writer + guarded rename,
N-min guard.

Mesh (M1/M2/M4/M5/M6/boundary/dyn-reg): M1 mm-x1000 + header inject (dead -- all
callers pass false -- but headers still inject on basePath files: drop conversion,
keep the rest per 6da985d); M2 adaptive downsample loop (fixed samplingRadius);
M4 adaptive CGAL-KNN (nb=5); M5 PCL curvature block (deleted); M6 cluster retry
sign flip + caps + dyn params (pristine -=2 incl. theshold typo; maxIterations cap
kept as hang insurance); boundary setRadiusSearch(3) with mismatch/empty guards kept
per M8; dyn-reg minCluster/noOfNeighbours. Keeps: M3 CGAL::IO paths, M7 ASCII PLYs,
M8 NaN/empty guards, prints, headless includes/fwd-decls, Juglet argv/env/single-file main.

## Keeps (stay in the live files)

Same keep classes as the vendored surgery, PLUS each file's headless main
(argv/env/single-file entry -- the reason these files exist as separate copies).
MATLAB axes are as-is per standing user decision -- do not touch AxisExtraction/.
data_path.h POT_NAME env glue and .gitignore stay -- do not touch.

## Boundary -- do NOT touch

- Main worktree uncommitted work (user's 204 edit) and .scratch/pota-repro/issues/204*.
- The .wt-pristine-dchain and .wt-dchain-port worktrees; the dchain-port branch.
- Any .m file, data_path.h, CMakeLists, sbatches, or .scratch evidence.
- Only the two root files may change. Work on a NEW branch `pristine-dchain-live`
  cut from pristine-dchain@6da985d with a NEW worktree under .scratch/ (new name).

## Practical notes (paid for twice already)

- The read tool hides leading tabs: verify every edit site with `cat -A` first;
  old_strings must carry exact tabs/spaces or the edit silently misses.
- Both files are CRLF: compare with --strip-trailing-cr (or -b); CRLF is the repo
  convention, not a finding -- keep it.
- No C++ toolchain on the laptop: no compile check possible. State preserved by
diff discipline (see acceptance), build check belongs to the E2E follow-up.

## Acceptance

1. Zero B-markers in edgeline_extraction_headless.cpp, zero M-markers
   (ADAPTIVE/dyn/convertToMM/boundary_radius_mm/curv_k) in mesh_processing_headless.cpp.
2. Normalized diff of each file vs the d5ee686 pin contains ONLY keeps
   (keep classes above + headless main); behaviour regions (e.g. getKNN/getCurvature
   bodies) identical to the reverted vendored copies.
3. One step per file, one commit per file, pushed to origin/pristine-dchain-live.
4. This ticket flipped to results-in with branch/commits/marker-greps/keep-list.

Report back: branch + commit hashes, per-file marker greps (before/after),
normalized-diff keep-class list vs pin, anything you deliberately kept and why.

## Comments (worker 2026-10-20, surgery on pristine-dchain-live)

Branch: pristine-dchain-live (from pristine-dchain@6da985d, origin fetched first).
Worktree: .scratch/.wt-live-revert (new; .wt-pristine-dchain/.wt-dchain-port untouched).
Commits (one file each, pushed to origin/pristine-dchain-live):
- 7ffede4 mesh_processing_headless.cpp (84+/227-)
- c617fd8 edgeline_extraction_headless.cpp (205+/780-)
No compiler on laptop; guarantee is diff discipline. CRLF kept (all files fully CRLF).

Marker greps, live files BEFORE -> AFTER (grep -c -E):
- mesh: ADAPTIVE 11->0; dynMinCluster|dynK 4->0; convertToMM 4->0;
  boundary_radius_mm 5->0; curv_k 3->0.
- edge: convertToMM 4->0; ADAPTIVE 18->0; adaptiveDensifyBreakline 3->0;
  robust-loader family (load_ply_pointnormals_robust|is_valid_normals|
  estimate_normals_from_xyz|load_pointnormals_from_cleaned_surface) 10->0;
  transposeInPlace 1->0; sensitivity_divisor 10->0; BUG FIX 2->0;
  SEGMENT FILTER|SEGMENT SAFETY|RIM DETECTION SAFETY 10->0 (FRACTURE SURFACE 0);
  geometric-curvature 2->0; getPointsOnFracturedSurface call 1->0; Surface_F 3->0;
  classic B1-B10 literals (foundK|ply_ok|K_NEIGH|compute_diag|empty-synthesis) 0->0.
- Residual diff vs reverted vendored copies: mesh = 1 line (#include <iomanip> keep);
  edge = 33 strict hunks / 30 with -b, every one classified below as keep/deliberate.
- Behaviour bodies: mesh getKNN/getCurvature byte-identical to reverted copy;
  edge sphere loop (r=1.8, single pass, i++), K=50, radius 4/2.5/6, fixed /4.0
  findPeaks, void detectSeparateLineSegments, 2-arg PCD writer call restored.
  Braces balance in both files; no missing/extra toplevel functions (only #if0
  viewer lines differ, a grep artefact); zero return-value remnants.
- B-sites already pristine at base, verified untouched: B2 64-seed, B3 PLY snap,
  B4 curvature-zero, B5 small-guard, B6 KNN-bound, B7 diag-scale, B8 full-cloud
  save, B9 SOR=9, B10 synthesis all absent/already-pristine in the live copy.
  The live fork drift was the ADAPTIVE family + items above, all reverted.

Deliberately kept + why:
- Container paths (Dataset/Axes/, Dataset/Breaklines/, axesFolder, disabled
  create_directories; vendored C:\Users\cpp hardcode NOT restored): environment
  harness, not algorithm behaviour; vendored paths are stale there.
- copy+remove instead of vendored exists-guarded rename: EXDEV-safe superset of
  the guarded-rename keep; rename would throw cross-device in container.
- Explicit ASCII PLY flags (, false) + prints: identical to PCL default; prints
  are keep-class. Same at breakLineFromConcaveHull site.
- Dead peakData_index decl/pushes (12 refs): behaviour-neutral dead stores; only
  the compile-error (return value in void fn) removed with the void revert.
- peakTriggerLevel NOT transplanted: declared-but-unused in the spec itself.
- <sstream>/<iomanip>/obj_io includes, viz-disable comment style, whitespace and
  standalone DBG prints: harmless harness cosmetics, no churn.
- Method: mesh = sync-to-vendored + iomanip (one insert); edge = 65 validated
  scripted ops (check-then-apply, bottom-up) + writer repositioned before its
  helpers to match spec order. One mid-course restore (insert/delete spanning
  bug caught by the check phase and post-diff audit, redone clean).

Risks for lead/E2E follow-up:
- BUG FIX #1 call removed per spec (fracture-surface populating call absent from
  spec): if E2E shows empty fracture outputs, that needs its own ticket.
- breaklinesDir create_directories stays disabled (container path kept): fails
  only if the dir is missing in-container; consider pre-creating in the image.
- Build check not possible here; belongs to E2E.

## Comments (lead, 2026-10-20 -- ACCEPTED, verdict PASS)

Independently verified on origin/pristine-dchain-live: 2 commits (7ffede4 mesh,
c617fd8 edge), exactly 2 files changed (289+/1007-). All behaviour markers zero
in both files (clean re-grep, not the worker's). Mesh live file differs from the
6da985d spec by exactly one line: added `#include <iomanip>` (headless-main
printing keep). Edge bodies spot-checked vs 0da8891 spec: findPeaks 2/2, sphere
1.8 2/2, detectSeparate call site identical (extra mention is a DBG print keep).
The 3 E2E risks above are carried into ticket 208. Next: land this ticket, delete
original_nurbs_preprocessing/ per user decision (single source of truth), merge
dchain-port evidence onto the cleaned line.

