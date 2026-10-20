# 187 - Thin-loop roll-out: Pot B

Status: landed (lead 2026-10-20: census verified, vacuous close accepted -- zero doubled Bl_0, falsifier daylight on all axes; E2E decline accepted, rerun would byte-repeat 93)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Apply the 185 thin-then-walk cure to every doubled rim edge of Pot B, bundle, and E2E x3 vs this pot's established bar (cite the prior ticket that set it).

## Method (worker runs FULL chain, SSH works -- Host spartan)
1. Census: for each rim piece, test for doubling with key-free signals (closure distance, arc vs plan perimeter, D-token count per the 179 recipe). Name which edges are doubled.
2. Cure: apply the 185 v3 recipe (thin TRUE strip to centreline, uniform 1.8mm resample, verbatim walk_m144) to each doubled edge. Gate each loop: closure <=2.0, single wrap, rim-truth med where an author key exists (check-only).
3. Bundle: rebuild this pot's bundle with ONLY the cured Bl_0 slots changed (byte-proofs, only-changed-diff, veto-absence record, same guards as 180/186).
4. E2E: upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md, sacct tallies. Own a falsifier in advance.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message (child-to-parent messaging does not exist).

## Acceptance
Per-piece doubling census + per-loop gates + bundle byte-proofs + E2E tallies x3 (Total/pruned/sherd/edge) vs the pot's bar + honest verdict (pass / honest negative with the refusing numbers).

## Required evidence
Ticket Comments + final output: census numbers, loop gates, md5s, job IDs, per-run tallies, verdict.

## Comments (worker, 2026-10-20 -- HONEST NEGATIVE, rollout vacuous for Pot B; COMMIT NOTHING)

**Status: results-in. Verdict: honest negative -- Pot B has ZERO doubled Bl_0 edges in its bundle of record, so the 185 v3 thin-then-walk cure has no target. No bundle rebuilt, no E2E run (re-running would byte-repeat 93's landed jobs). The refusing numbers are below.**

**0. Boundary kept.** Dataset read-only; no repo sources touched (assembler never entered); production checkouts untouched; tickets 39-186 read-only (numbers quoted from their Comments); bundle verified read-only (`md5sum -c` only); nothing committed; only this Comments section added.

**1. Census (login-node numpy, key-free signals per 179 recipe: closure / arc-vs-plan-perimeter ratio / D-token count at 0.15 bins; plan perimeter = angle-sorted PCA-plane polygon). Bundle of record = 93 SXC (`pota93_bundle_B_SXC`), vehicle HEAD still `bffefb6` (same as 93).**

| piece | slot (assembler-facing = Bl_0) | n | arc | perim | ratio | closure | gaps>5 | D-tokens | verdict |
|---|---|---|---|---|---|---|---|---|---|
| B01 | Bl_0 (forest, untouched by 93) | 1069 | 1948.5 | 11466.7 | 0.17 | 69.31 | 25 | 54 | SCATTER, not doubling (no coherent strip to thin; interior loop missing -- with 78 per 93) |
| B02 | SXC Bl_0 (= fresh Bl_1) | 116 | 259.1 | 247.1 | 1.05 | 1.92 | 1 | 4 | SINGLE loop (one pre-existing 43mm jump, byte-identical move from 93) |
| B03 | SXC Bl_0 | 133 | 250.8 | 248.1 | 1.01 | 1.64 | 0 | 3 | SINGLE, clean |
| B04 | SXC Bl_0 | 127 | 239.0 | 237.1 | 1.01 | 1.90 | 0 | 3 | SINGLE, clean |
| B05 | SXC Bl_0 | 121 | 229.3 | 227.7 | 1.01 | 1.92 | 0 | 4 | SINGLE, clean |
| B06 | SXC Bl_0 | 99 | 184.2 | 184.4 | 1.00 | 1.68 | 0 | 2 | SINGLE, clean |
| B07 | SXC Bl_0 | 97 | 180.8 | 181.0 | 1.00 | 1.91 | 0 | 3 | SINGLE, clean |
| B08 | SXC Bl_0 | 95 | 176.8 | 177.0 | 1.00 | 1.72 | 0 | 3 | SINGLE, clean |
| B09 | SXC Bl_0 | 70 | 132.8 | 134.0 | 0.99 | 1.92 | 0 | 3 | SINGLE, clean |

Author ORIG Bl_0 reference (check-only): all 9 single closed loops, closure 1.80, ratio 0.99-1.01, 2-3 D-tokens. The 179 doubling signature (C01: ratio 1.82, closure 17.67, 34 tokens) appears ONLY in the retired fresh-Bl_0 slots (now SXC-Bl_1 for B02-B09: ratios 1.35-2.23, closures 36-83, 19-38 tokens) -- already cured by 93's slot exchange, not by thinning. Rim-truth (check-only): SXC Bl_0 vs ORIG Bl_0 med 0.49-1.15mm for B02-B09 (B02 1.15/68% cov -- partial arc, see s3), B01 4.43 (forest, exonerated from this ticket).

**2. Falsifier (owned in advance, NOT triggered).** This negative is refuted if any SXC Bl_0 shows ratio >= 1.2 with closure > 2.0 and D-tokens >= 10. Observed maxima among B02-B09: ratio 1.05, closure 1.92, tokens 4 -- daylight on all three. B01 fails differently (scatter, ratio 0.17) and has no strip to thin.

**3. Why no bundle / no E2E (refusing numbers).** (a) Zero Bl_0 slots qualify for the cure, so a `rebuilt bundle with ONLY cured slots changed' is bit-identical to the 93 SXC bundle -- verified intact just now (`md5sum -c pota93_B_SXC_BL_md5.txt`: all Bl_0 OK; vehicle HEAD `bffefb6` unchanged). (b) E2E x3 on an identical bundle + identical vehicle reproduces 93's landed jobs 33387265/66/67 exactly (SXC 5/9+3/15, 6/9+5/15, 6/9+5/15 vs bar; ORIG 9/9+15/15 x3; A arms 8/8+15/15) -- ~1h of GPU to re-prove a landed result, declined per YAGNI. (c) Thin-then-walk would HURT the one imperfect piece: B02's SXC loop is a partial single arc (116 pts, 68% station coverage, rev med 1.60); the v3 recipe shrinks arcs (C: arc -5%, 476 dots -> 204), it cannot regrow missing arc -- B02's gap is a densify/completeness ticket, explicitly out of scope per 93's rules. (d) No TRUE-strip inputs exist for any Pot B piece (p173 bags are C01-only); manufacturing them to thin already-single loops adds a variable for zero gain.

**4. Bar cited (ticket 93, the prior ticket that set it).** Pot B established bar: SXC 6/9+5/15 (R2/R3 converged, binaries; R1 5/9+3/15) vs fresh-best 4/9+2/15 (39 R1); same-vehicle ORIG ceiling 9/9+15/15 (114/76-77). Standing recommendation from 93 unchanged: B needs no rim re-roll; piece-2 flip + 2/5/8 cluster are assembly-lane data; B01 forest numbers are 78's input. Next thin-rollout ticket (188/D): run this same census first -- if that pot's SXC/current Bl_0s are already single (as here), close vacuous without E2E.

**5. Evidence.** Login-node scripts `/tmp/p187_census.py` + `/tmp/p187_census2.py` (Spartan scratch, outside repo); bundle proofs re-verified live (`md5sum -c` all-Bl_0 OK, vehicle `bffefb6`); no new files staged, no jobs cut (no job IDs -- nothing was submitted).
