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

**Status:** ready-for-agent

**Worker:** unassigned

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
