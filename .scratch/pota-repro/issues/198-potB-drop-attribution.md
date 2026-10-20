# 198 - Which Pot B pieces did thinning drop (194 follow-up)

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Attribute 194's collapse (6/9+5/15 -> 2/9+1/15): GT-score the 194 T-files per piece, name exactly which 2 still seat and the dropping set vs 93's seated [1,3,4,6,7,9] (R2/R3), and test the worker's mechanism hypotheses from the 194 Comments against the per-piece pattern (e.g. does the drop concentrate on partial-arc B02 / low-coverage pieces / the flagged-marginal +0.457 loop?).

## Method (laptop-side analysis ONLY, no sbatch, no rebuilds; read 194 Comments for the tally table, hypotheses, and T-file paths)
1. Write the GT-scoring analysis (new code allowed -- script freeze applied to the walk, not to scoring), score per piece per run.
2. Report: seated set in 194 vs 93, dropping set, and for each dropped piece the most likely mechanism with numbers (coverage delta, rim-truth delta, gate numbers).
3. Own a falsifier: if the drop shows no per-piece pattern (uniform random across runs), say so -- mechanism UNATTRIBUTED.

## Constraints
No Slurm, no commits to tracked files beyond this ticket's Comments. Read-only on bundles. Finish via ticket Comments + final output -- never via send_message.

## Acceptance
Per-piece seated/dropped table x3 runs + mechanism verdict per dropped piece (or UNATTRIBUTED with the refusing numbers).
