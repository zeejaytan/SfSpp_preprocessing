# 26: RP-level starvation (pairs 2-8/4-8, 1-3/3-5/3-6)

**What to build:** the pairwise fix that feeds true p8/p3 candidates past RP — the last known barrier to strict 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 25-remaining-vetoes (starvation evidence below).

**Status:** ready-for-agent

**Starting position (ticket 25, job 33133724, ORIG control valid):** p8 and p3 are STARVED, not vetoed — zero true graphs reach PLAUS (nearest 128mm+ / 60mm+ off). Upstream location: pair 2-8 PP support matches ORIG (14–35 inliers at axis 0.11–0.39) but no true candidate survives RP (axis≈0 ones show inlier=0; supported ones at axis 0.44–1.5 die on the 0.436 axis gate/score). Pair 3-2 is a non-edge (p3 joins via printless 1-3/3-5/3-6). Do NOT relax PC_ or CheckGraph-150 on current evidence. Staged sources: Spartan `sfs_main/sfs_p22fix_src/` (verify diff first); P25DIAG print line reusable.

**Rules:** RP-survival prints first for pairs 2-8/4-8 (+1-3/3-5/3-6 for p3): where exactly true candidates die (inlier count? axis gate? score threshold?). Minimal search-side fix for the proven cause only. Build from committed sources in a fresh Spartan-side experiment copy. Same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void). If strict 15/15 passes at k=5/b=3, report SFS-T24 + RP ablation + CheckGraph-150 + this fix as ONE landable set; if not, report — no partial claims. Acceptance is the STRICT bar only.

- [ ] RP-survival prints per pair: the exact gate that kills true candidates, with ORIG-arm comparison in the same job
- [ ] Minimal fix; rerun gate + E2E k=5/b=3, strict 15/15
- [ ] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.
