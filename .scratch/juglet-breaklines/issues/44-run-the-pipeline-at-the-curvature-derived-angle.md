# 44 — run the pipeline at the curvature-derived angle

**What to build:** the one untested step of ticket 43. A full grid over the 17 pieces
(Juglet 1-9, Pot A 01-08) with two arms each — A today (no env overrides) and
B `SFS_PAPER_THETA` set per piece to ticket 43's curvature formula
`theta = k x S / R_fold` (k = 3.3573) — through the existing env switch, **no source
change**. Plus the no-env proof arm (N) on the four proof pieces. This is the run that
decides whether the formula *is* the method: if the formula's theta reproduces what the
outcome search found by hand, the growth-angle gate stops being a tuned constant and
becomes geometry in, angle out.

**Answers:** U19, E1

**Blocked by:** none (ticket 43 merged, f38ed3b..2e7082a; its committed prediction table
is the input)

**Status:** results-in
**Working in:** run 20261030-1511_fa92002_t44-formula, job 34028966, COMPLETED 0:0 at
2026-10-30T15:29:01+11:00 (lead chat, 2026-10-30)
**Branch:** 44-run-the-pipeline-at-the-curvature-derived-angle, in /c/PR/worktrees/sfs/44

- [x] `stage44/instruments/thetas44.tsv` committed, values **verbatim** from ticket 43's
      k-rule table: Pot A PA01 4.36, PA02 3.30, PA03 3.76, PA04 2.92, PA05 3.50,
      PA06 3.17, PA07 2.66, PA08 3.61; Juglet J1 10.29, J2 12.40, J3 9.35, J4 10.25,
      J5 8.74, J6 8.16, J7 8.65, J8 10.05, J9 12.68 — verified: job carried the file as
      `out/thetas_committed.tsv` (484 B, 17 rows); every arm-B cell's requested theta
      equals it to 3 dp (`theta_proof.tsv`)
- [x] one Spartan job, run dir `runs/20261030-1511_fa92002_t44-formula`, 34 cells (17
      pieces x arms A/B) + 4 arm-N proofs (Juglet_Piece_2, Pot_A_Piece_01,
      Juglet_Piece_5, Pot_A_Piece_07), staged per cell and deleted after the counted
      record — `pipeline_cells.tsv` holds 38 rows = 34 + 4 N; poll
      `scripts/slurm_poll.sh` (SPARTAN_SSH=Windows OpenSSH) final line
      `COMPLETED|0:0|2026-10-30T15:29:01`
- [x] `theta_proof` match=yes on every arm-B cell (the env reached the gate the binary
      actually used) and defaults proof armN sampled md5 == armA on all 4 proof pieces —
      17/17 arm-B match=yes, requested==committed; defaults 4/4 `same` (J2, PA01, J5,
      PA07); arm-A rows of this run replicate ticket 43's arm A to the second decimal
      (J1 1.82/0.53 @7 deg), so the grid is the same machine
- [x] Pot A arm B keeps two clean surfaces 8/8 (positive control; a collapsed pot voids
      the run, ticket 43's arm C precedent) — 8/8 `status_outcome=two` at formula thetas
      2.66-4.36, surface point counts within ~1-2% of arm A (e.g. PA01 B 66917/57872 vs
      A 66758/57292). The control holds: the formula does not disturb the pot it was
      calibrated on
- [x] Juglet arm B outcomes recorded per piece against the ticket-42 ladder reference
      — reproduced, better, or worse, named per piece: see Results below.
      **6 of 8 reproduced or better; J2 lost at its own 12.40; J1/J9 unchanged (no clean
      pair either way)**
- [x] corpus integrity: corpus md5 before == after, surfaces kept for the lead, geometry
      otherwise deleted with counted record, index row appended with empty verdict —
      `corpus.diff` and `inputs.diff` both 0 bytes; `GEOMETRY_DELETED.txt` written;
      index row `20261030-1511_fa92002_t44-formula  34028966  fa92002...` appended by the
      job with empty verdict
- [x] lead verdict written back, ticket closed, board rebuilt — verdict: **pass**
      (formula carries the ladder's wall pairs per piece with no per-vessel tuning;
      one named exception, J2). Written to index.tsv 2026-10-30 by the coordinating
      session

## Results (run 20261030-1511_fa92002_t44-formula, job 34028966)

Juglet arm B, each piece at **its own** formula theta (med_along/med_across mm, angle,
vs ticket 42's ladder 10.2 reference):

| piece | formula theta | arm B pair | t42 @10.2 | verdict |
|---|---|---|---|---|
| J1 | 10.29 | 8.36/19.40 @62 deg | none (pair only at 3.4: 1.82/0.53) | unchanged — no clean pair either way |
| J2 | 12.40 | 3.78/10.02 @49 deg, s0=172 pts (fragment) | 1.88/0.67 genuine | **worse — lost**: 12.40 overshoots; the wall survives only near 10.2 |
| J3 | 9.35 | 1.88/0.63 @18 deg | 1.77/0.51 | reproduced |
| J4 | 10.25 | 2.14/0.45 @19 deg | 2.14/0.45 | reproduced exactly |
| J5 | 8.74 | 2.47/0.41 @13 deg | 2.46/0.42 | reproduced |
| J6 | 8.16 | 2.33/0.48 @14 deg | 2.28/0.48 | reproduced |
| J7 | 8.65 | 2.81/0.43 @13 deg | 2.52/0.52 | reproduced (along 0.3 mm wider) |
| J8 | 10.05 | 1.86/0.38 @16 deg | 1.86/0.38 | reproduced exactly |
| J9 | 12.68 | 1.38/0.72 @50 deg, s0=392 pts (fragment), coin 2% | 0.79/2.42 borderline-reversed | unchanged — neither is a wall pair |

Genuine-pair signature (from the six reproduced): across 0.38-0.63 mm, angle 13-19 deg,
coin 0 — the same signature the ladder found, now reached per piece from S and R alone.

**What this settles:** the growth angle stops being a tuned constant. One rule fitted
only on Pot A (k=3.3573 over S/R_fold) carries the Juglet wall pairs at each piece's own
angle — 6 of 8 the ladder found, through the shipped env switch, with the pot it was
calibrated on intact (8/8). The exception is J2, whose fold radius (3.24 mm, the
tightest) sends its formula theta to 12.40, past where that piece's wall pair survives;
its pair lives near 10.2, so for J2 the rule is directionally right but ~2 deg wide.
Ticket 42's ladder search is superseded **except as the J2 fallback**: the formula is
the default, the ladder is the audit.

**What it does not settle:** seating. This is the preprocessing gate only; whether the
six wall pairs (plus J2 at 10.2) seat the Juglet end to end is U19's remaining question,
via ticket 07 with these thetas.

Verified: verify44.py against the run's own `out/cells-pipeline/*.tsv` (report in
`stage44/results/`); corpus and inputs diffs read back as 0 bytes; theta_proof and
defaults_proof read directly, not from the job's log.
