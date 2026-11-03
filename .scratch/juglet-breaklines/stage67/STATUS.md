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
- [x] guard dry-run on login node (text only): both anchors found once; inserts after shipped :216 and :222;
      G.cpp md5 `056dfb914d7f067244a87d200ecb9863` (shipped shim `fb26e8ab49e9c00f7e8d02de44f6eea5`)
- [x] run dir created + job submitted (setup67.sh); index.tsv row appended, verdict/human_note empty
- [x] job polled to end, sacct recorded. Laptop poller (Git Bash, `SPARTAN_SSH=/c/Windows/System32/OpenSSH/ssh.exe
      /c/PR/scripts/slurm_poll.sh 34264796 60`) printed RUNNING at 14:30/14:31 then hung (no output for 7+ min,
      a stuck ssh); final state read directly with `sacct -j 34264796 -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS`.
      NOTE: the `bash` on PATH is WSL's -- run local .sh with `C:\Program Files\Git\bin\bash.exe`.
- [ ] Results: arm x piece table, GT-edge table, renders (artifacts/67/), attitude attack (task 3)

## Run
- Run dir: `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1429_3b3efbc_t67-juglet-assembly`
- Commit: `3b3efbc9f6caf3eacd8fa30c0838024b6a177d57`
- Job 1: **34264796** (sapphire, 8 cpu, 64G, 2h) -- sacct `COMPLETED 0:0`, elapsed 00:03:50, MaxRSS 6873484K,
  node spartan-bm148. Budget used 1 of 5 jobs.

### Binaries (logs/md5_binaries.txt; source diff vs guarded base = floor literal only, `logs/diff_<ARM>.txt`)
Guard diff vs shipped shim: `logs/diff_guard.txt` (two 4-line inserts after shipped :216 and :222).

| arm | floor | source md5 | binary md5 | exit | wall s | LCS cand / pruned-left | Acc.txt sherd / edge | T files |
|---|---|---|---|---|---|---|---|---|
| F50G | 50 | `056dfb914d7f067244a87d200ecb9863` (= G.cpp) | `5a5d83b325c41ab6131af3fa3483ce6f` | 0 | 45 (0 binary) | 1 / 0 -> `T67-NO-CANDIDATES` | none (early exit) | none |
| F30 | 30 | `cd650478935cc1d1f2845c03d453a5f1` | `dccb00289b979a5a5615e277b6e1d9da` | 0 | 13 | 23 / 1 | 0/8, 0/13 | T_1to_1, T_5to_5 (pieces 2, 6) |
| F20 | 20 | `90b5091bd4e191e411c618e50b10de14` | `320aa5a073cbe2c05c93ea426a78b90e` | 0 | 13 | 23 / 1 | 0/9, 0/18 | pieces 2, 6 |
| SCL17 | 17 | `a48ab78fe270b8f225ff039833ee504a` | `7eb92f2406d0c9abf0c46e00a832ba2f` | 0 | 13 | 23 / 1 | 0/9, 0/18 | pieces 2, 6 |
| PACTL | 50 (Pot A, inc2) | `056dfb914d7f067244a87d200ecb9863` (= G.cpp) | `d4323adc90a9a181eaf2cb54620822dc` | 0 | 134 | 124 / 70 | **8/8, 15/15** | 8 |

Pristine `Hierarchy-Clear` built in work/build: `de720ccf1cc9e1c15763bb59c0f10e10`. PACTL and F50G share source
but differ as binaries (different include root inc2 vs inc1 + `-DJUGLET_ORIG`), same as t58's F50/PA10 pairing.
score58.py: seated 0 in every Juglet arm; F30/F20/SCL17 one saved piece at chamfer 21.52 mm (bar 4.596 mm).
Pot A trees are hardlinks (link count 3 on Pot_A_Piece_01_Breakline_0.pcd).

Reading (worker, unverified): the guard turns the t58 SIGSEGV 139 into a clean exit 0; Pot A at the shipped
floor reproduces 8/8 and 15/15 on the guarded binary. F20 and SCL17 are the same run in effect (all 9 active,
min lane 22). F30 drops J9 (22). All three make one merge (2,6) and seat nothing.

## Next (resume here)
1. Check whether (2,6) is a GT edge: `Dataset/Juglet_GT/Juglet_simple_graph.txt` row 2 col 6 (1-based).
   Confirm F20 == SCL17 byte-for-byte (md5 out/*/T_*.txt, Edgeline_*), and F30 vs F20.
2. Fix the scorer's denominators for F30 (8 active) / F50G (2 active) as t58 flagged; per-piece table from
   `score/<ARM>.json` (F20 is the arm of record for all-9).
3. Renders: t58 `render58.py` (look in the t58 run dir `instruments/`/harvest; not in instruments/ listing --
   locate first) -> `SfSpp_preprocessing/artifacts/67/` for F20 and PACTL.
4. Attitude attack (task 3) on F20: instrumented shim copy (dump every LCS candidate pair, LCS length, and the
   relative pose proposed, vs GT relative pose from Juglet_GT/*_T.txt). Job 2 of 5.
