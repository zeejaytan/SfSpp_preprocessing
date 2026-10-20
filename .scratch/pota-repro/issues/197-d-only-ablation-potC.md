# 197 - D-only ablation: is the walk chain sufficient without the swap?

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Test whether section D of the ledger (densify -> split -> thin+walk -> recovery) ALONE seats C01, with NO slot-swap applied. If yes, D is the load-bearing change and the swap is redundant (at least for C); if no, both are load-bearing.

## Method (worker runs FULL chain, SSH works -- Host spartan)
0. Base: FRESH (non-SXC) Pot C bundle -- the 0/3+0/3 base from 98 (cite exact bar). Verify by md5 that no swapped slot is in the base. Same vehicle cure-potA @ bffefb6 (verify HEAD); same-binary ORIG control must reproduce 4/4+5/5 (98's ORIG arm) or VOID.
1. D chain on the fresh doubled C01 input (both faces, per 175 -- read 175-two-walks-two-slots.md FIRST): densify true mesh-sampled only (midpoints forbidden); split by parent surface (mesh-observable only); thin each face cloud (185 v3); walk each (verbatim walk_m144 + 144 recovery where it fires honestly). Gate each walk: closure <=2.0, single wrap, rim-truth med check-only.
2. Slot choice: use 175's measured recommendation (assemble-both-pick-better-seated vs gate-score pick -- cite which 175 recommended and apply it, do not invent a new rule). File per that recommendation.
3. Bundle: ONLY the D-chain outputs differ (byte-proofs, only-changed diff, veto-absence, 180/186 pattern).
4. E2E: upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md. Bar = 186's 3/3+3/3 (swapped-base + D). Falsifier: D-only < 3/3 (any run unseating what 186 seated) refutes sufficiency.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish via ticket Comments + final output -- never via send_message.

## Acceptance
Per-walk gates + slot-choice citation + byte-proofs + E2E x3 vs 186 + verdict (D SUFFICIENT / D NEEDS SWAP, with the refusing numbers).

## Required evidence
Ticket Comments + final output: walk gates, slot-choice applied, md5s, job IDs, per-run tallies, verdict.
