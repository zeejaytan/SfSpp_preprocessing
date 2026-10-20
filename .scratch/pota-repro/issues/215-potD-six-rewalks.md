# 215 - Pot D six mixed lanes: targeted re-walk + re-score (214 follow-up)

Status: ready-for-agent
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User verdict on the 214 gate (2026-10-20): fix the 6 mixed sherds first, then
GO on all 29 together. Targeted re-walks for P12 (Bl0 interior chord),
P15 (inner shortcut one arc), P16 (Bl1 stalled 83/140, Bl0 slightly short),
P22 (mid-span excursion ~10mm), P25 (small-piece offset), P27 (parallel
offset upper arc). The 23 clean sherds are NOT re-run (214 evidence stands).
Re-score fixed lanes with the same 211 bar; the gate re-opens when all six
are at bar.

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
All six sherds at bar both lanes (or a stated honest-negative per sherd
with mechanism, if a lane will not come). Before/after overlays filed.
Then 214's gate flips to GO on user nod -- this ticket does NOT flip it.

## Required evidence
Comments: per-sherd cause + fix + before/after numbers + picture paths.
Final report: same, self-contained. Do NOT flip to done -- lead flips
after review.

## Comments (worker)
