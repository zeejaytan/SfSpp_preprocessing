# 12: Reverse-engineered axle finder (fit 01–04, prove on 05–08)

**What to build:** our finder, not their patch — reverse-engineered from three sources: the paper's method (§IV-B2), the shipped Pot A inputs+axles as the answer key, and the pristine code as clues. Starts from 09's working scaffold; closes the 1/8 → 8/8 gap with new variables 09 named.

**Answers:** E1

**Blocked by:** 09-pristine-axle-repair (kill verdict above).

**Status:** results-in

## Comments (worker, 2026-10-15)

**Verdict: fit 2/4 (P02, P03) + frozen validation 0/4 = 2/8 overall** (09 baseline 1/8).
Direction is solved everywhere the geometry allows (fit pieces all ≤1.2°, P05 0.48°);
position hits a ~2-3mm material floor (P01 2.42, P04 3.03, P05 2.77 — all direction-PASS).
P06 direction miss (8.19°/24.7mm) and multi-axis 07 (nearest axis 2.90°/1.87mm, other two
missed 56-59° off) / 08 (both missed) stay open. Kill branch not taken: the three variables
moved fit 1/4 (V1) → 2/4 (V3) and fixed direction everywhere fittable — but the ticket bar
(8/8) is missed, and the evidence says why.

**Frozen finder** (`axle_finder/` in Spartan `/data/gpfs/projects/punim2657/Temp/potsac-p12-run/`,
staged at `.scratch/pota-repro/p12-stage/`): `af_find_all` = spatial split (voxel union-find,
eps 10mm, drop <300pt splinters) → per component: raw-GM vote (6-pt Pottmann solves =
pristine `compute_pottmann_axis` reused read-only, 6000 iters, seed 0) → orientation frozen
per surface (`af_orient`: REV iff reversed Cao error has lower GM sum) → fixed-orient Huber
W=1 LM refine (10% subsample, then full; scaffold `r3fix/refine_axis.m` + `r2fix/` repmat fix
reused) → sequential peel, winner by tight inlier count (|R|≤1, minfrac 10%, maxK 4) →
union → hard-IRLS x8 polish (`af_polish`, |R|≤1, Huber W=1) → dedup (distinct iff angle
>10° OR radial offset >2mm, x1.1 near-tie gate, max 6) → sort by inliers desc. Scorer:
09's `score_vs_shipped.m` (bar ≤5°/≤2mm radial). Shipped axles used ONLY for scoring and two
landscape probes (cost-at-shipped, refine-from-shipped) — never finder input. Pieces 05-08
untouched until V5 (run once, no changes after).

**V1 weighting (fit 1/4: P03).** Tried a normalized-angular cost (per-point fwd/rev softmin +
normal-confidence + surface balance, GM width w): D1 rank test looked great (shipped rank
1/200, job 33075324 COMPLETED) but pure-angular vote was catastrophic (P01 51°/159mm, job
33075523). D2 root cause (job 33075637): degenerate exploit — normals parallel to the true
axis make truth's angular residual noise-dominated, a spurious perpendicular axis wins by 6%;
raw-GM discriminates the same pair by +18%. Lesson: angular = right local shape, wrong global
shape. Staged raw-select + angular-refine destroys passes (P03 2.31°/0.78mm → 24.9° FAIL,
jobs 33075802/33075938/33076127): the per-point orientation softmin lets points game the
orientation, drifting into deeper spurious pockets; frozen weights don't help. Fix (V1e, job
33076317): freeze orientation per surface ONCE — unanimous S0→REV, S1→fwd on all fit pieces
at 1.5-2x margins — then refine raw residuals, Huber W=1. No drift anywhere; W∈{0.5,1,2}
flat, wider W worse for position. V1f refine-from-shipped probe (job 33076559): refinement
walks AWAY from the shipped axle on all 4 fit pieces → shipped is not a stationary point →
systematic 0.5-3mm position bias (routed: search for P02's start, V3 for bias).
Paper (§IV-B2) says: MLESAC + 6-pt Pottmann, top-10, 10° dedup by higher robustified cost,
10%-then-full refine, extended Cao–Mumford + trust region. Kept: 6-pt solves, GM-select vote,
10°/x1.1 dedup spirit, sub-then-full refine. Changed: orientation frozen per surface (the
paper's two-configuration test, done once), Huber-LM for trust-region (from scaffold),
winners ranked by inlier COUNT not GM sum (GM sum prefers compromise axes between true modes
— proven: on a synthetic 50/50 two-axis cloud the vote top-1000 are all 60-77° off truth,
job 33077336).

**V2 search + dedup.** 12/24-pt solves + 3000 iters don't beat 6-pt (equal sampling poverty,
job 33076970 FAILED-script/33077142 rerun: sprintf-recycling bug); 6-pt kept (better
pure-sample odds for multi-part data). Position-aware dedup (paper's direction-only rule
merges parallel-but-offset axes, killing multi-axis pieces): nset=1 on all fit singles (no
phantoms, job 33077142) and on peel (minfrac stop verified, jobs 33077892-33079037 with
script-bug FAILEDs 33077615/33077892/33078297/33078668: af_inliers matrix-sum, empty-set
scoring, kmeans output order — all fixed, reruns COMPLETED). Compromise trap documented:
direct peel on synthetic disjoint 50/50 returns nset=0 (job 33078297/33079037). Spatial split
`af_split` (job 33084770 COMPLETED): 1 component on all fit pieces at eps 5/10/20mm
(specificity), exact 2x18305 split on synthetic (sensitivity) → per-part fit recovers both
axes (0.65°/0.65°). Frozen assembly check V4 (job 33086913): fit 2/4 pattern, synth nset=2.
Connected multi-axis (shared-points/handle-type) is NOT testable on fit data — flagged as
open risk (realized in validation).

**V3 boundary/rim (fit 2/4: P02, P03).** Pristine has NO rim masking in the fit path:
`check_base_and_rim` is breakline/output-only and answer-dependent (`read_axis`), and neither
`run_potsac` nor `refine_axis` references rim/base — variable 3 as hypothesized doesn't exist
upstream. Hard-IRLS x8 polish (|R|≤1, thr=Huber W fixed a priori): P02 5.17→1.86 PASS,
monotone over 8 iters (job 33086235); P01/P04 frozen at floor through thr sweep {0.5,1,2}
(job 33086552; P01 thr=2.0 gives 2.00 — NOT adopted, no threshold-shopping). Half-split test
(job 33085834 FAILED-script/33086235 rerun): P01 halves disagree 8.34mm radially → the local
best-fit axis varies mm-scale across one fragment (handmade variation) → the ~2-3mm floor is
material-level (fragment-local truth ≠ full-pot shipped axis), not method noise. Scale
controls: uniform 1:10 downsample (07-scale counts, full span) → (0.68,2.60) ≈ full density —
point COUNT is irrelevant; ball patches at 07 scale → catastrophic (8°/41mm, near-flat
degenerate); thin slabs fail (8.5/4.5mm) → small pieces need 2D shape span, not just counts.

**Frozen validation V5 (job 33087310 COMPLETED 0:0, run once):**

| piece | nAns | nset | derr (°) | rerr (mm) | verdict |
|---|---|---|---|---|---|
| 05 | 1 | 1 | 0.48 | 2.77 | FAIL (material floor) |
| 06 | 1 | 1 | 8.19 | 24.73 | FAIL (direction — needs new ticket to diagnose) |
| 07 | 3 | 1 | 2.90 / 56.6 / 59.5 | 1.87 / 209 / 164 | FAIL (1 near, 2 missed) |
| 08 | 2 | 1 | 64.6 / 37.2 | 120 / 54 | FAIL (both missed) |

**For the session:** (1) P05/P01/P04 form a family — direction-right, 2.4-3.0mm off; if the
2mm bar is negotiable or a per-fragment bias term is modellable, they're done. (2) P06's
direction miss is the most decision-relevant failure (mid-size single-axis piece, should have
worked) — recommend a diagnosis ticket (base fragment? disjoint sub-parts? vote poverty?).
(3) 07/08 need connected-multi-axis machinery (shared-points modes, untestable on 01-04) or a
scale-span admission test (V3b says flat patches are unidentifiable — check whether 07/08 even
span enough shape). (4) Successor ticket 10 runs on `af_find_all` as frozen here.
Job ledger: terminal COMPLETED jobs — 33075324 (D1), 33075523 (V1), 33075637 (D2), 33075802
(V1b), 33075938 (V1c), 33076127 (V1d), 33076317 (V1e), 33076559 (V1f), 33077142 (V2a/b),
33077336 (V2c-diag), 33079037 (V2d), 33084770 (V2e), 33085412 (V3a/b), 33086235 (V3c),
33086552 (V3d), 33086913 (V4), 33087310 (V5). FAILED runs were all script bugs with completed
reruns: 33075189 (`cross` implicit-expansion), 33076970 + 33085834 (sprintf format recycling),
33077615/33077892/33078297/33078668 (v2d series), 33081258 (output-arity). No commits made
(per rules); all code staged at `.scratch/pota-repro/p12-stage/` + Spartan potsac-p12-run/.

**Starting position (inherited, re-verify what you touch):** 09 leaves a working chain — loader shim, vote fix (direction ≤1.3° on pieces 01–04), from-paper LM refinement, validated scorer — that still scores 1/8: position stalls 3–5mm in a flat cost basin, small/multi-axis pieces fail on direction (worst 56°/200mm). Cost diagnostic proved the shipped axles ARE the GM-cost minimum but the basin around them is flat. Spartan scaffold to reuse: `/data/gpfs/projects/punim2657/Temp/potsac-p09-run/` (shim/, r2fix/, r3fix/refine_axis.m, score_vs_shipped.m). Paper: `C:\PR\papers\text\sfspp-2502.13986v1.md:169-177`. Pristine clone: re-clone upstream `DominicoRyu/SfSpp_preprocessing @ d5ee6865` yourself.

**The three unknowns (in this order, one variable at a time):**
1. **Point weighting** — what weighting of surface points makes each shipped axle the *unique sharp* minimum instead of a flat basin (rim vs wall balance, normal-confidence, radius arms).
2. **Search + de-dup** — what candidate generation and pruning finds small-sherd and multi-axle answers (pieces 07 has 3 shipped axes, 08 has 2; current dedup keeps only the top-1 neighbourhood).
3. **Rim/base handling** — what the small pieces need that the big ones don't (see 07's rim map + 08's toolbox notes).

**Rules:** fit on pieces 01–04 ONLY; pieces 05–08 stay sealed until the final frozen validation. Shipped axles are the test key, never finder input. New code lives in a new `axle_finder/` package (never edit `sfs_axes/` — quarantined — nor any fork pipeline file). Pristine files stay read-only (overlay, don't fork-edit). Kill branch: if weighting + search + rim work move the fitted score by nothing, stop and report — do not add a fourth variable on your own.

- [ ] Fit (01–04): per-piece direction + position errors after each variable, reported against the ≤5° / ≤2mm bar
- [ ] Frozen validation (05–08, run once, no tuning after unsealing): per-piece errors + pass count; bar for the ticket: 8/8 across fit + held-out reported separately as 4/4 + x/4
- [ ] Design note in Comments: for each variable, what was tried, what the paper says, what the shipped answer implies, what won — so a cold reader can re-derive it
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

**Successor:** ticket 10 (generalise B–J) runs on the frozen finder from this ticket.
