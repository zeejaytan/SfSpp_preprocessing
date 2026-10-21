# Ticket 232: P22 turn-away diagnosis (split-plan check + divergence point)

Status: ready-for-agent
Answers: none (Pot D bridge class; feeds the R6-rule 4th-leg hole + bridge-class record)

## Goal
Two ordered questions on Pot D Piece 22, whose 221-kept lanes are stubs (o0 med 3.37/cov 32.5, o1 med 2.70/47.2, slot-corrected; zoom: C:/PR/SfSpp_preprocessing/.scratch/pota228/p228_P22_zoom_ours.png):
1. SPLIT-PLAN CHECK: is the author's line cut right on the edge of our 2 surface planes? (i.e. the split is correct and only the walk failed). Method: the 229 sharpness instrument (baseline/line/control triple, ticket 229 Comments) applied to author-lane dots vs the S0/S1 ladder faces (221 thr_* dirs on Spartan) + dense ORIG cloud. Verdict SPLIT-OK (author on-edge) or SPLIT-OFF (author mid-surface).
2. TURN-AWAY POINT: the exact dot where our trace leaves the author line (first our-dot >2mm from either author lane that never returns), its coordinates, and what is special about that point -- test in order: (a) S0-S1 bridge touch there (symmin gap ~0 at that spot, 222 method); (b) segmentation cluster boundary (segmentationStats.txt, 220/221 method); (c) boundary-bag hole (no input dots within r); (d) sharpness collapse (229 instrument at that dot). ONE named feature with a measurement, not a list.

## Boundary
Spartan read-only + compute on existing faces/clouds; may re-run edge ONLY on transplanted faces (223 pattern) if the walk must be re-observed -- no segmenter changes, no new thresholds. Do not touch: main worktree, cure branches, .scratch/pota228 renders (read them, don't overwrite), any ticket but this one.

## Constraints
Q1 before Q2 (if SPLIT-OFF, Q2's premise changes -- report that instead of forcing Q2). Slot-verify before grading (231 amendment: P25 gate-table misread). Numbers with coordinates, not adjectives.

## Acceptance criteria
- [ ] Q1 verdict SPLIT-OK / SPLIT-OFF with the sharpness triple + control
- [ ] Q2: divergence dot index + coordinates + the ONE special feature measured
- [ ] One picture with the turn marked (gold author, blue ours-on, black ours-off, red ring on the turn dot)
- [ ] Verdict line: TURN-AT-<feature> / SPLIT-OFF / NEED-<named thing>

## Required evidence to report
Sacct COMPLETED for any Slurm; face/cloud md5s or paths; the triple numbers; the turn coordinates + feature measurement; PNG path. Self-contained report in ticket Comments; leave Status for the lead.
