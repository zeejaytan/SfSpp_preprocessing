# 288 — the shipped binary must be the committed source

Status: ready-for-agent
Answers: E1
Working in: C:/PR/worktrees/sfs/288

## Why

Ticket 287's seed change is now on `main` (commit 8e1e514, source
`edgeline_extraction_headless.cpp`), and the scores that justified it came from a binary built in a
worktree from the uncommitted patch. The two must be the same program. The last time a change was
landed in this file without a build from the commit, the compile failed on an orphaned static
(`gateDiag_turnSum`, 538357c -> 67ff3d7), and every later number would have been suspect.

## Goal

Build the edge binary from `main` at the seed commit, prove it is the same program that was scored,
and re-run the eight surviving 287 lanes as the gate. No code change of any kind.

## Phases

**Phase 1 — build.** Build `EdgeLineExtractionHeadless` from a clean `git archive` of the seed commit
in the same apptainer recipe ticket 287 used (record the exact command in `logs/`). Report:
commit sha, source md5 (LF), binary md5, and whether the binary is bit-identical to
`a28d10afab2b50bbe750d599ee2b7214` (the binary that produced the 287 `after` numbers).

**Phase 2 — gate.** Run the eight lanes whose frozen sheets still exist (Pot C 01, Pot J 01, Pot H 02,
Pot H 10, both lanes), defaults only, no `SFS_*` set except `POT_NAME`; score with the run's own
scorer against the authors' breaklines. Expected, from ticket 287's `after` column:

- C01 Bl0 207 / 0.682 / 98.55, C01 Bl1 226 / 0.572 / 100.00
- J01 Bl0 170 / 0.581 / 100.00, J01 Bl1 184 / 0.597 / 100.00
- H02 Bl0 152 / 0.582 / 100.00, H02 Bl1 138 / 0.867 / 73.19
- H10 Bl0 98 / 0.664 / 100.00, H10 Bl1 92 / 0.642 / 72.83

Tolerances: n exactly; median +-0.05 mm; coverage +-1.0; jumps equal. Every lane must print a
`[SEED-287]` line carrying `ncomp=`, `biggest=` and `size=<n>/<n>`.

**Phase 3 — one-line answer to the question that decides everything downstream.** Does the binary
built from the committed source reproduce the scored behaviour? Yes or no, with the row that would
have failed.

## Boundary

Edge stage only. Do not touch `mesh_processing_headless.cpp`, any default, any threshold, or the
`SFS_*` switches. Do not edit the source; if the build fails, paste the first compiler error and
stop. Do not re-mesh (the mesh RNG is unseeded, `mesh_processing_headless.cpp:1526-1527`); reuse the
frozen sheets from the 287 run directory. Never use `build.sh --target nurbs` (ticket 282: it builds
the pre-247 duplicate at `original_nurbs_preprocessing/`).

## Record

Run directory under `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with
`run.json`, `submit.sbatch`, `logs/`, `out/`, and one appended row in `runs/index.tsv` (verdict and
human_note left for the lead). Write the result into this ticket in the main clone, leave it
uncommitted; the lead commits. Confirm it with a Slurm poll on every `sbatch`.

## If it fails

Report the divergence per lane and stop: a committed source that does not reproduce its own scores is
a finding about the build, not a reason to retune anything.
