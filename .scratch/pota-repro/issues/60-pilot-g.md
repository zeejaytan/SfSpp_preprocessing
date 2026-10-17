# 60: Pilot G second — Arm C as-is

**What to deliver:** G fresh E2E with Arm C (R-gate + second-chance recall) — tallies, identities, ceiling.

**Answers:** E1

**Blocked by:** 59 (Arm C = F recipe: Rmean ≥ 0.9×Rmax gate under finder axis + second-chance recall; F 4/6+3/9 ×3; p59 scripts) + 58 (G carries foot-flag exposure: ORIG G base flags 02_0 −2, 05_0 −3).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING; lead owns checkboxes + roll-out call)

## Comments (worker, 2026-10-17 — G pilot lands AT the unflagged baseline, measured)

**Verdict: Arm C transfers to G at-baseline. Fresh flagged G E2E = 4/7+3/10
×3 identical tallies (jobs 33265362/63/64, all sacct COMPLETED 0:0),
matching the best of 39's unflagged G runs (R1 4/7+3/10; R2 3/7+1/10).
ORIG-validity green in all 3 runs: 7/7+10/10 (forest/pruned 51/31 =
39's G ORIG baseline exactly) — cure-potA @ bffefb6 vehicle VALID for G.
No foot poison (ORIG-base 02_0 −2 / 05_0 −3 correctly spared by the
R-gate). Render coherent (green seated ring tracks gray GT ring; no
58-style scatter). No roll-out by me (one-pot mandate kept). No commits;
tickets 39-59 untouched (read-only); original flaggers untouched (p60C is
a laptop-side copy of p59C). Poll was sacct directly throughout.**

**0. Provenance.** Fresh Spartan work area pota60_repro/ only (39/40/49/58/59
lanes read-only, never written). Bundle = byte-identical copy of 39's
pota39_bundle_G (md5-verified COPY-IDENTICAL, 14 files) + Arm C flagging
via p60C_flagger.py (COPY of p59C: R-gate Rmean ≥ 0.9×Rmax + 2nd-chance
recall tier; env P59_POT=G, N_PIECES=7, MIN_N=10; axes = finder_axes_G).
DATA-section md5 identical on all 14 files post-flag (asserted per file);
39's G gate 10/10 carries over formally (same invariance argument as
47/49). Stage = 59's F-stage adapted to G (POT_G overlay, STEPS=7, k=5/b=3
shim, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK green in all
6 arms; asm head bffefb6 asserted per run; A-validity banked in 49 on this
exact vehicle). One fix to my stage copy on record: the tar line tars
`pota60_fetch_G` but the dir is `pota60_fetch_G_C`, and the Pot_F cp
globs missed G — shipped 45-byte empty tgzs; repaired post-hoc on Spartan
(GT from 39's G bundle + flagged rims + T dirs, re-tarred 44 KB each).
Binary tallies/asserts unaffected (read from RUNDIR logs/snapshots).

**1. Tallies (binary-printed; identities recompute exact, CountResult port).**

| job (sacct COMPLETED 0:0) | ORIG (validity) | fresh flagged |
|---|---|---|
| 33265362 (~3.5 min) | 7/7+10/10 (51/31) | 4/7+3/10 (117/17 pruned) |
| 33265363 (~3.5 min) | 7/7+10/10 (51/31) | 4/7+3/10 (117/15 pruned) |
| 33265364 (~3.5 min) | 7/7+10/10 (51/31) | 4/7+3/10 (117/17 pruned) |

Fresh identities ×3 identical (recomputed = binary all 6 arms): seated
[1,3,4,6], missing [2,5,7]; correct edges (1,3),(1,4),(3,6); piece 7
UNPLACED (no T file) all runs; pieces 2+5 placed-but-wrong (every edge
touching 2/5/7 off by 150–830 mm trans, no near-misses).

**2. Flag inventory (Arm C on G: sparse but clean).** 3/14 files flagged
(01_0 s0 strict; 04_0 s0 strict; 04_1 s0 strict). Spared: 02_0 + 05_0
entirely (ORIG-base −2/−3 — the foot exposure 58 warned about; R-gate
spared them, zero fresh-only foot flags) + 01_0 s2 2nd-tier arc
(Rmean 18.4 < 0.9×Rmax, R-gated). Heavy recall losses vs ORIG tops:
02_1, 03_1, 05_1, 06_0, 06_1 carry ORIG rim but no fresh arc passes even
the 2nd tier (too rough/chopped). Forest 117 vs unflagged 146 — masking
works where flags exist.

**3. Declared ceiling for G under Arm C: 4/7 sherds + 3/10 edges, seated
[P1, P3, P4, P6] via edges (1,3),(1,4),(3,6); missing P2
(placed-wrong), P5 (placed-wrong), P7 (unplaced).** Stable ×3 (unflagged
39 arms wobbled 4/7↔3/7). To exceed: content-side recall on pieces 2/5/7
(their ORIG-rim arcs fail even the sh/sr 2.0 tier fresh) + seating work —
flagging alone cannot (only 3 flaggable arcs; pushing thresholds
re-admits feet). Render (eye-checked)
artifacts/pota60/pota60_seating_G_C1.png: green seated fresh tracks gray
GT ring; P2/P5 red dashed off-vessel; P7 absent — coherent, no scatter.

**4. Evidence.** Laptop artifacts/pota60/: 3 fetch tgz + extracted fetch_R*
(GT, rims_fresh, T_orig/fresh, P60 tallies), p60_identities.py (copy of
p58 logic, POT/N parameterised), p60_render.py + seating PNG. Spartan
pota60_repro/ (p60C_flagger.py copy, flag sbatch + p60_flag_report_G_C.txt,
stage sbatch, bun md5s) + sfs_main/pota60_run_C_{33265362,63,64}/
(binary logs, snapshots, repaired fetches). Flag job 33265324 COMPLETED
0:0 (7 s). Poll was sacct directly throughout.

**5. Recommendation for lead.** Land Arm C as the G recipe (at-baseline ×3,
controls green, identities named). It does NOT exceed the unflagged
baseline — same wall as F (pieces too rough for recall; one piece
unplaced). Successor: roll Arm C to remaining pots (C/D/E/H/I/J) per
ticket 58 — G proves the foot fix generalises where F proved the poison.

**Starting position:** run Arm C unchanged on Pot G: same flagger copy (p59 scripts — COPY, never edit originals), same T48b pipeline, cure-potA @ bffefb6 vehicle. Per-pot GT keys in class/data_structure.cpp + data_path.h; 39's G ORIG baselines as the validity bar. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** (a) ORIG-validity FIRST (must match 39's G ORIG baselines — else void); (b) fresh E2E ×3 same-binary + identities; (c) gate green; (d) declare G ceiling with names; renders (eye-check); no commits; sacct-direct polling; Comments-only ticket edits.

- [ ] G ORIG-valid + fresh ×3 + identities + ceiling
- [ ] Job IDs + sacct states

**Successor:** roll-out to remaining pots (C/D/E/H/I/J) per ticket 58, or G-specific attribution (51-pattern) if short of ceiling.
