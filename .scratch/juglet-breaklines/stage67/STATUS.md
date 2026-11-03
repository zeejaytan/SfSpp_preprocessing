# Ticket 67 worker status (resume-cold file)

Updated 2026-11-03 (UTC+11). Branch `67-juglet-assembly-scaled-floor`, worktree `C:/PR/worktrees/sfs/67`.

## Files in this folder (all LF; `.gitattributes` = `* -text`)
- `rsh.ps1` -- laptop helper: LF-normalise a script, run it on Spartan via OpenSSH `bash -s` (PowerShell has no `<`).
- `patch_guard67.py` -- writes the guarded COPY `work/shim/G.cpp` of the shipped batch shim. Two guards,
  each anchored on a line that must occur exactly once (else exit 2):
  1. after `cout << "Total number pruned : "...` : `if (LCS_out.empty())` -> print `T67-NO-CANDIDATES`, `return 0`.
     This precedes `StateManager manager(...)`, whose constructor (`Initialize`, ranking_system.cpp:665-728)
     dereferences `ext_state_[0]` at :727 with an empty vector. Guard is in the shim; class/ untouched.
  2. after `manager.BuildStep();` : `if (manager.out_state_.empty())` -> print `T67-NO-STATES`, `return 0`
     (the fine-registration block reads `out_state_[0]`).
  Limit (recorded, not covered): a NON-empty pruned list whose root graph is still empty would also reach
  :727 inside the constructor; the shim cannot see that before construction. Watch for 139 in any arm.
- `stage67_inputs.py` -- t58 `stage_inputs.py` minus the 60-dot tree; lanes = t66 arm-U
  `outU_jug/geom/Juglet_Piece_N.{Bl0,S0,S1}`; S0/S1 PLY -> bare 6-number .xyz; Mesh/Axes/GT from
  `Dataset/{Mesh/Juglet,Axes/Juglet,Juglet_GT}`; Pot A hardlinked from `sfs_main/original_samples/SfS_pp`.
- `arm67.sh` -- t58 `work/arm.sh`, but every variant is sed-ed from `G.cpp` (floor literal only);
  logs diff vs G.cpp and vs shipped shim, and the BINARY md5.
- `submit67.sbatch` -- one job: guard, include roots (t58 recipe; JUGLET_ORIG block copied from t58 work/),
  stage, arms F50G(50) F30 F20 SCL17(17) on Juglet + PACTL(50, Pot A, inc2), then score58.py on Juglet arms.
  RUN = `$SLURM_SUBMIT_DIR`.
- `setup67.sh` -- Spartan side: fetch the branch into the canonical checkout (fetch only), create the run dir,
  `git show` the instruments at the commit, write run.json, sbatch from the run dir.

## State
- [x] scripts written, committed (see git log)
- [ ] run dir created + job submitted -> fill in below
- [ ] job polled to end, sacct recorded
- [ ] Results: arm x piece table, GT-edge table, renders (artifacts/67/), attitude attack (task 3), Pot A control

## Run
(filled after submission)

## Next (resume here)
1. Poll the job; record sacct State/ExitCode here and in the ticket.
2. Read `logs/panel.tsv` (exits), `logs/guard.log`, `logs/diff_guard.txt`, `logs/md5_binaries.txt`,
   `logs/binary_<ARM>.log` (T67- lines, candidate totals), `out/<ARM>/1. Acc.txt`, `score/<ARM>.json`.
3. Expect F50G: 2 active (J1 59, J7 54) -> T67-NO-CANDIDATES or a real pair, exit 0 either way.
   PACTL must read 8/8 and 15/15.
4. Pick the arm with most graph growth for the attitude attack (task 3) -- needs an instrumented shim
   that dumps per-pair LCS candidates + proposed relative pose; that is the 2nd job (budget: <= 5).
5. Renders: t58 `render58.py` (harvested copy under `SfSpp_preprocessing/artifacts/t58/`?) -- locate first.
