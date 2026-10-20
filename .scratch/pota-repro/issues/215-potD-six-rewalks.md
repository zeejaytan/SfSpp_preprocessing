# 215 - Pot D P16 re-walk + re-score (214 follow-up; narrowed 2026-10-20)

Status: ready-for-agent
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User verdict on the 214 gate (2026-10-20), refined same day: the five locally-wrong stretches (P12/P15/P22/P25/P27 -- same class as P01's stray squiggle, which seats fine) LET SLIDE, their 214 scores stand. Fix P16 ONLY (Bl0 leaves rim upper arc, Bl1 interior shortcut + stalled 83/140). The 23 clean + 5 slid sherds are NOT re-run. Re-score P16 with the same 211 bar; the gate re-opens when P16 is at bar.

## Boundary
Same line: branch pristine-splitwalk (213 cure). Spartan: reuse
sfs-potD-214's inputs but write ALL new outputs to a separate out dir (do
NOT overwrite 214's gate_table.csv, overlays, or lane files -- they are the
record). Do NOT touch: live main checkout, the 2 pre-E2E stashes, any
208/210/211/212/213 dirs, the .wt-pristine-splitwalk worktree (read-only
source). Touch NO tracked file except this ticket. COMMIT NOTHING (lead
commits). Scope ends at re-score -- NO assembly.

## Constraints
Per sherd: state the cause from the 214 overlay + gate numbers BEFORE
changing anything (shortcut? stall? offset? wrong loop?), then the minimal
fix (re-walk seed/params, veto, separation rule -- no new machinery without
a mechanism). Same 209-pattern scoring, same 211 bar per fixed lane
(med <2mm, >=90% cov) with the already-good lane confirmed unchanged.
Pictures: before/after overlay per fixed sherd. Standing submit sign-off
covers probe/re-extract jobs -- do NOT ask; held allocation for iterative
work, sbatch only for long unattended runs with laptop-side poll.

## Acceptance
P16 at bar both lanes (or a stated honest-negative with mechanism, if a lane will not come). Before/after overlay filed. Fix stated GENERALLY (portable, not P16-hardcoded) -- next ticket applies the same fix to the five slid sherds as a same-class-or-not test, THEN 214's gate flips to GO on user nod. This ticket does NOT flip the gate.

## Required evidence
Comments: P16 cause + fix + before/after numbers + picture paths.
Final report: same, self-contained. Do NOT flip to done -- lead flips
after review.

## Comments (worker)
