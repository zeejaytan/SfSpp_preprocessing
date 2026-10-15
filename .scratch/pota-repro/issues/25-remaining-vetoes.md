# 25: Remaining profile vetoes (p8 flip, p3 orphan)

**What to build:** the veto fix that closes Pot A — diagnose why the profile gate eats the true p8 and p3 seatings, fix minimally, reach strict 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 24-clean-rim-rerun (numbers below).

**Status:** ready-for-agent

**Starting position (ticket 24, job 33132499, ORIG control valid):** with the T14 patch poison skipped for p2 and the two ORIG-validated relaxations (RP ablation + CheckGraph-150), fresh E2E stands at strict 6/8+10/15 — p2 seated strict-OK (1.85°/4.43mm, attractor gone). Two pieces remain: p3 unplaced (its only non-junk graphs are orphaned 13467@250 plus the vetoed full assembly) and p8 flipped ~172° (winner is all-but-3@454 with true p2 but flipped p8; the full true assembly 12345678@363 is PC_-vetoed). Open from ticket 24: true-p8 vetoed vs outscored — the prints can't separate p8's pose, so extend the P22FIX3 rim-centroid instrumentation to p8 and p3 first, then decide.

**Rules:** diagnose before touching (pose prints for p8/p3 true-vs-seated, what each veto eats). Candidate fix directions only after measurement — the PC_ veto stays authoritative until a content cause is proven (no gutting). Staged sources: Spartan `sfs_main/sfs_p22fix_src/` (verify diff first). SFS-T24 (skip patch append for p2) + both relaxations land WITH the veto fix as one set, only if strict 15/15 passes — no partial landing. Same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void). Acceptance is the STRICT bar only.

- [ ] Extend pose prints to p8/p3: true seating vetoed or merely outscored, per veto (PLAUS-PC_, Overlap_), with rim-centroid evidence
- [ ] Minimal veto fix for the proven cause; rerun gate + E2E k=5/b=3, strict 15/15
- [ ] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.
