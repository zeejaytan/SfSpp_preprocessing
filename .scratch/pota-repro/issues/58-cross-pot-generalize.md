# 58: Cross-pot generalization — run the B recipe on C–J

**What to deliver:** per-pot fresh-vs-ORIG E2E tallies on Pots C–J using the banked B recipe — with per-pot ceilings, not 100% expectations.

**Answers:** E1

**Blocked by:** 49 (relaxed ≥10-pt flag rule → B 8/9+7/15; flagger p49_flagger.py) + 47 (paper-recipe flagger base, p47_flagger.py) + 48 (T48b direction-mirror pipeline) + 51 (8/9-shape ceiling doctrine: one weak contact missing is the realistic target) + 39 (ORIG-validity vehicle pattern: prove ORIG scores first per pot, then read fresh) + 40 (cure-potA vehicle @ bffefb6).

**Status:** results-in (pilot Pot F done 2026-10-17, COMMIT NOTHING; lead owns checkboxes + roll-out call)

## Comments (worker, 2026-10-17 — PILOT Pot F: recipe does NOT transfer, measured)

**Verdict: NEGATIVE transfer on F. The banked B recipe (paper-recipe flagger +
relaxed >=10-pt rule) collapses Pot F fresh E2E from 39's unflagged 4/6+3/9
(x3) to 0/6+0/9 (x3 identical tallies). ORIG controls valid in all 3 runs
(6/6+9/9, forest 36/27 = 39's F ORIG baseline exactly) — vehicle
cure-potA @ bffefb6 is VALID for F; the failure is the flagged rims, not the
vehicle. No roll-out to other pots (per brief: one pilot only). No commits;
tickets 39-57 untouched (read-only); original flaggers untouched (p58 copies).
All jobs sacct-verified COMPLETED 0:0.**

**0. Pilot choice + provenance.** Pilot = Pot F (smallest: 6 E2E pieces 01-06,
9 GT edges; F07 excluded by EMPTY axle file, carried over from 39's bundle;
GT graph row for F07 all-zero). Fresh Spartan work area pota58_repro/ only
(39/40/49 lanes read-only, never written). Bundle = byte-identical copy of
39's pota39_bundle_F (md5-verified COPY-IDENTICAL, 14 files) + header-only
flagging (DATA-section md5 identical on all 14 files post-flag; full-file
diffs confined to `# nseg npts top` + seg flag columns, e.g. 02_0 top 0->1).
39's F gate was 9/9 on these exact coordinates -> gate carries over formally
(same invariance argument as 47/49). Flagger = laptop
.scratch/pota-repro/p58_flagger.py (COPY of p49 recipe, POT/AXDIR/BUN
parameterised, MIN_N=10) uploaded to pota58_repro/p58_flagger.py; axes =
finder_axes_F (same axes the E2E arm consumes, so ONLY delta vs 39 is flags).
Stage = copy of 39's F-stage (POT_F overlay, STEPS=7, k=5/b=3 shim,
LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK green in all 6 arms).

**1. Tallies (binary-printed; identities recompute exact).**

| job (sacct COMPLETED 0:0) | ORIG (validity) | fresh flagged |
|---|---|---|
| 33263263 (~4 min) | 6/6+9/9 (36/27) | 0/6+0/9 (67/17) |
| 33263264 (~4 min) | 6/6+9/9 (36/27) | 0/6+0/9 (67/17) |
| 33263265 (~4 min) | 6/6+9/9 (36/27) | 0/6+0/9 (67/17) |

39 baseline same vehicle/bundle-coords: ORIG 6/6+9/9 (36/27) x2; fresh
UNFLAGGED 4/6+3/9 (136/18) x3. So flags: forest 136->67 (masking works),
pruned 18->17, but seating 4/6->0/6. Recomputed identities (p58_identities.py,
CountResult port, matches binary exactly all 6 arms): fresh seated [] missing
[1-6] all 3 runs; piece 1 UNPLACED (no T file) all 3 runs; all 9 GT edges
wrong by 380-780 mm trans (total scatter, not near-misses). Runs 2+3 pose-
identical, run 1 differs slightly (beam lottery, tally-identical).

**2. Flag inventory vs ORIG F layout (why transfer fails — evidence, not tuning).**
8/14 files flagged (02_0, 03 both, 04 both, 05_0, 06 both); pieces 01 (both)
and 07 unflagged. Against ORIG F tops: 3 recall losses on E2E pieces (01 both
sides carry ORIG rim, 02_1 s0, 05_1 s3 — fresh arcs too rough, no
recipe-passing arc); 5 fresh-only flags on edges ORIG marks base(-2)/zero
(02_0, 03_0, 04_0→ORIG-top-0, 05_0, 06_0). True-rim check (nn fresh-flagged vs
ORIG-flagged arcs, either side): 4 arcs ~1 mm (02_0 s0 0.84, 04_0 s0 0.97,
05_0 s3 1.19, 06_0 s0 1.21 — consistent with 42's fresh-Bl_0≈shipped-Bl_1
side swap), 3 arcs 3-3.7 mm (03_1 s3, 04_1 s2, 06_1 s0), 2 far (04_1 s0
16 mm, 03_0 s4 43 mm — foot-arc suspects on ORIG-base edges). Matcher
channels (code-read, cure tree): LCS fracture-masking drops flagged ranges
(forest halves 136->67) + H_rim veto (feature_matching.cpp:1229,
ranking_system.cpp:1829 — "Breakline can not over rim height": rejects any
hypothesis whose profile spans H_rim±10 mm both sides, H_rim from flagged
rim_data). With foot-contaminated rim_data and 3 recall losses, the
mask+veto remove/down-rank the hypotheses 39's unflagged beam seated off —
B had a clean true-rim flag set (17/18 validation), F does not. No vehicle
patch, no ORIG points used anywhere (ORIG evidence-only: layout + nn).

**3. Ceiling: UNDETERMINED for F under this recipe (0 seated — nothing to
attribute; 51-doctrine needs a seating to dissect).** The pilot answers the
transfer question in the negative; per-pot ceiling work on F belongs to the
successor only with a working recipe. Render (eye-checked)
artifacts/pota58/pota58_seating_F_R1.png: gray GT ring coherent, red EST
poses total scatter (loops floating above/beside pot), P1 unplaced — matches
0/6+0/9.

**4. Evidence.** Laptop artifacts/pota58/: 3 fetch tgz + extracted fetch_*
(GT, rims_fresh, T_orig/fresh, P58 tallies), orig_F_bl.tgz, flag report,
truerim, render, p58_identities.py + p58_render.py (masters in
.scratch/pota-repro/). Spartan pota58_repro/ (flagger, stage sbatch, flag
logs, bun md5s, orig_F_bl.tgz) + sfs_main/pota58_run_{33263263,64,65}/
(binary logs, snapshots, fetches). Poll was sacct directly throughout.

**5. Recommendation for lead (no second pilot run by me — one-pot mandate kept).**
(a) Do NOT roll the as-is recipe to C–J: F proves flags can destroy as well
as rescue. (b) G as a second pilot is NOT predicted clean: ORIG G also
carries base flags (02_0 -2, 05_0 -3) — same foot-confusion exposure. (c) The
falsifiable follow-up is flagger-side, not beam-side: mouth/foot
disambiguation (e.g. z-side test: rim arc must sit high on the piece axis;
ORIG tops ±1/±2/±3 already encode rim-vs-base and the paper test ignores
them) + recall on chopped fragments; then re-pilot F (needs: seated>0 with
controls green x3). Successor per ticket: per-pot attribution where a pot
falls short of ceiling — F currently has no working recipe to attribute.

**Starting position:** the banked recipe: (1) paper-recipe flagger + relaxed ≥10-pt recall rule, (2) T48b honest pipeline (no resampling — 50; raw sampling is signal), (3) cure-potA @ bffefb6 vehicle with LINK-SHIM-OK + DRIVER-SHIM-OK, (4) repeats ≥3 per condition (last-bit FP rule from 43), (5) same-binary ORIG control per pot must score like ticket 39's ORIG-valid baselines before any fresh tally reads. Per-pot GT keys from class/data_structure.cpp + data_path.h. Expect drowning-shape forests (39) and per-pot weak contacts (51-doctrine: ceiling = full seating minus weak contacts, declared per pot with names). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** per pot, in order: (a) ORIG-validity control FIRST (must match 39's per-pot ORIG baselines — else vehicle is void for that pot); (b) fresh E2E ×3 same-binary + identities; (c) gate 15/15-equivalent per pot; (d) declare per-pot ceiling with seated-piece names; renders per pot (eye-check); no commits; sacct-direct polling; Comments-only ticket edits. Start with ONE pilot pot (smallest: F or G — G was 7/7 on axle finder, F small), prove the recipe transfers, then roll to the rest. Do NOT touch tickets 49-57 files or flaggers (read-only reference; copy, don't edit).

- [ ] Pilot pot (F or G): ORIG-valid + fresh ×3 + identities + ceiling
- [ ] Roll-out C–J (minus pilot): same per pot
- [ ] Cross-pot table: recipe transfers or measured where-not per pot
- [ ] Job IDs + sacct states

**Successor:** per-pot weak-contact attribution wherever a pot falls short of its ceiling (51-pattern).
