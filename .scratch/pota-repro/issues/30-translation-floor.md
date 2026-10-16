# 30: Translation floor — ablate C9, then C8/C10, one at a time

**What to move:** strict from 10/15 toward 15/15 on the repo-traceable shim binary.

**Answers:** E1

**Blocked by:** 29-assembly-provenance (position below).

**Status:** ready-for-agent

**Starting position (ticket 29, jobs 33152327/33153903):** restoring the pairwise axis gate to true-upstream 0.436 moves ORIG 0/8→8/8+14/15 binary, but laptop strict stalls at 10/15 (fresh 9/15) — rotations pass almost everywhere (worst 4.1°), failures are pure translation (10.4–26.7mm) over a systematic ~7–9mm floor. Provenance list lives in ticket 29 §2: C9 (registration-correspondence floor `>3→>8`, two sites, 869e696) thins true correspondences before ICP and is the prime suspect; C8 (CountInlier floor) and C10 (solver numerics) follow. Plus a noise caveat from 29 §3: identical code scored ORIG 0/8 vs 2/8 across runs while fresh reproduced exactly — size the ORIG noise band with a same-binary repeat before judging 14/15-vs-15/15.

**Rules:** shim-driven k=5/b=3 with LINK-SHIM-OK + DRIVER-SHIM-OK asserts every run; non-empty transform snapshots; same-binary ORIG control (ORIG ≠ 8/8+15/15 voids that run); ONE ablation per run (C9 first — revert one or both sites? one variable: do one site, then the other only if the first moves nothing); no commits in either repo; reuse ticket 29's bundle, strict script (`artifacts/pota29/p29_strict.py`), and render script.

- [ ] Same-binary repeat of the abl2 C arms: ORIG noise band on binary + strict
- [ ] C9 ablation (site-by-site): ORIG control decides each; strict table + seating render per moving arm
- [ ] C8, then C10, only if C9 moves nothing — stop at the first arm that reaches strict 15/15 with ORIG 8/8+15/15 valid
- [ ] Laptop poll per sbatch via sacct directly; job IDs + sacct states; Comments-only ticket edits

**Successor:** land the full set on the reproduced strict run; then B–J E2E on admitted fragments.
