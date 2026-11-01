# 54 — rename the worn-edge cap to WORNESS, a dial for how worn a sherd is

**What to build:** the opt-in worn-edge growth angle becomes ONE knob named after what it means
physically: SFS_WORNESS. Unset (default) = today's shipped behaviour, flat 3.4 (corpus). Set to a
multiplier w (0 < w <= 1, **recommended 0.7** -- the conservator's dial, 2026-11-01; 0.9 is the t51-calibrated value, no longer the recommendation) = worn-edge mode: theta =
min(formula theta, w x measured crossing), i.e. the current SFS_GROWTH_FORMULA=1 +
SFS_GROWTH_CAP=1 behaviour with the 0.9 promoted from a hard constant to the dial. More worn
sherd -> higher w -> looser allowed angle, still never above what the piece's own measured
crossing permits.

**Answers:** U19 (worn-edge regime as an explicit, named variable)

**Status:** done — merged 0724e5d, binary reproduced, ledger row 12
**Working in:** chat on Thinkbook16 (2026-11-01)

## Result (lead, 2026-11-01) — MERGED, binary reproduced, ledger row 12

**Code:** `SFS_WORNESS` in `mesh_processing_headless.cpp` (77f50ad, merged --no-ff as 0724e5d).
Unset = today's shipped behaviour (flat 3.4 on the corpus), proven byte-identical; `0 < w <= 1`
= worn-edge mode, theta = min(formula, w x the piece's own measured crossing); out-of-range or
unparsable = FATAL, rc 2, no surface. Precedence SFS_PAPER_THETA > SFS_WORNESS >
SFS_GROWTH_FORMULA/CAP, both old knobs untouched.

**Run of record:** 20261101-1613_83edd76_t54-worness-dial, job 34160654, COMPLETED 0:0 in 19:30,
68 cells rc=0, corpus gate 9/9 on md5 AND kept_points, inputs md5 unchanged.

| arm | what it proves | result |
|---|---|---|
| D (nothing set) | no-op | thetas identical to X (3.40000) on 17/17; point counts identical on Juglet and Pot A 07/08, 2-6 points (<=0.02 pct) on Pot A 01-06 from the known unseeded mesh-stage spread |
| W (0.9) | the worn dial | theta == min(formula, 0.9 x crossing) exactly on every cell; Juglet 8/9 genuine pairs (med_nn 81.9-103.5 pct of own wall, med_across <= 0.036 mm); J8 junk (145-pt second surface) — expected, it is spacing-bound, and it recovers under W7 |
| W7 (0.7) | the dial turns the right way | thetas strictly below W on 17/17 |
| FATAL probes | units guard | `=0` and `=abc` both rc 2 with `[WORNESS-54] FATAL ...` and no surface |

**Recommended dial: 0.7 (conservator's decision, 2026-11-01).** 0.9 stays in the record as the t51-calibrated value, but it is not the recommendation: at 0.7 the thetas turn down on 17/17 cells and J8's second surface recovers (9/9 genuine wall pairs on the Juglet), so 0.7 is the value the next tickets build on (ticket 55 runs the chain at WORNESS=0.7 down to breaklines).

**Reproduced from merged main** (conservator's instruction): run 20261101-1643_83edd76_t54-reproduce,
job 34161339, COMPLETED 0:0, built from the merged tree; binary md5 **736ff95c976486d17f7c00b3af402040**,
identical to the branch run's binary. Thetas, formula thetas and crossings identical across the two
runs on 17/17; pair-quality percentages agree to within 0.5 pct (J3 92.9/92.7, J7 90.9/90.4, J9 89.4/89.3)
— the mesh stage's unseeded draw, not a code difference.

**Ledger:** row 12 in `.scratch/pota-repro/FIXES-LEDGER.md` section Q (commit f2f17a3), pointing at
row 5 (the 3.4 gate it complements).

**Caveat recorded, not hidden:** on the Juglet, arm W does NOT reproduce the ticket-51 reference
thetas (deltas 1.96-14.37 deg). Both measured inputs differ from that reference table too (e.g. J1
formula 19.03 vs 10.84, crossing 9.18 vs 7.00), so the gap is in the measurements feeding the cap —
which changed when ticket 50 made the sampling step uniform — not in the dial's arithmetic, which is
exact per cell. The t51 numbers are not a valid reference for today's spacing.

verified: sacct 34160654 COMPLETED 0:0 and 34161339 COMPLETED 0:0; `diff` of thetas54.tsv columns
1,2,3,8,9,10,14 between the two runs = empty ("THETAS+FORMULA+CROSSING IDENTICAL ACROSS RUNS");
BUILD md5 line 736ff95c... in both run logs; awk D-vs-X mismatch scan on the reproduce run = empty.

**Branch:** 54-rename-the-worn-edge-cap-to-worness-a-dial, in /c/PR/worktrees/sfs/54

**Worker:** 14f39d5e-1124-4c7b-bab9-488002899071 - built SFS_WORNESS, the stage54 harness and submitted the run; lead verified, merged, reproduced the binary from main and wrote the ledger row

## Spec

- In mesh_processing_headless.cpp: read SFS_WORNESS (getenv, strtod). Unset/empty = OFF, and OFF
  must be byte-identical to today's main (no log line, identical output). Set = enable the
  formula path (as SFS_GROWTH_FORMULA=1 does today) AND cap theta at w x crossing (as the 0.9
  cap does today). w <= 0 or w > 1 or unparsable = FATAL with a clear message (this is a units
  guard, not a tuning fallback).
- Log per piece when ON: "[WORNESS-54] piece= formula_theta= crossing= w= capped= theta=".
- Keep SFS_GROWTH_FORMULA and SFS_GROWTH_CAP working exactly as today (back-compat; the t51/t52
  runs stay reproducible). Precedence: SFS_PAPER_THETA > SFS_WORNESS > SFS_GROWTH_FORMULA/CAP.
- No other behaviour change. No default flip (corpus stays 3.4; the conservator has decided).

## Acceptance (17-piece harness, one run, three arms)

- Arm D (nothing set): outputs byte-identical to arm X (SFS_PAPER_THETA=3.4) — the no-op proof
  (compare thetas + surface point counts; corpus md5s untouched).
- Arm W (SFS_WORNESS=0.9): reproduces the t51/t52 capped thetas and pair quality (Juglet 9/9
  genuine pairs, med_nn 70-105% wall, med_across <= 0.05 mm; J8 expected junk under uniform
  spacing — report, do not gate).
- Arm W7 (SFS_WORNESS=0.7): thetas strictly <= arm W's, showing the dial turns the right way.

## Reproduce binary + ledger (lead does after merge)

- After merge to main: rebuild from main on Spartan, record edge/mesh md5s in run.json, rerun
  arm D vs X no-op check on the reproduced binary.
- FIXES-LEDGER.md section Q row: the wornness dial; what was wrong (worn Juglet edges glue at
  corpus-tuned 3.4), what it bought (9/9 genuine wall pairs incl. J8 under its own spacing;
  corpus untouched at default, 281/292), pointing at ledger row 5 (the 3.4 gate it complements).

## Out of scope

- Any default flip, corpus change, spacing law change, e2e/seating, J8 spacing ticket.
