# Ticket 248: port the paper's K-D tree filter (outlier removal before vote-order) and re-test the P03-Bl1 exam

**What to build:** the paper's missing K-D tree outlier-removal stage, wired in front of the 247 vote-order arm, so the P03-Bl1 braid bag is filtered to one loop before voting — then re-extract + re-score the exam and guards. Ends at re-extract + score; no reseat/assembly; nothing committed to main.

**Answers:** E1

**Blocked by:** Ticket 247 (vote arm + SPLIT verdict; vote247.diff is the base).

**Status:** ready-for-human
**Working in:** subagent session-61c820f6 (2026-10-22)

- [ ] Paper K-D tree filter + corner criteria quoted with file:line before any build
- [ ] Filter ported in edge stage ONLY (edgeline_extraction_headless.cpp + call sites), greedy intact, default OFF (SFS_VOTE_ORDER OFF default; new SFS_KD_FILTER OFF default)
- [ ] P03-Bl1 exam at bar (med<2mm, cov>=90% vs author, zero jumps>10mm, walk order verified, lane stays ONE loop)
- [ ] Guards hold (P03-Bl0 ~0.58-0.72/97.8-100 class unchanged-or-better, P01 both lanes at/above 247-CTL bar, P22 fork intact = 239/244 class) else STOP + report
- [ ] Evidence in ticket Comments + Status results-in; diff left as vote248-filter.diff pattern (no main commit)

## Paper criteria (quoted BEFORE build — sfspp-2502.13986v1.md)

K-D tree filter (file:line C:/PR/papers/text/sfspp-2502.13986v1.md:164):
"Using a K-D tree-based search, points near the edge line are identified and filtered to remove noise and outliers."
- Population: points near the edge line (K-D tree search around the B-spline-smoothed edge line).
- Removed: noise and outliers.
- Threshold: NONE in the paper — no radius, count, distance, or density number is given. Any numeric gate is a stated surrogate, not the paper.

Corner segmentation (same line 164): "we segment the edge line based on corners detected by analyzing peaks in the distribution of distance scores, which measure the deviation of each point from its local linear trend."
- No numeric window/threshold in the paper (247 stated assumption: chord +/-8 pts, peak iff score > max(2.0mm, 3x median), corners LOGGED ONLY — carried over unchanged).

Resample/order anchors (same line 164): resample to equidistant d=1.9mm (empirically optimized, the only numeric constant); reorder counter-clockwise using normals + voting (Fig. 6, file:line :166 — "Fig. 6: Improved edge line detection on 3D object meshes. B-Spline fitting method (red) extracts edge lines closer to the real edge line, demonstrating enhanced accuracy over a wider area compared to the previous approach (blue)").

## Boundary

- Fresh worktree of origin/main + fresh Spartan copy. Edge stage ONLY (edgeline_extraction_headless.cpp and call sites; 247 vote code behind SFS_VOTE_ORDER).
- Mesh/splitter/classify/assembly untouched. Main worktree (user 204-edit) off limits except this ticket file.
- Diff left uncommitted as vote248-filter.diff pattern like 247 (vote247.diff lives in C:/PR/SfSpp_preprocessing-247/vote247.diff).

## Constraints

- Spartan: git pull --ff-only first, STOP on divergence; same build node as 244/245/247 for md5 comparisons.
- MSYS2: export MSYS2_ARG_CONV_EXCL='*' in every ops_bash (colon rev:path mangling).
- Source-changing build => rebuild + verify binary md5.
- Pot images: never similar colours for different things (no renders this ticket — numeric exam only).

## Required evidence to report

Quoted filter + corner criteria with file:line; filter diff summary; P03 both-lane + P22/P01 scores (med/cov/jumps, turnSum diagnostic per 247); guard scores with numbers; job IDs + sacct State/ExitCode; binary/edge md5s; Status results-in + Comments appended; self-contained completion message. Judgement stays with lead: stage evidence and STOP — propose no repair beyond this ticket, commit nothing to main.

## Comments (worker, 2026-10-22 — setup + build submitted)

Paper filter quoted BEFORE build (sfspp-2502.13986v1.md:164): "Using a K-D tree-based search, points near the edge line are identified and filtered to remove noise and outliers." Population = points near the edge line; removed = noise/outliers; NO numeric gate in the paper. Corner rule (same line): peaks in distance-score distribution (deviation from local linear trend), no window/threshold. Fig.6 caption :166 recorded in ticket body.

Code map (edgeline_extraction_headless.cpp @4887348, 3421 lines): PCL boundary r=4mm (:795) + face-veto -> boundaryCloud; K=1 snap to unclusteredPoints (:964-982) -> boundaryCloud_Improved; RadiusOutlierRemoval r=2.5/min6 (:989-996) -> cloud_filtered DIAGNOSTIC ONLY (POTA-212 deleted reload); splitRimVsStepRing_213 -> cloud_rimIn; greedy COMP_GAP 5.0/GUARD 6.0 (:729-730). Vote fn getPointsInSequence_Vote247 (:552-716, already in 4887348 tree — 2d99306 is its ancestor but carried no cpp change; vote code arrived as uncommitted vote247.diff, verified via git show 4887348: = 0 VOTE markers).

Filter edit (laptop C:/PR/SfSpp_preprocessing-248, uncommitted): SFS_KD_FILTER gate inside Vote247 BEFORE comp-BFS — reuses committed ROR(2.5mm/6) on vote input cloud_rimIn, [KD-248] kept/dropped log; greedy path untouched; default OFF. No invented thresholds.

Spartan: /data/gpfs/projects/punim2657/sfs-vote-248 cloned from sfs-vote-247, origin repointed to github (clone inherited local origin), checkout 4887348 clean, vote248-filter.diff (233 lines, +207/-1 = vote base + filter) uploaded + applied. Blob hash 6cc54734 matches laptop exactly (raw md5s differ on laptop CRLF only — autocrlf=true; content identical). Edge cpp md5 (Spartan LF): 7aa8177694fdb6bbf4e323afc1861467.

Jobs: build248 submitted as 33689658 (HEAD-pin 4887348 + FILTER-present gate, build-248/). Run plan run248.sbatch: pieces 03/22/01 from pota245_P03_RST/pota244_P22_RST/pota239_paper_P01 x arms CTL(0,0)/VOTE(1,0)/KDF(1,1). Scorer stats248.py = stats247.py with pota248 trees + KDF arm.

## Comments (worker, 2026-10-22 — RESULTS, exam FAILED, STOP)

Run 33689678 COMPLETED 0:0 (bm172). VOTE arm replicates 247b to the decimal (P03-Bl1 8.69/21j, P22-Bl0 4.79/38j, P22-Bl1 4.43/17j) — replication gate passes, so the KDF delta below is attributable to the filter, not to drift.

Scores (lanescore med/cov<2mm/jumps>10mm vs author GT):
- P03-Bl1 EXAM: CTL 0.98/52.8/1j | VOTE 8.69/11.0/21j | KDF 0.99/78.2/3j. Filter converts the 4328-pt braid scribble into a 403-pt coherent loop, but 3 chord jumps (maxjump 137.9) remain and cov 78.2 < 90. Bar asks med<2 + cov>=90 + zero jumps + ONE loop: FAIL (2 of 4). STOP per ticket.
- P03-Bl0 guard: CTL 0.72/97.8/0j | VOTE 0.58/100/0j | KDF 0.86/67.2/0j, max 1.2->41.2. The filter+comp-BFS (kept 306/668, comp 2 of 3) cut a clean loop's coverage from 100 to 67. Guard REGRESSED on the clean loop — committed ROR(2.5/6) + 5mm comp-BFS is too aggressive for dense rims, not just braids.
- P22-Bl0: VOTE 4.79/14.4/38j -> KDF 4.87/14.7/37j (filter ~no-op, kept 484/490). P22-Bl1: VOTE 4.43/15.8/17j -> KDF 2.40/41.8/2j (better, still FAIL). Fork intact = still failing, as in 239/244 class.
- P01: VOTE matches/betters CTL (Bl0 0.72/98.8/0j, Bl1 0.93/95.7/0j) — guard holds via VOTE arm. KDF arm for P01 is VOID (see crash note): scored values equal CTL only because the scored PCDs are byte-identical to the source tree (cmp SAME-AS-SOURCE, DIFFER-FROM-CTL).

Crash note (KDF-only, single occurrence): P01-KDF segfaulted — run log line "Segmentation fault (core dumped)", run .out "EDGE-EXIT-139 P01 KDF", only 1 of 2 fragments processed (vote block itself completed: kept 20/435 -> chain 20 -> resampled 17, L=31.7mm side lane; crash came later in "Detecting separate line segments"). No other arm/segfault in 8 other lanes. Not re-run (ticket: no re-runs); lead to decide whether a crash-hunt is a new ticket. Honest possibility it is filter-data-dependent (20-pt chain into downstream code that never saw tiny clouds) rather than flake — either way it is KDF-arm-only evidence.

Mechanism note for lead: the 247b BFS prefilter (5.0mm, kept, no-op on singles) becomes the active cutter under KDF — P03-Bl0 clean loop split into 3 comps, Bl1 braid into 5 comps (kept 433/1082, comp 0 of 5). The "filter" that moved the needle is arguably the comp-BFS, not the ROR (P22-Bl0 ROR kept 484/490 yet score unchanged). Paper gives no numeric gate, so no compliant fix exists without inventing one — STOP stands.

Overlays (author black / CTL blue #0072B2 / VOTE vermillion #D55E00 / KDF green #009E73; 3D + X-Y/X-Z/Y-Z, equal aspect; KDF series added to the requested three since the data was free and it is the exam arm):
- C:/PR/SfSpp_preprocessing-248/artifacts/pota248/P03_Bl1.png (exam: green coherent loop with 3 chord shortcuts vs vermillion scribble; viewed, matches numbers)
- C:/PR/SfSpp_preprocessing-248/artifacts/pota248/P03_Bl0.png
- C:/PR/SfSpp_preprocessing-248/artifacts/pota248/P22_Bl0.png
- C:/PR/SfSpp_preprocessing-248/artifacts/pota248/P22_Bl1.png
(Spartan masters: /data/gpfs/projects/punim2657/sfs-vote-248/overlays/*.png, gen overlay248.py; scorer stats248.py alongside.)

Diff: vote248-filter.diff pattern kept uncommitted on laptop worktree C:/PR/SfSpp_preprocessing-248 (vote base + KD-filter, +207/-1 vs 4887348). Nothing pushed, main untouched.

## Comments (worker, 2026-10-22 — )
