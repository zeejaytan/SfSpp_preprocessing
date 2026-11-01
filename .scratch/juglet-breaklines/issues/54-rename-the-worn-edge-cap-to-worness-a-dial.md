# 54 — rename the worn-edge cap to WORNESS, a dial for how worn a sherd is

**What to build:** the opt-in worn-edge growth angle becomes ONE knob named after what it means
physically: SFS_WORNESS. Unset (default) = today's shipped behaviour, flat 3.4 (corpus). Set to a
multiplier w (0 < w <= 1, recommended 0.9 = the calibrated value) = worn-edge mode: theta =
min(formula theta, w x measured crossing), i.e. the current SFS_GROWTH_FORMULA=1 +
SFS_GROWTH_CAP=1 behaviour with the 0.9 promoted from a hard constant to the dial. More worn
sherd -> higher w -> looser allowed angle, still never above what the piece's own measured
crossing permits.

**Answers:** U19 (worn-edge regime as an explicit, named variable)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-01)
**Branch:** 54-rename-the-worn-edge-cap-to-worness-a-dial, in /c/PR/worktrees/sfs/54

**Worker:** unassigned

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
