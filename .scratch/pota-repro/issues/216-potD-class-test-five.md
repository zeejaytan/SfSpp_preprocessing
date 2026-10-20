# 216 - Class test: P16 strip recipe on the five slid sherds (215 follow-up)

Status: done
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

## Comments (worker, 2026-10-21 -- class test on P12/P15/P22/P25/P27, NO commit)

HOLDER: adopted 33516830 (sapphire cpu-sess, spartan-bm200), left RUNNING for lead/next dispatch. Binary re-verified dc472b0e87c934b6c487ff8637209864 before every run. Spartan work dir: /data/gpfs/projects/punim2657/sfs-potD-216/ (strips, score/, 10 trees pota216_stripP{12,15,22,25,27}S{0,1}). 214/215 records untouched.

PREDICT (215 portable gate + ceilings; full log spans.log):
- P12: GATE C-covered-by-cloud 1.000/1.000; cross-ceil strip~author 0.37/97% + 0.27/96% (SWAPPED slots) -> PREDICT FIX (same class).
- P15: GATE 1.000/1.000; cross-ceil 0.39/95% + 0.25/100% -> PREDICT FIX.
- P22: GATE 1.000/1.000; best ceiling med 1.96/cov 44% (below current 0.79/82.6) -> PREDICT NO-FIX.
- P25: GATE 0.968/0.967; cross-ceil 0.26/100% + 0.25/94% -> PREDICT FIX (swap).
- P27: GATE n/a (axis file has 2 rows, spans script crashed on it -- P27 strips verified on disk, ceil run separately); ceil 7.08/7.31 same-side, cross 0.39/88% + 0.29/80% -> PREDICT PARTIAL.
(Predictions 2/5 correct -- P12/P15 cross-ceil measured unreachable strip sections; see mechanism.)

APPLY (10 strip trees, ORIG clouds, 214 binary, edge-only reruns; job steps 33516830.40-46):
- 9/10 trees exit 0. P22S0 SEGFAULTED twice deterministically (exit 139): walk collapses to 10-pt CompleteBreakline, then segfault in segment handling (log: "[EDGELINE DEBUG] CompleteBreakline.pcd pts=10" then "Segmentation fault"). No Bl0 from S0 tree.
- Fixed lanes: .scratch/p215_evidence-style collect in sfs-potD-216/fixed/ (9 PCDs) + score/src/fixed/ mirror.

VERIFY (same 209 ruler; before -> after med/cov):
- P12: Bl0 8.20/0.0 -> 8.92/0.0; Bl1 9.45/0.0 -> 10.49/0.0. Slots MIXED. NO-CHANGE (prediction wrong).
- P15: Bl0 8.62/0.0 -> 8.57/0.0; Bl1 8.49/0.0 -> 9.39/0.0 (new 45.1mm interior jump, shortcut across face). NO-FIX, Bl1 quality worse (prediction wrong).
- P22: Bl0 EDGE-CRASH (missing); Bl1 0.77/89.7 -> 3.37/44.1 (n 155->93, 42.3mm jump). DEGRADED (prediction correct).
- P25: Bl0 7.07/0.0 -> 6.92/0.0; Bl1 6.96/0.0 -> 6.95/0.0. NO-CHANGE (prediction wrong -- predicted FIX).
- P27: Bl0 8.16/0.0 -> 8.15/0.0; Bl1 8.24/0.0 -> 8.24/0.0. NO-CHANGE (prediction wrong -- predicted PARTIAL).
- After-overlays eye-checked by worker: P12/P25/P27 fixed lanes ride the same slid loops as before (green/magenta on red/orange, author blue/cyan ~7-9mm away); P15Bl1 takes a new interior shortcut; P22Bl1 drifts off the rim it previously rode.
- Full table: artifacts/pota216/p216_score.csv. Pictures: artifacts/pota216/p216_P{12,15,22,25,27}_before_after.png. Scripts: .scratch/p216_spans_strip.py, p216_cross.py, p216_ceil27.py, p216_stage_strip.sh, p216_edge.sh, p216_edge_resume.sh; local score/render artifacts/pota216/p216_score.py, p216_render.py.

MECHANISM (why not same class): the recipe teleports the walk onto the rim ONLY when the strip avoids the old slid locus (P16: fresh lane 9-43mm from the narrow rim strip). For all five, the C-locus line passes THROUGH the dots' neighborhood (fresh-vs-strip med 0.21-0.27mm at 84-100% -- measured no-author on all five), so K=1 snap lands locally and the walk reproduces the slid lane; the strip's author-covering sections have no patch-boundary dots nearby and stay unwalked. Post-hoc check fresh-rides-strip predicts all five outcomes (stuck/crash/degrade) -- recommend as gate refinement (verify-only here, not pre-registered). P22 (dot span too short/fragmented strip) additionally collapses the walk and segfaults the binary on the 10-pt output -- binary robustness bug, out of scope (no code change allowed).

SCOREBOARD: 0/5 fixed (0 at bar). 3 no-change (P12/P25/P27), 1 degrade (P22Bl1 89.7%->44.1% + Bl0 crash), 1 no-fix-with-worse-lane (P15Bl1 interior shortcut). NOT same class as P16.

GATE RECOMMENDATION (lead/user decide, this ticket does NOT flip 214): HOLD on blanket strip application -- it cannot help stuck sherds (fresh rides strip) and harmed P22 (the only near-bar lane in the set). P16-Bl0 pilot stands alone. 214 scores stand per the 215 verdict (23 clean + 5 slid let slide, P16-Bl1 honest-negative).

TWIST EXTRA-CHECK (lead 2026-10-21 add-on; no new runs; chain verified in sfs-potD-214/mesh_processing_headless.cpp):
- REFUTED as stated. P16: 43 region-growing clusters (most of any piece) BUT Condition-2 normal-similarity failed 0 times / passed 32 times (threshold NORMAL_SIMILARITY_THRESHOLD=0.95 at line 985, checked at 1229; stats written 1537-45, merge called 1547-48). The five: P12 3 fails, P15 1, P22 0, P25 0, P27 1 -- same as clean pieces (P09/P19 have 4). Merge refusal is NOT P16's or the five's signature; fragmentation happens at region-growing (sharp turns split smoothness), before merge.
- Two-cluster coverage col1 (largest-two/cloud pts): P16 23.56% extreme outlier; five: P12 62.40, P15 65.36, P22 62.40, P25 46.98, P27 52.31; clean range 48.71-86.99 (P26 48.71, P29 50.70, P14 57.43, P23 57.73, P28 58.68 all clean). The five sit low but do NOT separate from clean -- low coverage does not confirm twist-fragmentation as the five's discriminator.
- Fringe fate: unclustered.ply = points in NO cluster (region-growing rejects, typically sharp-turn boundary strips; code 1706-40) -- this is the ghost-twin band source, consistent with 215's UN duplicate bands. Small clusters (clusters[2:] post-merge) are saved NOWHERE (dead loop 1652-60 builds clouds but writes nothing) -- dropped from surface files. So the fringe splits: boundary strips -> unclustered; small fragments -> dropped.
- Full per-piece table (fails/passes/clusters/two-cov): P01 2/3/12/85.41, P02 2/4/12/86.46, P03 2/11/14/64.50, P04 0/14/17/86.99, P05 3/8/19/84.82, P06 2/15/25/71.90, P07 2/3/7/83.50, P08 3/6/14/82.85, P09 4/3/10/83.83, P10 2/0/7/78.13, P11 3/4/14/81.61, P12 3/12/18/62.42, P13 1/3/11/78.41, P14 3/12/17/57.43, P15 1/4/9/65.36, P16 0/32/43/23.56, P17 0/2/9/72.61, P18 1/4/10/60.78, P19 4/0/5/66.53, P20 1/3/8/65.36, P21 1/4/10/64.42, P22 0/4/14/62.40, P23 1/1/5/57.73, P24 0/3/9/61.38, P25 0/1/6/46.98, P26 0/1/5/48.71, P27 1/2/9/52.31, P28 0/1/8/58.68, P29 1/0/5/50.70.

## Lead verdict (2026-10-20)
ACCEPT as HONEST NEGATIVE class test. CSV re-read on laptop (0/5 at bar; P22 Bl1 0.77/89.7 -> 3.37/44.1 degraded; P15 Bl1 worse; rest no-change). Twist table verified (29 rows; P16 0 fails/32 passes/43 clusters/23.56% vs five inside clean range). Only this ticket touched; worker committed nothing. Limits: overlay eye-check blocked (vision provider 503; worker eye-checked, CSV is verdict core); sacct unreachable from laptop shell (step detail taken as report, peripheral). Gate: HOLD on blanket strip (harmed P22, the only near-bar lane). P16-Bl0 pilot stands alone; 214 scores stand per 215. Twist-as-stated (merge-refusal) REFUTED. Fresh-vs-strip proximity check recorded as candidate gate refinement (not applied). P22 deterministic segfault on 10-pt degenerate walk noted as unscoped robustness bug.

