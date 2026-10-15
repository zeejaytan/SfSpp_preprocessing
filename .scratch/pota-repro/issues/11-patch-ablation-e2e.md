# 11: Ablate patch segments on p2–p5, re-run E2E

**What to build:** the test of 06's prime suspect — whether the ticket-14 patch-rim segments on pieces 2–5 are what exploded the search forest (522 vs 124) and sank E2E to 4/8 + 3/15.

**Answers:** E1

**Blocked by:** 06-gate-e2e-rerun (evidence above).

**Status:** ready-for-agent

**Background (from 06, jobs 33051437/33054720/33055873):** gate 15/15 on fresh _0 rims; E2E fresh 4/8 + 3/15 vs ORIG 8/8 + 15/15 same binary; correct core {1,6,7}; 4,5,8 flung; 2,3 unplaced. Patch-augmented rims on p02–p05 are byte-different vs the Sept-28 bundle that assembled 8/8+15/15; p01,p06–p08 identical. Spartan leftovers to reuse: `pota06_fresh/`, `pota06_bundle/SfS_pp/`, `sfs_main/pota06_verify_33054720/`.

- [ ] Rebuild the fresh bundle with ticket-14 patch segments removed on p2–p5 (nothing else changed), re-run gate probe + E2E at k=5/b=3 with the same-binary ORIG arm alongside
- [ ] Report: gate x/15, E2E x/8 + x/15 fresh vs ORIG, hypothesis-forest size fresh vs ORIG, per-piece placement table
- [ ] Verdict with numbers: patch segments are / are not the E2E killer. If E2E still short, name the next suspect from the per-pair evidence (not a guess)
- [ ] Laptop poll per sbatch with final sacct State/ExitCode in ticket; Comments-only edits; no commits; E1 update proposal in Comments
