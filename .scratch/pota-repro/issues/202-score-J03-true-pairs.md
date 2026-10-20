# 202 - Score J03\u2019s true pairs: thin vs ORIG duet (laptop leg)

Status: open
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User decision (m04694, option 1). 201 exonerated J03\u2019s loop solo (words 0.556 = C01 level) yet J03 stays unseated (193). A join is a duet: the true edges (1,3),(3,6),(3,7) (92 \u00a74) need the mating rims (J01/J06/J07) to agree. Score, LAPTOP-SIDE, the true pairs with J03-thin vs J03-ORIG against the SAME neighbour loops. No E2E, assembler untouched (user freeze ruling stands).

## Legs (all laptop-side, numpy, read-only inputs; reuse .scratch/pota201_repro/ replication, cited source lines only)
1. Pair scores: replicate the assembler\u2019s pairwise match score (LCS + Cond1-4 incl. thickness, same cited lines as 201) for pairs (1,3),(3,6),(3,7) in two versions: neighbour-vs-J03-thin and neighbour-vs-J03-ORIG. Neighbour loops = the exact SXC bundle loops from 193 (J01/J06/J07 as seated in J_THIN). Report per-pair: score_thin, score_ORIG, delta, and rank of the true hypothesis among sampled wrong partners (same J03 vs 3+ wrong neighbours) in both versions.
2. Verdict per pair: SAME (thin duet scores like ORIG duet -- input fully exonerated, J03 is assembly-search) vs WORSE (thin duet scores worse despite matching solo words -- second input mechanism at pair level; name which gate kills it: LCS run, Cond4/thickness, veto).
3. Cross verdict: does pair scoring explain unseated-while-words-match? If all three pairs score SAME yet J03 unseats, the death is generation/pruning (beam never proposes or kills early) -- state this explicitly as the handoff to an assembly-search ticket.

## Boundary
Laptop only. Inputs read-only: 193 bundle loops (SXC + thin J03), ORIG loops, J meshes, pinned SFS++ source. Scripts + numbers under .scratch/pota202_repro/ + artifacts/pota202/ (untracked). Do NOT touch tracked files except this ticket. COMMIT NOTHING.

## Constraints
Same neighbour loops both versions -- the ONLY change is J03\u2019s loop (thin vs ORIG). Cite the matcher score source lines; no reimplementation from memory. No sbatch, no bundles, no E2E.

## Acceptance
Per-pair table (score_thin, score_ORIG, delta, true-vs-wrong rank both versions) + per-pair SAME/WORSE verdict with killing gate named + cross verdict (input-exonerated-to-search vs pair-level mechanism found).

## Required evidence
Comments: script paths, cited source lines, per-pair table, verdicts. Final output: same, self-contained.
