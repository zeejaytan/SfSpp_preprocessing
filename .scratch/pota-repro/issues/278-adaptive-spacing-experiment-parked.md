# 278 — the stale Spartan checkout held an experiment main never received

**Status:** ready-for-human
**Answers:** none
**Needs-eye:** no

## What was found

The canonical Spartan checkout /data/gpfs/projects/punim2657/sfs_preprocessing sat at f4add97 and
could not 'git pull --ff-only'. The 361 skip-worktree flags were the real blocker, so the local
content of those paths was archived to SfSpp/attic/sfs_preprocessing-skipworktree-20261024.tar.gz
before anything else happened.

Only 69 of the 361 flagged paths still had content (411,570,807 B); 292 were missing from the
working tree, and 'git status' had hidden that too. Of the fourteen paths origin/main keeps, twelve
differ from the index — and two of those are code:

| File | main | local (archived) | What the difference is |
|---|---|---|---|
| mesh_processing_headless.cpp | 109,992 B / 2,618 lines, last touched 2026-10-24 (b289e87) | 89,592 B / 2,234 lines, dated 2025-12-12 | a density-adaptive parameterisation main does not have |
| comprehensive_comparison.sh | 7,882 B / 203 lines, 70fe5cc 2025-11-19 | 8,164 B / 230 lines, 2025-12-07 | a whole-file rewrite, different input trees |

Measured three ways (index blob, origin/main blob, working tree): for 13 of the 14 paths the index
already equals main, so the pull restores main and only the working copy is at stake.
mesh_processing_headless.cpp is the exception, with three distinct versions.

## The experiment, in plain terms

The archived copy sizes four parameters from the point cloud itself instead of hard-coding them:

- estimatePointSpacing() at line 286 — kNN spacing over a 500-point sample, clamped 0.1–10 mm
- adaptiveCGALNeighbors() at line 321, used at line 513
- adaptiveRegionGrowingK() at line 333, used at line 1779
- adaptiveMinCluster() at line 345, used at line 1780

None of those names occurs anywhere in the 2,618-line main version (grep count 0). The idea is that
a fixed neighbourhood size is wrong at one end of a density range or the other — here as a local
experiment, never committed, never run against main's later code.

Main meanwhile has work the local file predates: TICKET 234 getenv (4 hits in main, 0 local) and a
curvatureThreshold argument on surfaceSegmentation(). Neither file is a superset of the other, so
this is a graft, not a merge.

## What is kept here

- ticket278_files/mesh_processing_headless.cpp — the archived local copy, byte-identical to the
  tarball member (cmp clean).
- ticket278_files/comprehensive_comparison.sh — likewise.
- ticket278_files/mesh_processing_headless.local-only.patch — diff -u main to local, so the
  local-only content can be read without diffing two files by hand.

The same bytes also live in the attic tarball on Spartan and on the laptop under
C:/PR/.scratch/workspace-restructure/archive/sfs_preprocessing-skipworktree-20261024/. This ticket
exists so the experiment is greppable in the repository instead of surviving only inside a tarball.

## Done when

Either
- the four adaptive functions are grafted onto current main in a ticket of their own, with a
  before/after on a named pot showing the parameter choice holding at both density extremes, or
- a decision is recorded here that the experiment is not worth pursuing, with the reason.

## Why it is worth one line rather than silence

A 121-line parameterisation idea that exists only in a tar file is one disk failure away from being
nobody's work. Recording it costs 89 KB.
