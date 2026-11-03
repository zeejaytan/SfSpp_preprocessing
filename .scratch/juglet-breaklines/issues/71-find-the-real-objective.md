# 71 — Find the objective the released axes are actually a minimum of

**What to build:** ticket 70 proved the shipped Cao cost does not have the pot axis at its
minimum (repairing the LM walks the released axis 40.9 deg away from GT, and 37 mm off the pot
on a synthetic shell). The next question is the one that decides what to ship: **is there an
objective whose minimum IS the released axis?** If yes, wire it in and the axis step starts
producing the sample's axes. If no, the released axes are unrefined candidates and the gap is
in candidate RANKING, not in a polisher — which is a different fix and must be stated as such.

**Answers:** U19, E1

**Blocked by:** none (t70 closed; branch 70-multi-axis-potsac holds the repair behind
`SFS_AXES_REFINE_NOOP=1`)

**Status:** ready-for-human — lead verified 2026-11-03; stage C correctly not run

**Worker:** cursor_code session `t71` (lead-verified; stages B4/B5 run by the lead)

**Budget:** 4

**Hand-over:** DeepSeek — code part; hidden check is stage B's synthetic exactness gate
(true axis must be the global minimum of the shipped-by-default cost).

## Spec

### The two hypotheses, and the test that separates them

- **H-obj:** the released axes are a minimum of some residual form R(vt, X). Then starting a
  minimiser of R from a perturbed released axis returns to it (drift ~0), and R ranks the
  released axis above a random candidate.
- **H-cand:** the released axes are raw candidates from the authors' own generator
  (Pottmann on 6 points), which is **never refined** in their MATLAB (t70 stage 1: the
  two-stage refinement is a silent no-op). Then no objective has them at its minimum, and they
  are only reproducible by reaching the same candidate.

Both can be true of different pieces; report per piece, never only in aggregate.

### Stage A — is the released axis reachable at all? (cheap, decisive)

Run the port's `run_potsac` on each of the 163 corpus pieces with **20 seeds** (0-19), step 10,
no truncation. For every piece record the best match of the released line 1 against all of that
seed's lines at the t70 gate (5 deg direction / 2 mm radial). Report:
- pieces where **any** seed produces a line within the gate;
- the distribution of the best angle over seeds (this is the search space's own noise floor);
- how many seeds are needed to cover the released axis on 50% / 90% of pieces.

Gate: if the released axis is reachable on the majority of pieces at some seed, H-cand is
supported and the ticket's remaining stages are still run but the conclusion is written as
"ranking/seed, not objective".

### Stage B — residual zoo, synthetic first, then corpus

Candidate residual forms, all on the same X (points + unit normals):

| name | R | note |
|---|---|---|
| `cao_shipped` | T2 - sqrt(sum T2^2 / sum T3^2) T3 | the shipped form, control |
| `cao_perpoint` | T2 - (\|T2\|/\|T3\|) T3 per point | t70 probe: still escapes |
| `proj_signed` | T2 - ((T2.T3)/\|T3\|^2) T3 | signed per-point least squares |
| `cross` | cross(T2, T3) | the form commented out at compute_cao_error.m:37 |
| `triple` | T1 . T3 (scalar per point) | classical surface-of-revolution condition |
| `sin_normal` | n . v | control, direction-only |

**B1, synthetic exactness (the hidden gate).** Exact two-wall cylinder and exact two-wall
cone, both normals, known true axis. For each cost, minimise from the true axis and from
true + 2 deg tilt, +1 mm, +20 mm. The true axis must be the global minimum and every start
must return to it (<=0.5 deg, <=0.5 mm). Lead has already run this locally
(`C:/PR/.scratch/diag70/objcheck7.py`): `cao_shipped` fails both geometries, `proj_signed`
and `cross`/ `triple` return 0.00 deg / 0.00 mm on both. Reproduce those numbers, do not
copy them.

**B2, corpus fixed point.** 163 released pieces (141 with GT). Perturb released line 1 by
2 deg + 1 mm, minimise each cost, record drift (deg, mm), final cost, and the angle of the
result to the GT axis. Also score the released axis and the GT axis under each cost and say
which cost prefers the released axis.

**B3, ranking.** For each cost, does the released axis outrank the port's own line 1 when both
are scored on the same cloud? t70 measured this for the shipped form only (released loses on
163/163).

### Stage C — only if B1 passes and B2 shows a cost with median drift <= 2 deg

Wire the winning form into `sfs_axes/cao.py` behind `SFS_AXES_COST=proj|shipped` (default
`shipped`, so nothing moves unless asked), rerun the t70 stage-2 match gate on all 163 pieces
(the gate is 5 deg / 2 mm; t70 recorded 0/163 for line 1 and 1/163 any-line), and report the
gate numbers side by side. Then the Juglet: nine pieces, the t69 JUG09F50 lane, the t68 axes
replaced by the new cost's output, and the t67 assembler reading.

## Constraints

- **Nothing changes by default.** Any new cost sits behind an env switch whose unset path is
  byte-identical to today.
- The corpus at `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` is read-only.
- Stage A and B are analysis; only stage C touches shipped code, and only behind a switch.
- Report per piece, not only medians: t70's whole lesson is that a median hid a 40 deg walk.

## Lead's starting evidence (measured 2026-11-03, reproduce it, do not cite it as proof)

`C:/PR/.scratch/diag70/objcheck7.py` on synthetic exact two-wall shells:

| cost | cylinder: min from true axis | cone: min from true axis |
|---|---|---|
| cao_shipped | 50.88 deg, 5.75e7 mm | 90.00 deg, 1.67e9 mm |
| proj_signed | 0.00 deg, 0.00 mm | 0.00 deg, 0.00 mm |
| cross / triple | 0.00 deg, 0.00 mm | 0.00 deg, 0.00 mm |
| sin_normal | direction-only, no position | — |

`C:/PR/.scratch/diag70/pottmann6.py`: Pottmann on 6 random points recovers the true axis to
0.0000 deg and 0.0000 mm over 300 draws on a synthetic exact cone — the authors' candidate
generator is exact on a true surface of revolution, so the released axes need no refinement to
be good.

Slurm run `/data/gpfs/projects/punim2657/SfSpp/probe/p71/` (job 34283802, lead, still
running) does the corpus fixed-point test for the six costs on 30 pieces (3 per pot). Read its
`p71_leadprobe.txt` when it finishes; early rows already show `cao` drifting 0.75-89.4 deg
while `proj_signed` drifts 0.55-7.65 deg and `cross`/`triple` 0.39-39.4 deg.


## Results (2026-11-03)

Four Slurm jobs, all COMPLETED 0:0. Nothing merged. Branch `71-find-the-real-objective`
carries the instrument only (`costs71.py`, `b1_synthetic.py`, `corpus71.py`, `b4_pottmann.py`,
`b5_rank.py`); no shipped code changed, no default moved.

### Stage A — our port cannot reach the released axis (job 34284310)

`runs/20261103-2243_647cc24_t71-objective`, 20 seeds x 163 pieces, refine no-op, step 10.

- **reachable at some seed: 1/163.** Cumulative coverage never exceeds 0.6%.
- Per-seed best angle median 41.8-53.1 deg, p10 10.9-18.0 deg, min 0.333-1.132 deg. The
  spread across seeds is the search's own noise floor and it does not close the gap.
- So H-cand is supported in its weak form: our generator, run 20 times, does not produce what
  the authors produced. That alone does not say whether the released axis is a minimum of
  anything.

### Stage B1 — synthetic exactness, independently reproduced (job 34284310)

`out/b1_synthetic.tsv`, `out/b1_landscape.tsv`. Exact two-wall cylinder (R=50, t=4, z -40..40)
and exact two-wall cone (r = 0.4z, z 40..120, t=4), 1152 points each, both walls, exact normals.
Gate = every start returns to the true axis within 0.5 deg and 0.5 mm.

| cost | cylinder | cone |
|---|---|---|
| cao_shipped | **FAIL** — 90.00 deg from both perturbed starts | pass (0.0005 deg) |
| cao_perpoint | **FAIL** — 89.68 deg | pass |
| proj_signed | pass (0.00 deg / 1e-11 mm) | pass |
| cross | pass | pass |
| triple | pass | pass |
| sin_normal | no position term; fails the mm test by construction | same |

The landscape table (cost at the true axis vs 90 deg vs 20 mm offset) shows why:
`cao_shipped` on the cylinder is **cheaper at 90 deg (3.876e6) than at the true axis (5.096e6)**,
and cheaper still at a 20 mm offset on the cone. `proj_signed`/`cross`/`triple` are cheapest at
the truth on both geometries by 5-12 orders of magnitude.

Note the difference from the lead's `objcheck7.py`: the worker's cone (r = 0.4z) lets
`cao_shipped` sit still, the lead's (R 40->55) does not. Both geometries are exact; the
disagreement is the geometry, and it does not change the verdict on `proj_signed`/`cross`.

**Gate B1: passed for proj_signed, cross, triple. Failed for both Cao forms and sin_normal.**

### Stage B2 — no cost is a fixed point on the real corpus (job 34284310)

`out/fixed71.tsv`, 163 pieces, perturb released line 1 by 2 deg + 1 mm, minimise:

| cost | drift med | drift p90 | <=2 deg | result vs GT med | released vs GT med | better than released |
|---|---|---|---|---|---|---|
| cao_shipped | 58.77 | 87.93 | 2/163 | 64.08 | 2.78 | 10/141 |
| cao_perpoint | 58.34 | 86.62 | 1/163 | 60.20 | 2.78 | 10/141 |
| proj_signed | **4.35** | 33.90 | 43/163 | 6.51 | 2.78 | 37/141 |
| cross | 24.89 | 72.41 | 20/163 | 23.57 | 2.78 | 24/141 |
| triple | 24.89 | 73.28 | 20/163 | 23.21 | 2.78 | 25/141 |
| sin_normal | 46.58 | 87.73 | 1/163 | 47.60 | 2.78 | 10/141 |

Two things at once: `proj_signed` is by far the closest thing to a fixed point (median 4.35 deg
against 24.9-58.8 for the rest), **and it still makes the axis worse than the released axis** —
6.51 deg from GT after minimisation against 2.78 deg for the released axis it started from.
It improves the axis on only 37 of 141 pieces.

**Gate B2: failed (median drift 4.35 > 2 deg). Stage C correctly not run.**

### Stage B3 — ranking (job 34284310)

Does the released axis score lower than our own seed-0 line 1? `out/rank71.tsv`:
cao_shipped 6/163, cao_perpoint 4/163, proj_signed 127/163, cross 119/163, triple 119/163,
sin_normal 92/163. Under `proj_signed` the released axis beats our own candidate on 127 of 163
pieces, which is the only arm where the objective agrees with the authors at all.

### Stage B4 (lead) — the answer is IN the candidate pool (job 34284870)

`runs/20261103-2254_647cc24_t71-pottmann`, `b4_pottmann.py`, 141 pieces with GT axes. Pottmann
on 6 random points straight from the released Surface files: no MLESAC, no scoring, no dedup,
no refine. 400 draws per piece.

| | median angle to GT | within 5 deg | within 10 deg |
|---|---|---|---|
| released axis (control) | 2.78 deg | 92/141 (65.2%) | 105/141 |
| best of 400 Pottmann draws, both walls | **0.95 deg** | 123/141 (87.2%) | 134/141 |
| best of 400, wall 0 alone | 0.89 deg | 129/141 (91.5%) | 136/141 |
| **median single draw** | 31.15 deg | 3/141 (2.1%) | 14/141 |

The released axes are beaten by a random search of their own generator on 2 of every 3 pieces.
A typical draw is 31 deg off, so the pool is mostly wrong and a small minority is essentially
exact. Also measured: mean |n.axis| median 0.393 (a genuine surface of revolution), and the
fraction of normals pointing inward is 0.494 — the surfaces are sane, both walls present.

### Stage B5 (lead) — but no residual can FIND it (job 34284924)

`runs/20261103-2300_647cc24_t71-rank`, `b5_rank.py`. Same 400-draw pool, then pick the argmin
under each cost — **GT is used only to score the pick, never to choose it**:

| cost (blind argmin) | median angle to GT | within 5 deg | within 10 deg |
|---|---|---|---|
| pool oracle (best available) | 1.18 deg | 128/141 | — |
| cao_shipped | 51.14 | **3/128** | 4 |
| cao_perpoint | 54.76 | 2/128 | 2 |
| proj_signed | 10.59 | 51/128 | 70 |
| cross / triple | 22.16 | 36/128 | 46 |
| sin_normal | 43.00 | 2/128 | 10 |

On the 128 pieces where the pool demonstrably contains an axis within 5 deg of GT, the shipped
Cao cost finds it 3 times. `proj_signed` finds it 51 times.

## Conclusion

**H-cand holds, and the gap is in RANKING, not in refinement.**

1. There is no residual in this family that the released axes minimise (B2: the best of six
   still drifts 4.35 deg median and lands further from GT than it started).
2. The candidate generator and the input surfaces are fine (B4: 0.95 deg median at best-of-400,
   beating the released axes; normals sane).
3. Every scoring rule available picks badly out of a pool that contains the right answer
   (B5: 3/128 for the shipped cost).

That is consistent with a specific defect already visible in the port:
`sfs_axes/potsac.py` docstring records that `compute_biaxial_cao_error` returns a **whole-cloud
scalar**, so `inliers = int(abs(err) < 1.0)` is a degenerate 0/1 count and MLESAC's consensus
ranking has nothing to rank on. The authors' MLESAC scores by inlier COUNT per hypothesis; this
port cannot.

**Recommended next step (not this ticket):** build consensus-style rankers on the pool —
(a) inlier count at a fixed absolute tolerance on the `proj_signed` residual, (b) the same on
|cross(T2,T3)|, (c) a normal-ray/axis Hough accumulator — and score them with the B5 harness,
which is already the right instrument (pool in, blind pick out, GT only for scoring). B4/B5
together give a clean ceiling: 1.18 deg is reachable blind-oracle, 0.95 deg at best-of-400.

## Verification the lead performed

- `runs/20261103-2243_647cc24_t71-objective`: job 34284310 COMPLETED 0:0 5m50s; tables read
  back from `out/` and re-summarised locally with an independent script
  (`artifacts/71/` holds `fixed71.tsv`, `rank71.tsv`, `piece71.tsv`, `reach71.tsv`,
  `b1_synthetic.tsv`, `b1_landscape.tsv`).
- `runs/20261103-2254_647cc24_t71-pottmann`: jobs 34284804 (NotADirectory, flat Surfaces dir),
  34284836/34284837 (indentation, then a 6-vector passed where a 3-vector was expected),
  34284870 COMPLETED 0:0 21s. The first two runs also read the axis files with the WRONG column
  order (position-first files read as direction-first), which is why an early run reported the
  released axis 65.9 deg from GT; fixed to columns 3:6 and re-run.
- `runs/20261103-2300_647cc24_t71-rank`: job 34284924 COMPLETED 0:0 17m56s.
- Lead's own earlier probe `probe/p71/leadprobe.py` (job 34283802, 30 pieces) agrees on the
  direction of travel: proj_signed tightest at 2.47 deg median drift, cao 59.45 deg.

## Acceptance

- [ ] Stage A: 20-seed reachability table for 163 pieces, with the per-seed best-angle spread.
- [ ] Stage B1: synthetic table reproduced independently (not copied), true axis is the
      global minimum for the winning cost on both geometries.
- [ ] Stage B2: per-piece drift table for all six costs, plus which cost prefers the released
      axis, plus the GT angle after minimisation.
- [ ] Stage B3: ranking table.
- [ ] Stage C only if the B1/B2 gates pass; otherwise state the conclusion as H-cand and stop.
- [ ] Every claim cites a run id or a file:line; nothing is asserted from a median alone.
- [ ] Code tickets: branch merged into main and pushed, no job still running from it,
      worktree removed, branch deleted locally and on GitHub.

## Operational note for the worker (2026-11-03)

**Laptop ssh to Spartan is currently broken** — the Windows ssh-agent holds no identities and
the private key at `~/.ssh/id_ed25519` is passphrase-protected, so `ssh spartan` returns
"Permission denied (publickey)" from every shell, including `C:/Windows/System32/OpenSSH/ssh.exe`
(which additionally emits nothing at all, not even `-V`). **Do not spend budget on ssh.** Write
the scripts and the submit files; the lead runs them through the DSH ssh tool, which holds its
own live connection (`ssh_list` -> `spartan-e0a8d1bc`).
