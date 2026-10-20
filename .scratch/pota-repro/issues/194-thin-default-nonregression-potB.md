# 194 - Thin-then-walk as default: non-regression on clean Pot B

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Prove the thin-then-walk default is HARMLESS on clean rims: force-apply the 185 v3 recipe to Pot B's already-single SXC Bl_0 loops, bundle, E2E x3 vs 93's bar. If tallies match 93, the default is safe everywhere (cures doubled, keeps clean).

## Method (worker runs FULL chain, SSH works -- Host spartan)
0. Densify (143 pre-step): measure dot spacing on each B02-B09 SXC Bl_0 loop first. If coarser than the ~1.8mm regime, true mesh-sampled densify per 143 (ladder to saturation); midpoint interpolation is FORBIDDEN (111/146 refutation -- it adds zero true edge info). If already at ~1.8mm, record spacing numbers and close this step vacuous per loop.
1. Split (175 pre-step, read 175-two-walks-two-slots.md first): apply the 175 split-by-parent-surface rule to each B02-B09 SXC Bl_0 loop BEFORE thinning -- mesh-observable features only, no ORIG in the rule. Expectation on clean singles: each loop yields ONE face cloud (no second cloud); if the split finds two faces inside a 'clean' loop, that is new evidence -- report it, do not silently pool. Then thin+walk the face cloud(s) per step 2.
2. Thin: apply 185 v3 (thin TRUE strip to centreline, uniform 1.8mm resample, verbatim walk_m144) to each face cloud from step 1 (B01 forest excluded, with 78 per 93/187). Gate each loop: closure <=2.0, single wrap, rim-truth med (check-only, expect ~0.5-1.15 per 187).
3. Falsifier (own in advance): any loop whose rim-truth med worsens by >0.5mm vs its unthinned SXC input is REFUSED (not bundled) -- thinning must not move clean dots off the rim.
4. Bundle: rebuild with ONLY the thinned Bl_0 slots changed (byte-proofs, only-changed diff, veto-absence, 180/186 pattern).
5. E2E: same vehicle cure-potA @ bffefb6 (this carries every Pot A-diagnosis change: preprocessing T13/T21/T23/T24/T27 + assembler P22FIX/P22FIX2 + C2-restore per ticket 38 -- verify HEAD before building); same-binary ORIG control must reproduce its bar (93's ORIG arm) or the run is VOID. Upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message.

## Acceptance
Per-loop gates + falsifier check + bundle byte-proofs + E2E tallies x3 vs 93 + verdict (safe-default / regression with refusing numbers).

## Required evidence
Ticket Comments + final output: loop gates, refused loops if any, md5s, job IDs, per-run tallies, verdict.
