# 19: Fork-vs-upstream audit — preprocessing (validate every change, document it)

**Answers:** E1

**Blocked by:** nothing — read-only until the doc says otherwise

**Status:** ready-for-agent

**Needs-eye:** none — diff classification, no geometry claim.

## Why this ticket exists

This fork's extraction code has ~2 years of layered changes over
`DominicoRyu/SfSpp_preprocessing`: the cluster lineage's headless
adaptation (~20 research commits), then our tickets (04 vote+guards, 14
patch rims, T07/T17 guards, merge loop, noise-filter seam, 1.9mm
resampling, KNN bound, unit-lie fixes, CTest seam). No single document
says what each change does and how it relates to the paper. The Nov-2025
`COMPREHENSIVE_CODE_DIFFERENCES.md` (assembly repo root — note the wrong
repo) tried this for the preprocessing side and is now stale: it predates
every ticket above. This ticket supersedes it for our changes (cite it,
don't duplicate its headless-adaptation analysis where still accurate).

## Baselines (pin these; if upstream moves, re-pin and say so)

- Upstream: `upstream/main` @ `d5ee6865` (fetch ref, 2026-10-01).
- Ours: `origin/HEAD` at time of audit (record the SHA in the doc).
- Upstream keeps `edgeline_extraction.cpp` + `mesh_processing.cpp` at ROOT;
  ours live as `*_headless.cpp` under `original_nurbs_preprocessing/`.
  Compare pairwise (upstream root file ↔ our headless file), not by path.

## Method (in this order — attribution before classification)

1. For each source file: `git diff upstream/main HEAD -- <file>`, grouped
   by hunk. Attribute every hunk to a layer with `git log -S` / `git blame`:
   (a) cluster-lineage headless adaptation, (b) our ticketed changes
   (cite ticket), (c) unattributed (neither — these are the findings).
2. New files inventory (`surface_classify.*`, `ticket04_*`, `ticket14_*`,
   `boundary_filter.*`, `tests/`, run/build scripts, MATLAB-adjacent):
   one line each — what it is, which ticket, paper relation.
3. Classify every OUR hunk (cluster layer summarized, not re-litigated
   except where it affects paper behavior):
   - PAPER-MATCH (implements §IV-B1 as written),
   - DEVIATION-measured (differs, with the ticket + numbers),
   - ROBUSTNESS-no-behavior (guards, loud-failures, skips — prove no
     behavior change on sane input or cite the ticket that did),
   - INFRA (build/scripts/tests/docs — no runtime effect),
   - UNATTRIBUTED (found something: file as a new ticket or explicitly
     accept here with reason — no third option).
4. Cross-check the paper-relation labels against ticket 16's deviation
   list — any hunk ticket 16 doesn't know about is itself a finding.

## Deliverable (the "then document")

`FORK_VS_UPSTREAM.md` at repo root: pinned SHAs, per-file hunk table
(file, hunk, layer, classification, ticket/paper-line), new-file
inventory, unattributed list (empty or ticketed). Replaces the Nov-2025
doc for our changes; says so in its first paragraph.

## Acceptance criteria

- [ ] Doc exists with pinned SHAs and the per-file table
- [ ] Every OUR hunk classified; every UNATTRIBUTED either ticketed or
      accepted-with-reason in the doc
- [ ] Ticket-16 cross-check done (no unknown-to-16 paper-behavior hunk)
- [ ] Nothing changed in code in THIS ticket (audit only)
