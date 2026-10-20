# 194 - Thin-then-walk as default: non-regression on clean Pot B

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Prove the thin-then-walk default is HARMLESS on clean rims: force-apply the 185 v3 recipe to Pot B's already-single SXC Bl_0 loops, bundle, E2E x3 vs 93's bar. If tallies match 93, the default is safe everywhere (cures doubled, keeps clean).

## Method (worker runs FULL chain, SSH works -- Host spartan)
1. Thin: apply 185 v3 (thin TRUE strip to centreline, uniform 1.8mm resample, verbatim walk_m144) to each of B02-B09's clean single SXC Bl_0 loops (B01 forest excluded, with 78 per 93/187). Gate each loop: closure <=2.0, single wrap, rim-truth med (check-only, expect ~0.5-1.15 per 187).
2. Falsifier (own in advance): any loop whose rim-truth med worsens by >0.5mm vs its unthinned SXC input is REFUSED (not bundled) -- thinning must not move clean dots off the rim.
3. Bundle: rebuild with ONLY the thinned Bl_0 slots changed (byte-proofs, only-changed diff, veto-absence, 180/186 pattern).
4. E2E: upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md. Bar = 93 SXC (cite tallies from 93/187). Verdict: MATCH (>= bar, no piece unseated that 93 seated) or REGRESSION (name the dropping piece + numbers).

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message.

## Acceptance
Per-loop gates + falsifier check + bundle byte-proofs + E2E tallies x3 vs 93 + verdict (safe-default / regression with refusing numbers).

## Required evidence
Ticket Comments + final output: loop gates, refused loops if any, md5s, job IDs, per-run tallies, verdict.
