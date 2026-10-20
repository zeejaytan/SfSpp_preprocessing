# 204 - D-chain-only whole-pot Pot C (staged, pristine)

Status: open (lead 2026-10-20: cut per user's m04774 intent + m04778 answers Q1b/Q2a/Q3a; 197 was C01-only ablation, this is all-pieces)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User's original intent (m04774): apply ONLY the D chain (densify -> split -> walk -> thin) to ALL of Pot C and test whether it produces good-enough traces and assembles E2E. No swap, nothing else. Success bar (Q3a): D-all == pristine+ORIG (4/4+4/5). The 197 comparison (D-all vs C01-only 2/4+1/5) is recorded regardless.

## Method (worker runs FULL chain, SSH works -- Host spartan; COMMIT NOTHING)
0. Pristine base (Q2a, 197 pattern): A, B and C are ALL OUT of the tree. Assembly = pristine pre-38 sources (revert P22FIX feature_matching.cpp:1989, P22FIX2 ranking_system.cpp:1838, and C2-restore -- locate via ticket 38 audit + git log; build from that tree). Preprocessing = D-chain ONLY (revert T13/T21/T23/T24/T27 -- locate via 38 audit + git log; if any T fix cannot be cleanly reverted, record it as a NAMED IMPURITY, do not silently keep it). Read 197's ticket + Comments FIRST for the exact revert list that worked (jobs 33490262/63/64 ran clean on it).
1. D chain on ALL FOUR fresh Pot C bundle pieces (C01, C02, C03, C04 -- C05/C06 are ORIG-only, out of scope), each piece independently: (a) densify TRUE mesh-sampled only (midpoints forbidden per 111/146; 143 method); (b) split by parent surface, mesh-observable only, per 175 (read 175-two-walks-two-slots.md FIRST; walk each face, keep 175's slot-choice reasoning but APPLY the chain to every piece -- no gating, no skipping undoubled rims); (c) thin each face cloud with 185 v3 verbatim; (d) walk each with verbatim walk_m144 + 144 recovery where it fires honestly. Gate-record (not gate-keep) each walk: closure, single wrap, rim-truth med vs G0 donor.
2. STAGED word-check (Q1b -- recorded, CANNOT abort E2E): 201 method on all four D-loops vs ORIG (fwd_cov thin_vs_fresh per piece + C01-as-calibrator context from 201: seating needed fwd ~0.5). Record every piece's word numbers in Comments BEFORE uploading. Whatever they say, E2E runs.
3. Bundle: pristine base with the four D-loops replacing the four fresh Bl_0 (byte-proofs; recursive diff listing exactly which files differ; veto-absence check; 180/186 pattern). If any piece's D output is byte-identical to its fresh input, record it as a no-op (that is data, not failure).
4. E2E: upload the PRISTINE tree, login-node build, sbatch x3 + laptop-side poll per AGENTS.md. Arms per job: C_D_ALL + C_orig BAR + C_fresh (expect 0/4+0/5) + A_orig/A_fresh vehicle sanity (197 pattern, STEPS=4 for C arms).
5. Falsifier (Q3a): C_D_ALL == C_orig (4/4 sherd + 4/5 edge, x3 deterministic) proves D-alone sufficient for the pot. C_D_ALL < C_orig refutes D-sufficiency (record margin + which pieces still unseated + their word numbers from step 2). Secondary (always recorded): C_D_ALL vs 197's C01-only (2/4+1/5) -- did treating all pieces gain anything.

## Controls
Same-binary x3 (197 ran bit-identical T matrices x3 on C arms). Pristine+ORIG is the bar; pristine+fresh is the floor. A arms are vehicle sanity only (197 showed pristine beam nondeterminism on A -- C arms decide).

## Notes for worker
- 201's lesson travels with you: resample rewrites quantized token runs, so geometry improving while words degrade is EXPECTED on some pieces -- that is why step 2 exists. Do not hand-tune per piece; run the verbatim chain on all four.
- 194/196 (blanket thin regressed B and A) do NOT predict this ticket: different pot, staged word-check, pristine vehicle. But if D-all regresses C below fresh anywhere, say so plainly -- honest negative is a landing.
- Full-chain discipline per standing rule (m04190): do everything via SSH yourself, stage under .scratch/pota204_repro/, report via this ticket's Comments + final output, never child-to-parent send_message.

## Comments (worker -- append below, do not edit above)
