# 215 - Pot D P16 re-walk + re-score (214 follow-up; narrowed 2026-10-20)

Status: done
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

## Lead verdict (2026-10-20)
ACCEPT (split): Bl0 AT BAR -- rechecked EXACT (0.56/97.4, cross-lane 7.64/0); Bl1 HONEST-NEGATIVE with mechanism -- rechecked EXACT (0.62/78.7, cross-lane 7.72/0). After-overlay eye-checked: red rides blue; orange improved mid-arc but stops at both corners, matching the stated cause (S1 patch spans 235-273 deg vs rim sector 230-308 deg; corner has no inner face, K=1 snap cannot sample it). 214 tree untouched (only ticket files modified). Cause proven with numbers (snap no-op: UN self-NN med 0.00, disp 0.00; bag idx ranges filed). Fix portable: face-ref normals (T_FRAC 40 deg) + strip-only unclustered -- no author input, no code change, same 214 binary. Dead ends logged with kill-numbers (dihedral-crease, cloud-fill). Holder 33516830 left running for class test.

## Comments (worker)

### 2026-10-21 worker note (subagent, P16 diagnosis + strip-UN fix, NO commit)
CAUSE (from 214 numbers + Spartan stage files, mechanism proven): P16's mesh is
watertight (13815 verts, 0 naked edges), split into S0=13767 / S1=6134 /
unclustered=16569 pts. BOTH true rims lie in unclustered (m0 vs UN 0.28mm,
m1 vs UN 0.23mm; m0/m1 = author arcs our walk missed). The edge binary snaps
every surface-boundary dot to its nearest UN pt (K=1), but the split left
near-duplicate UN pts all along both patch edges (UN med self-NN = 0.00),
so the snap is a no-op (S0 disp med 0.00, S1 med 0.00) and the walk input =
the patch's own eroded edge (carve cut), 9mm (Bl0 ends) to 25-43mm (Bl1
corners) from the true rim. Bag proof: S0 bag 367 rides o0 21-118 only
(rim ends 0-20/119-132 missing); S1 bag 230 covers o1 20-63 only, plus a
12-pt floating chip (16mm off both rims, cut-walked => 21mm jump).
FIX (general/portable, no author input, no code change, 214 binary reused
md5 dc472b0e87c934b6c487ff8637209864): (1) face-ref normals from
SampledWithNormals pts near each patch; (2) label SN pts face/fracture by
normal angle (T_FRAC=40deg; measured S1-side face p90 18 vs fracture p10
28); (3) rim estimate C0'/C1' = fracture pts within 1.5mm of face pts
(validation-only vs author: C0'->o0 med 1.20 cov2mm 93%, C1'->o1 med 1.09
99%); (4) per-face run with unclustered.ply REPLACED by strip-only
{UN within 1.0mm of that face's C'} + ORIG clouds (trees pota215_stripS0/S1,
214 inputs md5-verified, 214 tree untouched). Snap teleports then land on
rim-strip pts (harmless dups) instead of band garbage.
RESULTS (same 209 ruler, laptop artifacts/pota215/): Bl0 0.80/76.2% ->
0.56/97.4% AT BAR (n=115, one 17.8 jump idx22). Bl1 1.45/51.8% -> 0.62/78.7%
(n=61, 35.4 jump idx3) -- med fixed, cov short. Bl1 residue: o1 missing
runs (0-16),(35-38),(63-139): S1's patch spans 235-273 deg but the rim sector
is 230-308 deg (face1 label itself ends 281 deg -- the corner has no inner
face, chipped to fracture), so S1 has no boundary dots angularly near the
corners and K=1 snap can never sample the corner strip (every dot has a
nearer strip pt in the covered arc). Needs cross-face lane logic or
mesh-direct tracing = new machinery => HONEST-NEGATIVE on Bl1's corner arcs
with mechanism above. Bl0 fix is the class pilot. Before:
artifacts/pota214/p214_P16_overlay.png. After:
artifacts/pota215/p215_P16_overlay_after.png. Fixed lanes:
.scratch/p215_evidence/strip_P16_Breakline_{0,1}.pcd. Scripts:
.scratch/p215_p16_{membership,stage,bagmap,sectors,bridge,hole,crease,normcontrast,reclaim,stripun,spans}.py. Holder 33516830 (sapphire) left running
for follow-up. Status: worker done, lead to review/flip.
