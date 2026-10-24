# 283 — Name the test that refuses Pot H 10's ribbon

Answers: E1
Status: ready-for-agent
Working in: C:/PR/worktrees/sfs/283 (one mesh run; no C++, no default changed)
Needs-eye: no

## What ticket 281 established

Pot H 10 Bl1 misses 20 of its 88 reference dots. Fifteen of them sit on **dropped cluster 5** —
629 points, a 21.66 x 3.20 x 1.76 mm ribbon meeting kept cluster 1 at 0.3191 mm — so the edge the
authors drew belongs to a facet we never kept. Step 1 of the Appendix A merge is satisfiable there
(35 c5 points within rho_d = 1.0 mm of c1, 37 the other way), so a pair could have formed and the
refusal came from a later test. Which one is not recoverable from a dump: it needs the merge trace.

## Task

One mesh run, frozen inputs, theta 3.4, with **SFS_MERGE_PAIRS=1** (the ticket 276 Phase 2
instrumentation already prints nrm / curv / inner / icurv and the verdict per candidate pair) and
**SFS_AXIS_FILE set** — confirm the log's classify line shows the axis was used, not "no
SFS_AXIS_FILE, keep size order" (ticket 277). Cluster ids must come out the same as in 281's
dump; if they do not, stop and report, because the run is not the same piece.

Find the c5-c1 pair in the PAIR-276 output and quote its line verbatim: the pair index, the
qualifying-pair count, dmin/dmed, nrm, curv, inner, icurv, and the accept/reject verdict.

## Pre-registered read

- Rejected on **rho_n (0.95)**: the refusal is PRINCIPLED — the ribbon sits ~28 deg from the kept
  face's normal and the paper requires agreement within ~18 deg, so merging it would be against
  the paper's own rule. H10 Bl1 then closes as class K with a paper-consistent reason, and no
  merge change is proposed.
- Rejected on **rho_in,n (0.75)** or rho_c: this is the same Step 3 / curvature defect seen on
  Pot C 03 and Pot C 01 in ticket 276 Phase 2, and it becomes a shared cause rather than a
  one-off.
- **No pair printed at all** (no qualifying pair): then 281's Step-1 numbers were measured on a
  different frame — report it and stop; do not retune rho_d.

## Constraints

- Do not change a default, do not edit C++, do not retune any threshold.
- Run directory under SfSpp/runs/ with run.json, one index.tsv row, tag p283-h10-merge-test.
- Report the pair census as well as the c5-c1 line, so the absence of other pairs is visible.

## Acceptance

- The c5-c1 pair line quoted verbatim, with the rejecting test named.
- The classify line proving the axis file was used, and the cluster census matching 281.
- One of the three pre-registered verdicts, and the follow-up it implies.
