# 184 - Heading rule in greedy walker (arm 2 of 3-way shootout)

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Copy walk_m144 to scratch (never touch the repo file) and add direction preference: prefer the candidate most ahead of current travel, penalise sideways steps (worker's parameters, documented). The rule must hold a single file by itself.

## Common bar (all three arms): C01 new-edgeline TRUE-strip bag (paths in tickets 179 + 182; 182: .scratch/pota176_repro/p176_stepB2.txt, p176_lib.py walk_m144). Reference to match: p180 hand single loop, 220 dots / 383.5mm / closure 1.48 (.scratch/pota180_repro/p180_C01_single_walk.npy). Author key CHECK-ONLY never build: ORIG ring 211 / 380.0. Report: dots, arc, closure, med/max step, gaps over 5mm, D-tokens, order-coloured trace render (eye-checked), rim-truth med vs author, explicit key-free declaration (every input the rule used). Constraints: laptop-side read-only, COMMIT NOTHING, no Spartan. Honest negative with numbers is a result, not a failure. Acceptance: 240 dots or fewer, closure 2.0 or less, single station-wrap, render + numbers + key-free declaration. Rule + parameters documented; or honest negative with the refusing numbers.
