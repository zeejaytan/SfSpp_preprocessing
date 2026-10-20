# 196 - Default chain on Pot A: control must hold

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Pot A is the lane control (8/8+15/15). Run the FULL default chain (densify -> split -> thin+walk -> bundle -> E2E x3) on Pot A's rims and prove the control still holds. The default cannot ship if it moves the control.

## Method (worker runs FULL chain, SSH works -- Host spartan)
0. Densify (143): measure spacing per A loop; true mesh-sampled densify only if coarser than ~1.8mm (midpoints FORBIDDEN per 111/146); else record + close vacuous.
1. Split (175 rule, read 175-two-walks-two-slots.md): mesh-observable only, no ORIG. Expect one face cloud per clean single; two faces = new evidence.
2. Thin: 185 v3 per face cloud. Gate: closure <=2.0, single wrap, rim-truth med check-only.
3. Falsifier (own in advance): any loop worsening rim-truth by >0.5mm vs input is REFUSED, not bundled.
4. Bundle: ONLY changed Bl_0 slots (byte-proofs, only-changed diff, veto-absence, 180/186 pattern).
5. E2E: same vehicle cure-potA @ bffefb6 (verify HEAD -- Pot A-diagnosis changes live here); same-binary ORIG control must reproduce 8/8+15/15 or VOID. sbatch x3 + laptop-side poll per AGENTS.md. Bar = 8/8+15/15 (cite owning ticket). Verdict MATCH or REGRESSION (name piece + numbers).

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish via ticket Comments + final output -- never via send_message.

## Acceptance
Per-loop gates + falsifier + byte-proofs + E2E x3 vs 8/8+15/15 + verdict.

## Required evidence
Ticket Comments + final output: loop gates, md5s, job IDs, per-run tallies, verdict.
