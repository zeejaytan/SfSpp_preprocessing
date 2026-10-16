# 34: C1 retest on the abl2 base, then C5 true-upstream, then Reg6

**What to move:** strict from 10–11/15 (ORIG) / 9–11/15 (fresh) toward 15/15.

**Answers:** E1

**Blocked by:** 33-admission-residue (position below).

**Status:** ready-for-agent

**Starting position — a lead catch on the C1 exoneration (ticket 29 §3 reread):** the ablation-1 arms that "exonerated" the chunk-merge threshold ran on the port-state base whose pairwise gate was still the collapsed fork 0.610 (A arms scored ORIG 0/8 — the collapse signature; the abl2 restore came later in job 33153903). On a base where the pairwise stage vetoes everything, chunk-merge cannot show an effect either way — the exoneration is UNSOUND. C1 (RS:327 `isSimilarTrans` 0.2→0.436) has never been tested on a working base. That retest is handle #1.

**Handles in order:** (1) C1 0.2→0.436 on the abl2 base (fork + P22FIX + P22FIX2 + abl2 + nothing else); (2) C5 CheckGraph site2 back to TRUE upstream — P22FIX2 set 150 (a validated relaxation), upstream is 100, current value is neither-confirmed; restore 100, one run; (3) Reg6 Cauchy scales to upstream — first confirm the fork delta exists at Reg6 (M held it at fork values; if upstream ≡ fork there, kill with no run). C6 stays (validated fix); C7 stays (inert). No combinations in this ticket.

**Valid-run rule:** asserts pass + snapshots non-empty + ORIG snapshots-strict in 9–11/15; pruned counts recorded, non-gating; fresh strict is the score; stop at the first strict 15/15 with valid ORIG.

**Rules:** shim-driven k=5/b=3; base = abl2 + nothing else; no commits; reuse tickets 29–33 bundle, scripts, fetch discipline.

- [ ] C1 retest on abl2 base: strict table + seating render
- [ ] C5 site2 → 100 (only if C1 moves nothing): strict table + seating render
- [ ] Reg6 Cauchy provenance + conditional ablation (only if prior handles move nothing)
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** if all three move nothing, a combination ticket (C1 × weighting, justified by single-exhaustion); then land the full set; then B–J E2E on admitted fragments.
