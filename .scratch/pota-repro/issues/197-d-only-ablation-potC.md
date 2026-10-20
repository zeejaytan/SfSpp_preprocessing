# 197 - D-only ablation: is the walk chain sufficient without the swap?

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Test whether section D of the ledger (densify -> split -> thin+walk -> recovery) ALONE seats C01, with NO slot-swap applied. If yes, D is the load-bearing change and the swap is redundant (at least for C); if no, both are load-bearing.

## Method (worker runs FULL chain, SSH works -- Host spartan)
0. Pristine base (the point of this ticket): A, B and C are ALL OUT. Assembly = pristine pre-38 sources (revert P22FIX feature_matching.cpp:1989, P22FIX2 ranking_system.cpp:1838, and C2-restore -- locate via ticket 38 audit + git log; build from that tree). Preprocessing = D-chain ONLY (revert T13/T21/T23/T24/T27 -- locate via 38 audit + git log; if any T fix cannot be cleanly reverted, record it as a NAMED IMPURITY, do not silently keep it). Bundle = FRESH non-SXC Pot C (no swap anywhere; md5-verify). Controls in the same pristine job: (i) pristine + shipped ORIG rims (this is the bar -- record what it seats), (ii) pristine + fresh unchained rims (expect ~0/3+0/3).
1. D chain on the fresh doubled C01 input (both faces, per 175 -- read 175-two-walks-two-slots.md FIRST): densify true mesh-sampled only (midpoints forbidden); split by parent surface (mesh-observable only); thin each face cloud (185 v3); walk each (verbatim walk_m144 + 144 recovery where it fires honestly). Gate each walk: closure <=2.0, single wrap, rim-truth med check-only.
2. Slot choice: use 175's measured recommendation (cite which + apply; no new rules).
3. Bundle: ONLY the D-chain outputs differ (byte-proofs, only-changed diff, veto-absence, 180/186 pattern).
4. E2E: upload the PRISTINE tree (not cure-potA), login-node build, sbatch x3 + laptop-side poll per AGENTS.md. Falsifier: pristine+D < pristine+ORIG (any run seating less) refutes D-sufficiency; pristine+D == pristine+ORIG (and C01 seated) proves D is the ONLY load-bearing change.
