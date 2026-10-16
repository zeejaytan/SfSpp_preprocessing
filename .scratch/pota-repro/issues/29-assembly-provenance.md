# 29: Assembly-tree provenance — ablate the drift, rebuild the cure

**What to build:** a repo-traceable assembly binary that reproduces the cure — by finding which tree the proven binary came from.

**Answers:** E1

**Blocked by:** 28-port-and-land (void diagnosis below).

**Status:** ready-for-agent

**Starting position (ticket 28, jobs 33143346/33145079):** all hunks verified byte-identical; the repo-built PIPELINE reproduces fully (T21×1, 4 skips, Bl0 exact, gate 15/15, zero teleports). But the repo-built ASSEMBLY run is VOID: ORIG scores 2/8+1/15 (must be 8/8+15/15), so nothing about the fresh arm counts. Named suspect: the assembly fork tree is not upstream+hunks — live `isSimilarTrans` 0.436→0.2 chunk-merge threshold (commit 869e696), `CheckOpposingNormals` commented out (dead), GGCE/combined_score leftovers. Yet ticket 27's cure binary (from staged `sfs_main/sfs_p22fix_src/`) held ORIG 8/8+15/15. So: diff the proven base against the repo checkout (`sfspreproc-docker` @ 11f4827) and find what the cure actually depended on.

**Rules:** provenance first (tree diff, commit archaeology), then ONE ablation at a time in scratch (first candidate: 0.2→0.436 — if ORIG restores to 8/8+15/15, the drift is the cause). Do NOT commit anything in either repo. Fix the transform capture the 28 run lost (fork binary writes cwd-relative `results_*/` — bind-mount a capture dir or run from a known cwd; snapshots must be non-empty). Same-binary ORIG control in every assembly job (any ORIG ≠ 8/8+15/15 voids that job, not the hypothesis).

- [ ] Tree diff: proven cure base vs repo checkout — full list of live deltas beyond the four hunks, with the commit that introduced each
- [ ] Ablation run(s): restore candidates one at a time; ORIG control decides each
- [ ] Cure reproduction on the repo-traceable binary: gate + E2E k=5/b=3, binary 8/8+15/15 + STRICT relative-edges 15/15, with captured transforms + seating render
- [ ] Laptop poll per sbatch (`sacct` directly); job IDs + sacct states; no commits; Comments-only edits

**Successor:** land the full set (T21+T23+T24+T27+RP ablation+CheckGraph-150+provenance fix) on the reproduced run; then B–J E2E on admitted fragments.
