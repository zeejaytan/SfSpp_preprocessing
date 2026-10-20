# 198 - Which Pot B pieces did thinning drop (194 follow-up)

Status: landed (lead 2026-10-20: GLOBAL-collapse attribution verified -- untouched B01 drops 3/3, surviving edge = beam chance; no per-rim repairs)
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

## Comments (worker, 2026-10-20 -- ATTRIBUTED: global feature change, not per-rim damage; COMMIT NOTHING)

**Verdict: the collapse is GLOBAL and UNIFORM -- 14/15 edges wrong in every run, all 9 pieces placed-but-wrong (zero unplaced), and the single surviving edge varies by run. No per-piece pattern tracks rim damage: the untouched-Forest piece (P1, B01 byte-identical to 93 SXC) and the gate-green P9 drop in ALL 3 runs. Mechanism (a) from 194 SUPPORTED as the primary cause; (b) linchpin and (c) exclusion-driver REJECTED as pattern drivers. One correction to 194: runs are NOT solution-identical -- tallies match but T-files differ and the surviving edge changes (beam variance on top of collapse).**

**1. Per-piece GT scoring (p60 strict logic: D = GT_rel * T_rel^-1, angle < 0.35 rad and |t| < 50mm; piece seated iff >=1 correct edge; script artifacts/pota198/p198_identities.py; recompute matches the binary tallies 2/9+1/15 exactly all 3 runs). Sources: laptop artifacts/pota198/pota194_fetch_{33485122,33485129,33485130}.tgz (byte sizes match 194 Comments), extracted to fetch_*/pota194_fetch/{GT_B,T_B_194}.**

| run (job) | recomputed | seated (via) | missing |
|---|---|---|---|
| R1 (33485122) | 2/9 + 1/15 | [4,6] via (4,6) | [1,2,3,5,7,8,9] |
| R2 (33485129) | 2/9 + 1/15 | [4,6] via (4,6) | [1,2,3,5,7,8,9] |
| R3 (33485130) | 2/9 + 1/15 | [3,7] via (3,7) | [1,2,4,5,6,8,9] |

Wrong-edge magnitudes (ang rad / trans mm), all far past gate -- no near-miss a threshold tweak would rescue (closest: R3 (1,8) 0.208/86.0, R2 (1,3) 0.281/83.5 and (6,7) 0.274/93.1 -- angles pass, translations fail by 30-40mm+):
- R1: (1,2) 2.0/598, (1,3) 2.99/854, (1,4) 3.04/830, (1,5) 3.07/449, (1,8) 2.90/552, (1,9) 2.86/756, (2,4) 2.88/638, (2,8) 2.97/629, (3,5) 3.04/574, (3,7) 1.02/285, (5,8) 1.54/476, (6,7) 2.63/438, (6,9) 2.04/493, (7,9) 0.71/267.
- R2: (1,2) 3.07/471, (1,3) 0.28/84, (1,4) 0.91/335, (1,5) 1.96/701, (1,8) 1.84/630, (1,9) 1.16/486, (2,4) 3.13/696, (2,8) 3.11/663, (3,5) 1.93/436, (3,7) 0.75/197, (5,8) 2.50/619, (6,7) 0.27/93, (6,9) 2.04/490, (7,9) 1.83/427.
- R3: (1,2) 2.0/680, (1,3) 1.43/465, (1,4) 2.24/736, (1,5) 0.65/280, (1,8) 0.21/86, (1,9) 0.45/153, (2,4) 2.05/370, (2,8) 1.89/408, (3,5) 2.04/446, (4,6) 0.68/268, (5,8) 0.52/166, (6,7) 1.50/269, (6,9) 2.62/520, (7,9) 1.21/258.

**2. Dropping set vs 93's R2/R3 seated [1,3,4,6,7,9] (93 strict sets: R1 [1,4,7,9], R2/R3 [1,3,4,6,7,9]; P2/P5/P8 missed in 93 too -- pre-existing, not thinning-attributable).**
- Always-dropped (3/3 runs): P1, P9.
- Sometimes-dropped (survive once via a single edge): P3 (R3 only), P4/P6 (R1R2 only), P7 (R3 only).
- Still-seated: [4,6] (R1R2), [3,7] (R3) -- each pair hangs on ONE edge out of 15.

**3. Mechanism verdicts per dropped piece (rim numbers from 194 §2 table; falsifier deltas vs unthinned SXC).**
- P1 -- KNOCK-ON, not rim damage. B01 byte-identical to 93 SXC (194 §4), yet P1 (seated all 3x93 runs, incl. via (1,4) 0.048-0.093/17-41mm) drops 3/3; its edge (1,4) to thinned P4 blows out to 0.91-3.04 rad / 335-830mm. An untouched rim's piece fails because its neighbours' features moved -- the signature of a global matcher-level change.
- P9 -- GLOBAL, not rim damage. Rim gate-green (delta +0.168, cov 74/75, closure 1.79) yet drops 3/3; incident edges (1,9)/(6,9)/(7,9) all wrong every run.
- P3/P4/P6/P7 -- UNIFORM COLLAPSE + beam noise. Survival does not rank with rim quality: P4 has the BEST falsifier delta (-0.013, cov 132/136) yet drops R3; P3 (+0.224) survives once; P6 (+0.068) and P7 (+0.089) likewise. No rank correlation between per-loop delta/coverage and survival -- the falsifier's own numbers refuse a per-rim story.
- P2 (B02, flagged marginal +0.457, cov 83->72) -- NO NEW ATTRIBUTION POSSIBLE. P2 was flipped ~pi in all 3x93 SXC runs already; its incident edges (1,2)/(2,4)/(2,8) were wrong in 93 and are wrong in 194. Hypothesis (b) linchpin REJECTED as primary cause: one weak rim cannot explain 14/15 wrong edges, and P1/P9 drop with clean/untouched rims -- at most a minor contributor, unisolable from the pre-existing flip.
- Hypothesis (c) (on-arc exclusions B06 13/B02 9 bridged by smoothing) REJECTED as pattern driver: highest-exclusion B06 survives 2/3 runs; zero-exclusion B01 never survives; low-exclusion B09 (4) never survives.
- Hypothesis (a) (resample swaps measured dots for centreline interpolations: zero true edge info added, every matcher station moved) SUPPORTED: (i) 14/15 edges wrong every run, zero unplaced -- everything placed-but-wrong; (ii) untouched-P1 + green-P9 drop; (iii) no delta-vs-survival correlation; (iv) 464->554 hypothesis-space shift (194 §5); (v) sole surviving edge flips between runs ((4,6) vs (3,7)) -- collapse floor with beam noise on top.

**4. Correction to 194's determinism claim.** 194 Comments state "binary-identical all 3 runs (deterministic, not beam variance)". Tallies ARE identical (2/9+1/15, pruned 44/45/44), but the T-files are NOT: cmp-differs on 8-9/9 T-files R1vsR2 and R1vsR3 (only T_0to_0 R1=R3), and the recomputed seated set differs (R3 [3,7] vs [4,6]). So: the collapse depth is deterministic, which single edge survives is beam chance. Trivially reproducible from the laptop fetches above.

**5. Evidence.** Laptop artifacts/pota198/: pota194_fetch_{33485122,33485129,33485130}.tgz + fetch_*/ extracts + p198_identities.py (new scoring code -- allowed: freeze covered the walk, not scoring). Spartan untouched (read-only ssh downloads of the existing fetch tgzs; no sbatch, no builds). No commits; bundles read-only.

**6. Recommendation.** Do not chase per-rim repairs (B02 refit, exclusion tuning) for this collapse -- the numbers say the resample itself moved the whole feature space. Any thinning rollout must stay gated on a doubling diagnosis (179 census recipe) per 194's verdict; clean singles keep author dots.
