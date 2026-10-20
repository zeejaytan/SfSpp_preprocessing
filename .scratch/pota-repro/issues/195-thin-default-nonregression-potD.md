# 195 - Thin-then-walk as default: non-regression on clean Pot D

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Same as 194 for Pot B: prove the full default chain HARMLESS on Pot D's clean single rims (29/29 per 188). Force-apply densify -> split -> thin+walk, bundle, E2E x3 vs 84's bar (22/27+49/66 lineage, cite exact 84 tallies).

## Method (worker runs FULL chain, SSH works -- Host spartan)
0. Densify (143 pre-step): measure dot spacing per D loop; if coarser than ~1.8mm, true mesh-sampled densify (ladder to saturation); midpoint interpolation FORBIDDEN (111/146). If already ~1.8mm, record numbers, close vacuous per loop.
1. Split (175 pre-step, read 175-two-walks-two-slots.md first): apply the 175 split-by-parent-surface rule to each clean single -- mesh-observable features only, no ORIG. Expect one face cloud each; two faces = new evidence, report it.
2. Thin: 185 v3 on each face cloud (P22 handled per 188's ruler-artifact note). Gate: closure <=2.0, single wrap, rim-truth med check-only (~0.51-0.86 per 188).
3. Falsifier (own in advance): any loop whose rim-truth worsens by >0.5mm vs unthinned input is REFUSED, not bundled.
4. Bundle: ONLY thinned Bl_0 slots changed (byte-proofs, only-changed diff, veto-absence, 180/186 pattern).
5. E2E: same vehicle cure-potA @ bffefb6 (this carries every Pot A-diagnosis change: preprocessing T13/T21/T23/T24/T27 + assembler P22FIX/P22FIX2 + C2-restore per ticket 38 -- verify HEAD before building); same-binary ORIG control must reproduce its bar (84's ORIG arm) or the run is VOID. Upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message.

## Acceptance
Per-loop gates + falsifier + byte-proofs + E2E x3 vs 84 + verdict.

## Required evidence
Ticket Comments + final output: loop gates, refused loops if any, md5s, job IDs, per-run tallies, verdict.
