# 288 — the shipped binary must be the committed source

Status: results-in
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

## Results

**Phase 3 answer, first: YES — the binary built from the committed source reproduces the scored
behaviour, lane for lane, and the file it produces is byte-for-byte the one ticket 287 scored.**
No row would have failed; the eight rows are re-derived below, not restated.

### Phase 1 — build from the commit

Built from a clean `git archive 8e1e514` with nothing overlaid: the archive's blob md5 for
`edgeline_extraction_headless.cpp` equals the extracted file's md5, and no `*.cpp` in the tree is newer
than its `CMakeLists.txt`, so no local edit could have leaked in.

| item | value |
|---|---|
| commit | `8e1e5147da4f8ad065704462e2a464eb2953f466` ("Ship the largest-lump walk seed…") |
| source md5 (LF) | `f0dbfe7032d90a04412d15bd1699a703` (3739 lines, one `SEED-287` string) |
| binary md5 | `a28d10afab2b50bbe750d599ee2b7214` |
| expected (the 287 `after` binary) | `a28d10afab2b50bbe750d599ee2b7214` |
| bit-identical to the scored binary | **yes — IDENTICAL** |

Same recipe as ticket 287: `cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`
then `make -j8 EdgeLineExtractionHeadless` inside `pcl_191_nurbs.sif` (312,520,704 bytes, apptainer
1.3.3), compiler `/usr/bin/c++`, `CMAKE_CXX_FLAGS` empty. The exact compile command (511 chars) is in
`logs/compile_cmd.txt`, the build log in `logs/build_commit.log`, `BUILD_EXIT=0`. Strings in the
binary: STOP-267 ×4, FULL-263 ×3, VOTE-247 ×6, SEED-287 ×1.

### Phase 2 — the eight lanes at defaults

Defaults only, `POT_NAME` the single variable set; frozen theta-3.4 sheets copied verbatim; no mesh.
Columns are `n` / median (mm) / coverage ours→author / coverage author→ours / jumps / max step (mm).
The "287 after" column is read out of that run's own `out/score287.txt`, not retyped.

| lane | n | median | cov ours→author | cov author→ours | jumps | max step | 287 after | verdict |
|---|---|---|---|---|---|---|---|---|
| H02 Bl0 | 152 | 0.582 | 100.00 | 100.00 | 0 | 3.569 | 152 / 0.582 / 100.00 | REPRODUCES |
| H02 Bl1 | 138 | 0.867 | 73.19 | 74.45 | 0 | 3.736 | 138 / 0.867 / 73.19 | REPRODUCES (below bar, as before) |
| H10 Bl0 | 98 | 0.664 | 100.00 | 100.00 | 0 | 3.633 | 98 / 0.664 / 100.00 | REPRODUCES |
| H10 Bl1 | 92 | 0.642 | 72.83 | 77.27 | 0 | 4.571 | 92 / 0.642 / 72.83 | REPRODUCES (below bar, as before) |
| C01 Bl0 | 207 | 0.682 | 98.55 | 98.58 | 0 | 4.460 | 207 / 0.682 / 98.55 | REPRODUCES |
| C01 Bl1 | 226 | 0.575 | 100.00 | 99.57 | 0 | 5.028 | 226 / 0.575 / 100.00 | REPRODUCES |
| J01 Bl0 | 170 | 0.582 | 100.00 | 100.00 | 0 | 4.224 | 170 / 0.582 / 100.00 | REPRODUCES |
| J01 Bl1 | 184 | 0.601 | 100.00 | 99.47 | 0 | 4.031 | 184 / 0.601 / 100.00 | REPRODUCES |

Tolerances (n exact, median ±0.05 mm, coverage ±1.0, jumps equal): **8 of 8 pass with zero difference
on every column** — not merely inside the window.

**Pointwise against the 287 `after` exports** — the check a tolerance cannot fake:

```
H02 Bl0 n_new=152 n_287after=152 max_dxyz=0.000000 identical
H02 Bl1 n_new=138 n_287after=138 max_dxyz=0.000000 identical
H10 Bl0 n_new= 98 n_287after= 98 max_dxyz=0.000000 identical
H10 Bl1 n_new= 92 n_287after= 92 max_dxyz=0.000000 identical
C01 Bl0 n_new=207 n_287after=207 max_dxyz=0.000000 identical
C01 Bl1 n_new=226 n_287after=226 max_dxyz=0.000000 identical
J01 Bl0 n_new=170 n_287after=170 max_dxyz=0.000000 identical
J01 Bl1 n_new=184 n_287after=184 max_dxyz=0.000000 identical
```

**The seed line, every lane** (`[SEED-287]` carries `ncomp=`, `biggest=`, `size=<kept>/<bag>`):

```
[SEED-287] ncomp=4 biggest=0 size=716/986 seed=-5.85638 -27.3575 403.765   (C01 Bl0)
[SEED-287] ncomp=2 biggest=0 size=825/1090 seed=-12.6057 -29.6216 404.988  (C01 Bl1)
[SEED-287] ncomp=1 biggest=0 size=462/462 seed=35.7955 4.1832 509.674      (H02 Bl0)
[SEED-287] ncomp=1 biggest=0 size=484/484 seed=7.0776 13.7992 529.179      (H02 Bl1)
[SEED-287] ncomp=1 biggest=0 size=374/374 seed=-7.83697 9.45079 482.739    (H10 Bl0)
[SEED-287] ncomp=1 biggest=0 size=298/298 seed=-7.07469 15.1813 479.289    (H10 Bl1)
[SEED-287] ncomp=4 biggest=0 size=580/832 seed=55.1673 10.7026 472.957      (J01 Bl0)
[SEED-287] ncomp=2 biggest=0 size=600/883 seed=57.7673 17.4733 474.449      (J01 Bl1)
```

**Sheets:** `EDGE_EXIT=0` on all four pieces (H02, H10, C01, J01), and every sheet's md5 is identical
before and after its run — "sheets unchanged" on all four. No mesh stage ran.

### Record

Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1006_8e1e514_p288-from-commit/`
(`run.json`, `submit.sbatch`, `score288.py`, `logs/`, `out/`, `bin/`). One Slurm job:

| jobid | name | state | exit | elapsed | ended |
|---|---|---|---|---|---|
| 33746506 | p288commit | COMPLETED | 0:0 | 00:02:02 | 2026-10-24T21:08:53 |

Polled from the laptop (`scripts/slurm_poll.sh 33746506`); the `sacct` row above is the settled state.
A row for this runid is in `runs/index.tsv` with `verdict` and `human_note` left empty for the lead.
No code was changed; the canonical checkout was only fetched from.

### What this establishes, and what it does not

It establishes the bridge the ticket was opened for: **the program that produced ticket 287's numbers is
the program commit `8e1e514` builds** — identical binary, identical exports point for point — so 287's
results now attach to the commit instead of to an uncommitted patch. It says nothing new about the
method: no new material was tested, and the four Pot D lanes plus Pot B 01 remain untested for the
reason recorded in ticket 287 (their stage inputs were deleted on 2026-10-24). The weight it can bear is
"the build is honest", not "the change is proven on more pots".

## Lead verdict (2026-10-24)

1. **Accepted.** I verified the three things the ticket exists to prove, from the run's own files
   rather than from the summary: the built binary is `a28d10afab2b50bbe750d599ee2b7214`
   (`logs/p288-33746506.out`, "binary_matches_287_after=... -> IDENTICAL"), all eight lanes
   REPRODUCES with zero difference in n / median / both coverages / jumps (`out/score288.txt`), and
   the pointwise comparison is `max_dxyz = 0.000000` on all eight — the exports are the same files,
   not merely inside tolerance. The four frozen surfaces are byte-unchanged before and after, so no
   mesh ran. Job 33746506 COMPLETED 0:0.

2. **The median drift is mine, and the project scorer wins.** The three expected medians in this
   ticket (C01 Bl1 0.572, J01 Bl0 0.581, J01 Bl1 0.597) came from my independent recompute against a
   separately copied author file; the 287 run's own `score287.txt` says 0.575 / 0.582 / 0.601.
   Gating against the file instead of a retyped number was the right call. Differences are <= 0.004 mm,
   inside the +-0.05 window, and change no verdict. **Downstream, quote the project scorer's numbers**
   — the difference is one copy of the reference dots, not the method.

3. **What it establishes:** the program that produced ticket 287's numbers is the program commit
   `8e1e514` builds. The four shipped changes (growth angle 3.4, the 12 mm stop rule, the short-chain
   clamp, and the largest-lump seed) now attach to git instead of to an uncommitted patch in a worktree.

4. **What it does not establish:** anything new about the method. No new material was tested; the four
   Pot D lanes and Pot B 01 remain untested for the reason recorded in ticket 287 (their staged inputs
   were deleted on 2026-10-24). Weight: "the build is honest", not "the change holds on more pots".

5. **Record:** index row for `20261024-1006_8e1e514_p288-from-commit` / 33746506 filled by the lead
   (verdict + human_note); `run.json` carries the build identity, the eight rows, the pointwise line,
   the seed lines and the sheet md5s. The stale cleanup manifest the worker flagged
   (`.scratch/cleanup-2026-10-23-manifest.md`, 19 h old, a finished record) is committed with this
   ticket rather than left untracked.

