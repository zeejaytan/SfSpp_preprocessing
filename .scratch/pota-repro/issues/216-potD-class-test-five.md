# 216 - Class test: P16 strip recipe on the five slid sherds (215 follow-up)

Status: ready-for-agent
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User sequence (2026-10-20): P16's fix now goes onto P12/P15/P22/P25/P27 as
the same-class-or-not test. 215's recipe is portable (face-ref normals
T_FRAC=40deg + strip-only unclustered, no author input, no code change,
same 214 binary dc472b0e). Each sherd gets a verdict: SAME CLASS (fixed at
bar) or NOT (with mechanism -- like P16-Bl1's patch-span shortfall).
Holder 33516830 (spartan-bm200, sapphire 4h) was left running by 215 for
this -- adopt it or release it, state which.

## Boundary
Same line (pristine-splitwalk cure), same binary. Spartan: separate out
dir (never overwrite 214's record or 215's P16 evidence). Do NOT touch:
live main checkout, the 2 pre-E2E stashes, 208/210/211/212/213 dirs,
.wt-pristine-splitwalk (read-only source). Touch NO tracked file except
this ticket. COMMIT NOTHING (lead commits). Scope ends at re-score -- NO
assembly.

## Constraints
Per sherd, IN ORDER: (1) run 215's portable gate FIRST (does that face's
patch span the rim sector? patch span vs strip span, no author needed) and
PREDICT fix/no-fix; (2) apply the recipe; (3) verify against the author
with the 209 ruler + 211 bar (med <2mm, >=90% cov). A correct prediction
counts as much as a fix -- the question is same-class-or-not, not fix-all.
Before/after overlay per sherd. Standing submit sign-off covers jobs -- do
NOT ask; laptop-side poll per sbatch.

## Acceptance
Five verdicts, each: prediction + outcome + mechanism. Scoreboard: which
lanes moved to bar, which did not and why. Then the 214 gate state (GO /
GO-with-flags / hold) is the user's -- this ticket does NOT flip it.

## Required evidence
Comments: per-sherd predict/apply/verify + picture paths + scoreboard.
Final report: same, self-contained. Do NOT flip to done -- lead flips
after review.

## Comments (worker)
