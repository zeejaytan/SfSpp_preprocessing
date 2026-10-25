# 277 — The mesh stage must not silently keep size order when it has no axis file

Answers: E1
Status: in-progress
Working in: chat on Thinkbook16 (2026-10-25)
Branch: 277-axis-file-must-shout, in /c/PR/worktrees/sfs/277
Needs-eye: no

## Why

classifyAndOrderPaper234 (mesh_processing_headless.cpp:1990) decides which of the two big
clusters is the interior surface by casting rays from each point along its normal to the
symmetry axis read from SFS_AXIS_FILE (:1994 onwards).

When SFS_AXIS_FILE is unset the function prints
`[PAPER-234] classify: no SFS_AXIS_FILE, keep size order` and leaves clusters in size
order. No error, no non-zero exit. The run continues and produces a full set of surfaces
and breaklines.

The labels are then wrong in a way nothing downstream can see: Surface_0 is whichever
cluster happens to be larger, so **Bl0 and Bl1 stop corresponding to the author's Bl0 and
Bl1**. A 2026-10-24 run hit this (ticket 275 Phase 0): it scored med 5.8 mm / cov 0.00 and
looked exactly like a method failure until the axis file was restored.

This is the worst shape of defect we have: a wrong answer that reads as a real result.

## What to do

Make the missing axis file loud, in this order of preference:

1. Exit non-zero with a message naming the variable — preferred, since every pipeline run
   in this repo sets it.
2. If some callers legitimately run without it (check first; record who and why), keep the
   fallback but print a banner that cannot be missed and write a marker file next to the
   outputs so a later reader can see which runs were mislabelled.

Do not change the classification itself, and do not invent a default axis.

## Acceptance

- A run with SFS_AXIS_FILE unset either fails non-zero with the variable named, or writes
  the marker and prints the banner.
- The six guard lanes of ticket 271 reproduce bit-identically with the variable set.
- The log line quoted above no longer appears without an accompanying loud warning.

## Evidence to report

- the new message text and where it is emitted
- the guard-lane reproduction table
- what callers were found that do not set the variable, and their justification
