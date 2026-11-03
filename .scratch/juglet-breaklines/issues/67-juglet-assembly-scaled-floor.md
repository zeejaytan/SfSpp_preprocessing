# 67 — Juglet edgelines in the assembler: scaled floor, crash guard, and a real reassembly

**What to build:** the Juglet (9 pieces) assembled by SfS++ from our current edgelines, with
the assembler made safe for it: (1) an honest replacement for the 50-dot floor that admits
short Juglet breaks without admitting noise, (2) the empty-candidate SIGSEGV fixed so no arm
dies before scoring, (3) a measured attack on the wrong-attitude poses t58 exposed (I60:
pieces near-touching but 138-163 deg from the correct relative orientation), and (4) rendered
assemblies scored against the Juglet GT. Continues ticket 58 (resolved, cure undecided) under
the conservator's order of 2026-11-03: "we need juglet edgeline to work in assembler as other
pots, and get juglet reassembled".

**Why now (2026-11-03, conservator):** "it throw away the edgeline less than 50 points which
is most of juglet edgelines. this is continue the investigation for ticket 58".

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let
SfS find joins)

**Blocked by:** none (t66 merged d1d0123 supplies the lanes; t58's run of record is read-only)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-03)
**Branch:** 67-juglet-assembly-scaled-floor, in /c/PR/worktrees/sfs/67
**Worker:** (unset)

## Spec

### Given (measured facts this stands on)

- The gate: `structure-from-sherds-pp/main.cpp:86-90` and its batch twin
  `hpc/tools/main_pristine_batch.cpp:86` drop any piece whose Bl0 lane has < 50 dots.
  The paper states 50 only as a corpus-exclusion rule for pot-scale breaks
  (`papers/text/sfspp-2502.13986v1.md:329`); it removes 8 of 9 pieces of pot J, the same
  8 of 9 it removes from ours. The floor is length-bound: at the paper's d = 1.9 mm a
  43 mm break cannot hold 50 dots (t58 Table 3).
- Current lanes (t66 arm U, the merged recipe: worness 0.7 + radius 1.0 + admit-sign on):
  Bl0 dots J1..J9 = 59/32/44/31/43/45/54/40/22. Only J1 (59) and J7 (54) clear 50.
  Better preprocessing does NOT clear the floor -- loop length does (43-100 mm).
- t58 findings (run of record `runs/20261101-1913_d8f716f_t58-floor-density-panel`):
  - floor 10: all 9 active, 21 LCS candidates, one non-GT merge (2,4), 0 seated, exit 0.
  - floor 45/50: 1-3 active, 0 candidates, SIGSEGV 139 at
    `class/ranking_system.cpp:727` (`ext_state_[0]` on an empty vector; ext_state_ only
    appended at :720 when a non-empty graph exists).
  - I60 (old lanes resampled to 60 dots, floor 50): 63 candidates, 7 pieces saved, but
    0 seated -- chamfers 458-475 mm; three GT pairs physically near-touching (5.9-11.0 mm,
    14-21 contact points) while facing 138-163 deg away. A MATCHING/attitude failure,
    not a seating failure.
  - Pot A control at floor 10: 8/8 seated, 15/15 joins -- the floor edit alone is inert
    on a working corpus.
  - `MINIMUM_NUMBER 6` (LCS window) is NOT binding on these lanes (min 22 dots).
  - A second hidden floor: `reconstruction.cpp:72` `if (numberOfPoints < 10) return;` in
    AxisAlignment returns WITHOUT setting R_out/t_out -- not fired yet (min 22), but a
    short-lane arm must watch it.
  - LCS matcher needed ~45+ honest inliers on Pot A short lanes (ticket 45 lesson).
- Staging recipe that worked in t58 (reuse it): Breaklines/ = Bl0 lanes; Surfaces/ = S0/S1
  converted to bare 6-number .xyz (`class/data_structure.cpp:781-843` cannot parse PLY
  headers); Mesh/Axes/Ground Truth from `Dataset/{Mesh/Juglet, Axes/Juglet, Juglet_GT}`;
  Pot A bundle hardlinked. Seating bar: chamfer < 7.07% of the 65 mm reference = 4.596 mm;
  strict edge bar 5 deg / 10 mm.

### Task

1. **Crash guard (code, built in the run area, merge proposal at close).** In the batch
   shim (`hpc/tools/main_pristine_batch.cpp` path), guard the empty-candidate case at
   `ranking_system.cpp:727` (and any sibling `[0]` on `ext_state_`): when no candidate
   pairs exist, print a one-line "no candidates" result and exit 0 with empty outputs,
   instead of SIGSEGV. Record binary md5 + the diff. The canonical
   `structure-from-sherds-pp` sources stay untouched during the run; if the guard proves,
   the lead decides the merge as a separate commit.
2. **Scaled-floor experiment.** Arms (same binary family as t58, one sed-style literal
   change each, md5 + diff recorded): F20 (floor 20: all 9 t66 lanes active), F30, and
   SCL (a scale-aware floor = 50 x Juglet/PotA reference extent = 50 x 65/194 ~ 17, use 17).
   Lanes = the t66 arm-U Bl0 lanes (current merged recipe). Also rerun F50 (shipped) as the
   baseline-with-guard (expect "no candidates", exit 0 now).
3. **Attitude attack.** Whichever arm shows the most graph growth: instrument per GT-adjacent
   pair the LCS candidate list (pair, LCS length, inliers if extractable) and the relative
   pose the matcher proposes vs the GT relative pose (rotation error deg, translation mm).
   Name where the attitude error enters (candidate scoring? pruning? StateManager merge?
   axis alignment?). Do NOT tune by trial -- locate the stage, measure it, report.
4. **Control.** Pot A on the same guard binary at the shipped floor 50: must reproduce
   8/8 and 15/15.
5. **Write `## Results`**: arm x piece x seated/chamfer table, GT-edge pass table, attitude
   table, renders (workspace-relative under `SfSpp_preprocessing/artifacts/67/`), best-of-N
   stated (assembly path carries no RNG, so N=1 per arm -- say so), every sbatch polled and
   sacct recorded.

### Acceptance

- Every claim carries file:line or a measured number from a named run dir.
- Experimental binaries: md5 + diff recorded; canonical assembler untouched during the run.
- Renders for every seating claim; the Juglet assembly however it comes out -- a negative
  result with located cause is acceptable, a silent one is not.
- Budget: <= 5 Slurm jobs, <= 24 h wall.
- Worker measures; the lead verifies and merges; the conservator judges the assembly.

**Edges:** t58 run of record read-only; t66 run read-only; shares the Dataset/ trees
read-only.
