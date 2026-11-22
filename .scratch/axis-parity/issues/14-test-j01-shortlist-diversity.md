# 14: Can our walls supply the useful J01 axis at the same shortlist size?

**What to build:** Test whether J01 lines already generated from our surfaces survive the existing refinement once admitted, and whether a reference-blind shortlist can recover their benefit at the existing capacity.

**Answers:** E1
**Blocked by:** None. Use Ticket 13's saved J01 trace and Ticket 03's frozen surface and assembly inputs.
**Status:** ready-for-agent
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek, one-shot Spartan diagnostic.

## Pins and files

Use selector commit `2e951d9`, normalized union, stock tri selector and the exact Ticket 13 surface order and RNG settings. Record pin, wall hashes, seed list and native units. Use Ticket 13's executable and fixed bind recipe from the resolved ticket. Its run is `/data/gpfs/projects/punim2657/SfSpp/runs/20261122-1612_651fee0_t13-j01-recip`. Hash the executable on every Pot J launch. For Pot A use a separate executable compiled once with the same recipe and POT_A header; reuse it for all A cells. Re-stage from frozen corpus and Ticket 03 artifacts if any old trees have been retired. Only run-local diagnostic files may change. Keep breaklines, scoring, assembly settings, and exported candidate cap fixed. No corpus writes, shipped code changes, or default changes.

The run-local selector changes belong in `sfs_axes/select.py` and `sfs_axes/joint.py`. In `select.py:select_union_lines`, replace only the index selection at the stock-profile `np.argsort(-sizes, kind="stable")[:PROFILE_BASINS]` loop with a call to `shortlist_indices(reps, sizes, centre, size)`, defined in `select.py`. In `joint.py:_candidates`, call the same helper and pass the existing centre and size through the normal and thickness call sites. Return selected indices in original stable draw-count order so downstream ties preserve their existing policy. Baseline mode must reproduce frozen axis files byte-for-byte. Leave all scoring, refinement, cluster generation, merge, orientation and caps unchanged.

## A. Forced admission, for diagnosis

On J01, replay the original shortlist (top 60 by draw count) and two forced shortlists. In each forced shortlist, replace the last selected cluster with exactly one of the two saved representatives: raw tracks `t00621` and `t01111` in Ticket 13's own-wall trace, draw-count ranks 88 and 102 as recorded. Resolve tracks to basin columns from the saved representative records and require exact 6-vector equality against the newly generated pool before use. Break on a provenance mismatch. Log ancestry through each arm's candidate costs, refinement, merge and export. Score the outputs blind, then compare to the donor at the fixed J01 centroid (10° and 10 mm, sign separately). If a matching line is exported, replay its resulting whole J01 file on our frozen assembly background against the own-wall baseline, two interleaved attempts each. If both forced variants export a match, test both. If neither exports a match, record the first drop and stop with no blind trial.

Continue only if at least one forced arm gains at least two net scored Pot J joins in each attempt with no baseline scored seam lost in either paired contrast. Ground-truth and donor lines are evaluation aids. The forced arms cannot count as a deployable result.

## B. One reference-blind shortlist, same capacity

Keep the top 52 clusters by stable descending draw count. Fill the final eight seats by greedy farthest-first selection from the remaining representatives. For each remaining line compute its minimum distance to any already selected line. Use `max(angle_deg/10, centroid_foot_distance_mm/(0.10*piece_size_mm))` for each pair. The angle is sign-free and each foot is the closest point on that line to the same sherd centroid. Maximise that minimum, breaking exact ties by earlier stable draw-count order. Keep every candidate if there are 60 or fewer. Reject non-finite lines using the existing input validity path. In case of zero or non-finite piece size, use the baseline indices. No sherd labels, donor inputs, or per-pot settings enter the rule.

Apply the blind rule to all named sherds of Pot J and Pot A on their own walls. Run paired baseline and blind assembly twice per pot with one executable per pot. Report the repeat-level seam sets, gained and lost IDs, and best-of-two with its frequency. A useful blind result gains at least two net joins in **both** J attempts with no baseline join lost, and preserves **15/15** joins in both Pot A controls and both blind arms. Report separately whether J reaches 8/11 sherds and 16/21 joins. Keep successful settings experimental.

## Evidence and acceptance

- Export `selector.tsv` with columns pot, sherd, mode (baseline, force88, force102, blind), pool_n, shortlist_n, export_n, pool_sha256, axes_sha256. Include selected basin IDs, original ranks and final lineage in `shortlist.tsv` (pot, sherd, mode, basin_id, original_rank, selected, exported). Record baseline frozen byte comparisons for every baseline in `baseline.tsv` (pot, sherd, frozen_sha256, replay_sha256).
- Export `replay.tsv` (pot, arm, repeat, executable_sha256, joins) and `seams.tsv` (pot, arm, repeat, seam, pass) with arm labels baseline, force88, force102, blind. Use repeat 1 and 2. Provide `phase.tsv` (mode, state, reason) for force88, force102 and blind, with states ran or skipped. Retain the input manifests, fitted line geometry and executable hash log. Render J01 axes before/after and locked views of J01–J03 and J03–J06 when assembly runs, with units and scores. Deliver `renders.tsv` (path, kind) with paths relative to the evidence directory.
- Save `jobs.tsv` (job_id, run_id, state, exit_code, polled, indexed) with all submissions and `corpus_before.md5` and `corpus_after.md5`. Poll each job, keep final accounting and patches on Spartan and fetch the small record to `C:/PR/artifacts/axis-parity-14/`.
- Run the pinned selector's existing tests on a compute node with `python -m pytest tests -q`. Check a stock baseline byte comparison before any trial. Record all failures, test output, decisions required by the preset gates and one End state in this ticket's worktree. No commits, merge or close by the worker.

## Comments

One-shot diagnostic. [SfS++ §IV-B.2](https://arxiv.org/html/2502.13986v1#S4.SS2.SSS2) uses multiple proposals before refinement. Ticket 13 establishes that the current draw-count cutoff misses two useful representatives on J01. The fixed-cap comparison tests recovery without changing the number of lines the estimator evaluates.
