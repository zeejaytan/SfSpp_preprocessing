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

**Status:** in-progress
**Working in:** run 20261030-1511_fa92002_t44-formula, job 34028966 (lead chat, 2026-10-30)
**Branch:** 44-run-the-pipeline-at-the-curvature-derived-angle, in /c/PR/worktrees/sfs/44

- [ ] `stage44/instruments/thetas44.tsv` committed, values **verbatim** from ticket 43's
      k-rule table: Pot A PA01 4.36, PA02 3.30, PA03 3.76, PA04 2.92, PA05 3.50,
      PA06 3.17, PA07 2.66, PA08 3.61; Juglet J1 10.29, J2 12.40, J3 9.35, J4 10.25,
      J5 8.74, J6 8.16, J7 8.65, J8 10.05, J9 12.68
- [ ] one Spartan job, run dir `runs/<ts>_<git7>_t44-formula`, 34 cells (17 pieces x
      arms A/B) + 4 arm-N proofs (Juglet_Piece_2, Pot_A_Piece_01, Juglet_Piece_5,
      Pot_A_Piece_07), staged per cell and deleted after the counted record
- [ ] `theta_proof` match=yes on every arm-B cell (the env reached the gate the binary
      actually used) and defaults proof armN sampled md5 == armA on all 4 proof pieces
- [ ] Pot A arm B keeps two clean surfaces 8/8 (positive control; a collapsed pot voids
      the run, ticket 43's arm C precedent)
- [ ] Juglet arm B outcomes recorded per piece against the ticket-42 ladder reference
      (J2 1.88/0.67, J3 1.77/0.51, J4 2.14/0.45, J5 2.46/0.42, J6 2.28/0.48, J7 2.52/0.52,
      J8 1.86/0.38 along/across mm) — reproduced, better, or worse, named per piece
- [ ] corpus integrity: corpus md5 before == after, surfaces kept for the lead, geometry
      otherwise deleted with counted record, index row appended with empty verdict
- [ ] lead verdict written back, ticket closed, board rebuilt
