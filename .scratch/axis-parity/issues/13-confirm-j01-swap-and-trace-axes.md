# 13: Confirm the J01 swap with one executable and trace the useful axis

**What to build:** Verify the reciprocal J01 axis-file effect with one assembler executable, show the joins, and locate the stage at which the useful axis is lost on our walls.

**Answers:** E1
**Blocked by:** None. Use frozen Ticket 12 arm inputs, recorded at `04cb4a6` and Spartan run `20261121-2359_2e951d9_t12-ctl`.
**Status:** ready-for-agent
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek, one-shot diagnostic.

## A. Confirm the reciprocal result

- Reuse Ticket 12's pinned assembler, scorer and staging recipe. Compile **once** for fixed in-container input and output paths. Rebind each isolated arm's input/output directories to those same paths. Keep executable, container, flags, scorer, ordering, thread settings and non-axis inputs fixed. Record SHA-256 of the actual executed file for every launch and fail before scoring if any hash differs. Record checksums for the arm input manifests and confirm the reciprocal contrasts each differ by exactly one entire J01 axis file. Preserve candidate order and sign. Hold breaklines and wall clouds read by the assembler fixed. The donor is the same selector on the authors' walls, not their released or ground-truth axes.
- Run two interleaved repeats of each arm: all own-wall axes, own background with J01 donor, all author-wall axes, author background with J01 own. Reuse thread settings and document available seeding. Score each reference join by the existing relative scorer and corpus caveats. Report exact gained/lost seams, best attempt and frequency. Confirm the effect only if both forward swaps gain joins and both reverse swaps lose joins against their paired controls. Record any unstable or incomplete cells.
- Render all four arms at the same locked view and scale using scorer-aligned native meshes or wall clouds. Show seam close-ups for J01–J03 and J03–J06, which Ticket 12 recovered both times, with matching camera, sherd colours, and mm scale. Label absent or failed seams and show actual assembled poses. If those seam verdicts differ in this replay, retain the views and label what happened.

## B. Attribute the J01 axis

- A whole-file swap does not identify which candidate matters. On the own background, insert one author-wall candidate at a time into the corresponding rank slot of the own J01 file. Preserve the other slots and their bytes, candidate count, and input invariants. Run the three substitutions twice using the same assembler executable and paired controls. Record loaded rank, axis orientation and seam set. Treat a line as sufficient for the observed effect only if both attempts recover at least 10 of the full forward swap's common recovered seams with no baseline join lost. If several pass, trace all passing lines. If none pass, report that the isolated line is unresolved, trace all donor candidates, and keep candidate order or combination as an open explanation.
- Use Ticket 03 selector source `2e951d9`, its recorded settings and original frozen J01 walls. Add logging only in a run-local copy: in `sfs_axes/potsac.py:run_potsac_union` capture the raw proposals, cluster membership, representatives and shortlist; in `sfs_axes/joint.py:_select`, `merge_lines` and `orient_merged` capture arm costs, refinements, duplicate decisions, ordering, truncation and final signed lines. Inspect the stock profile arm in `select.py` for its equivalent pre/post-rank events. Retain stable source-to-output IDs. Require traced and untraced selector outputs to be byte-identical on both wall sets and compare to the frozen files before linking trace to replay. Keep original file order, frames, random draws and scales.
- Compare candidates to each traced donor line by sign-free angle and line separation measured at the same J01 centroid. Record sign separately. Pre-register a joint match within 10° and 10 mm, and give nearest distances, plus 5°/5 mm and 15°/20 mm sensitivity. For each stage report candidate count, matched IDs, cost/rank and drop reason on both wall sets. Identify absence at generation, loss in clustering/refinement, removal by ordering/dedup/cap, or survival in the exported file. If the reading changes with tolerance or no single line is attributable, report the ambiguity. Never feed reference labels into candidate generation or selection.

## Acceptance

- [ ] Save `replay.tsv` with columns `arm`, `repeat`, `binary_sha256`, `joins`, `changed_paths` (including patch arms), per-seam scoring, input hashes, render inventory, and a candidate trace with linked stage IDs and an output byte comparison under `C:/PR/artifacts/axis-parity-13/`. Report any skipped or incomplete cells explicitly.
- [ ] Keep instrumentation patches, geometry and scripts in the isolated Spartan run record. Hold the corpus fixed and record manifest equality. Poll each submitted job, record final sacct State/ExitCode and run-index entries. Do geometry and builds on compute nodes.
- [ ] Write a factual report with one End state in this ticket on its worktree. Leave commit, merge, close and judgement to the lead. No tracked source changes.

## Comments

One-shot diagnostic. The pinned [SfS++ method](https://arxiv.org/html/2502.13986v1#S4.SS2.SSS2) generates several axis hypotheses before pruning and refinement, so final axis files alone cannot distinguish candidate generation from selection.
