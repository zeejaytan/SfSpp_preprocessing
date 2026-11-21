# 03: Ship the tri-invariant axis selector into `sfs_axes/` and run the 100%-own-code E2E gate

**What to build:** Land Ticket 06's winner `tri_psec_d10` (`A1` calibrated Huber `width=0.05` rank-0 + `B2` Hermite normal-consistent rank-0 + shipped position-only `select_union_lines` rank-0 and secondaries, `10°` dedup, `K <= 3`, one final `orient_base_axis`) into `SfSpp_preprocessing/sfs_axes/` as the default of the union path, behind one opt-out that restores `axes335` byte-for-byte. Add unit tests. Then run the **100%-own-code E2E gate**: our `MeshPreprocessingHeadless` surfaces -> landed `sfs_axes` -> our `EdgeLineExtraction` breaklines -> `structure-from-sherds-pp` assembler, on all 10 paper pots + native-3x `def_3x` Juglet.

**Answers:** E1
**Blocked by:** None (Ticket 06 resolved at `ad0cc0f`, `Reading: tri-selector-passes-all-ten-pots-and-juglet`)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-21)
**Branch:** 03-ship-joint-axis-and-e2e-own-surfaces-gate, in /c/PR/worktrees/sfs/03
**Worker:** dsh one-shot subagent w03-axis-parity
**Budget:** large 8
**Hand-over:** DeepSeek — hidden acceptance check staged separately by lead

---

## 1. Source of truth (read, do not re-derive)

- Ticket 06 (merged): `.scratch/axis-parity/issues/06-tri-invariant-selector-potj-and-tenpots.md` (Comments section has every number).
- Working prototype as a clean `-p1` diff over `9e0fe6a`: `C:/PR/artifacts/axis-parity-06/impl_t06.diff` (9 new files, zero tracked edits; adds `sfs_axes/t02/*`, `sfs_axes/t06/{__init__,tri}.py`, `tests/test_t02*.py`, `tests/test_t06_tri.py`). Same file on Spartan: `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-0323_9e0fe6a_t06-tri/work/impl_t06.diff`; run dir also holds `work/` harness, `out/axes06_tri/` (163 axes) and `out/axes06_juglet_def3x/` (native 3x).
- Own-surface pieces for Pots A..J: reuse Ticket 02's `work/run.json` Own-surface paths and Ticket 01's `out_poth/geom` (see Ticket 06 §1). Juglet `def_3x` geometry: `/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0430_d272313_t80-default-on/out/cell_def_3x/geom/Juglet_Piece_{1..9}.S{0,1}`.
- E2E driver recipe: `make_e2e_323.sh` / the `t06` builders under the Ticket 06 run `work/` (Authors' `MOR` controls + `K3R` ours; Juglet scorer `cluster366.py --scale 3.0 --bar 13.788`).

## 2. Implementation requirements (LF line endings in every edited file, zero `\r`)

1. **Land the code, do not copy the t02/t06 prototype namespace.** Move what `tri.py` needs (`arm_a1`, `arm_b2`, the merge, calibrated Huber cost) into the production modules (`sfs_axes/select.py`, `normalized.py`, `profile.py`, a new module is fine) under production names. No `t02`/`t06` names may remain in shipped code or in the CLI.
2. **Single switch, default ON:** env `SFS_AXES_TRI_SELECT` (default `1`) plus CLI `--no-tri-select`. OFF must reproduce current `axes335` output byte-for-byte on all 172 pieces (163 Pot A..J + 9 Juglet). Keep `run_potsac` (paper chain) and the legacy `UNION_RANKER == "normal"` path untouched; `BASE_ORIENT` (`orient_base_axis`) stays ON and remains the final sign step; no `canonicalize()` on written axes; `line_shift <= size`.
3. **No magic numbers by object/pot/piece:** only the constants already named in Ticket 06 (`width=0.05`, `dedup_deg=10.0`, `kmax=3`, `include_p_secondaries=True`).
4. **Unit tests** (`tests/`): keep all 42 existing tests green; port the 22 `t06` tests and the 13 `t02` tests to the production API; add tests that (a) the switch OFF returns exactly the `select_union_lines` result, (b) `A1` rank-0 precedence, `B2`/`P` append order, `10°` dedup, `K <= 3`, (c) `N -> -N` normal-sign invariance, (d) base-disk upright orientation. Target `>= 77` passing, run on a Spartan compute node (record job id), plus a local `python -m pytest tests -q` that must also pass.
5. **Do not touch** `structure-from-sherds-pp/` (C++ assembler is Ticket 04), `docs/`, `intent/`, or any other ticket.

## 3. Gate on Spartan compute nodes (`CORPUS-UNCHANGED`, run dir `runs/<YYYYMMDD-HHMM>_<git7>_t03-ship/`, `runs/index.tsv` row per job with blank `verdict`/`human_note`)

- **Pass 1 (switch ON, landed code):** extract Pot A..J (163) on Authors' surfaces and on our own `MeshPreprocessingHeadless` surfaces, plus native-3x `def_3x` Juglet (`.xyz` in 3x tree units, no `/3.0` on written files). Authors' surfaces must reproduce Ticket 06 `tri_psec_d10`: `110/141 K1`, `128/141 K3`, median `2.7054°`, `d_gt_to_est 4.3383 mm`, `Pot A 2.4733 mm`; own surfaces `116/141 K1`, `127/141 K3`; `Pot G 7/7 K=1` on both; `SignAxisGuard 0/18` rank-0 and `0` worst-case.
- **Pass 2 (switch OFF):** `cmp -s` against stored `axes335` for all 172 pieces, `DIFFER 0`.
- **Pass 3 (100%-own-code E2E, 2 repeats/pot, 4 repeats Juglet):** `MeshPreprocessingHeadless` surfaces -> landed `sfs_axes` (switch ON) -> `EdgeLineExtraction` breaklines -> assembler. Floors per pot: `A 8/8 15/15`, `B 9/9 15/15`, `C 4/4 5/5`, `D >=23/28 >=55/69`, `E >=29/31 >=57/62`, `F 5/5 7/7`, `G 7/7 10/10`, `H 11/11 17/17`, `I >=25/26 >=59/62`, `J 8/11 16/21`. Juglet best-of-4: `9/9` sherds, `>=10/18` edges, cluster `<=0.50 mm`, `4/4` Piece 7 joins `<5°`. Report **every repeat**, not only the best; say how many of 4 Juglet repeats reached the bar (Ticket 06 got 1 of 4; `dual_k2` got 4 of 4). If the own-code chain cannot run end-to-end, report exactly which stage breaks; do not substitute Authors' breaklines silently.
- **Harness traps already hit:** `AX_MO` (`<P>_MOR1/2`) = Authors' released `Axes/` control, `AX_318` (`<P>_K3R1/2`) = ours; label renders `MOR1 [Authors control]` vs `K3R1 [ours]`. `score58` lacks `--scale`, so Piece 7 angles come from its `per_edge` deg column. Do not divide Juglet `.xyz` by 3. Export `RUN_DIR` with `sbatch --export=ALL`. `sacct` inside a batch job returns a subset; collect `sacct -X` once from the login node into `out/sacct_all.txt`.

## 4. Deliverables (`C:/PR/artifacts/axis-parity-03/`, fetch from Spartan, then look at the renders before writing a Reading)

`axes03_audit.json` (non-empty `jobs` from `sacct -X`, Pass 1 metrics, Pass 2 `DIFFER` count, Pass 3 per-repeat table), `gate03.tsv` (header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote`), `render03_own_e2e.png` (10 pots + Juglet, `MOR1 [Authors control]` left vs `K3R1 [own code]` right), `cmp_axes335_off.txt`, `score/acc_pot{A..J}.tsv`, `score/juglet/`. Inspect `render03_own_e2e.png` before writing the Reading.

## 5. Git

Work only in your ticket worktree/branch. Commit the code, tests and this ticket's write-back; **do not** merge, push `main`, run `ticket_close.sh`, or change `**Status:**` (stays with the lead). Commit message states cause, decision, what was checked, and carries `Worker: DeepSeek`. Write `**End state:** ready` and one bare `Reading:` line last.

## Comments (worker: DeepSeek, 2026-11-21)

**Run:** `runs/20261121-1319_2e951d9_t03-ship/` (code commit `2e951d9`, branch `03-ship-joint-axis-and-e2e-own-surfaces-gate`). Every job below was submitted from that run, polled to a final state, and has a row in `runs/index.tsv` with blank `verdict`/`human_note`. `out/sacct_all.txt` is one `sacct -X` taken from the login node (33 lines); the final audit that wrote `axes03_audit.json`/`gate03.tsv` is job `35467233` (COMPLETED 0:0).

### What landed
- `sfs_axes/meridian.py` (new, 226 lines): calibrated Huber cost (`NORMAL_WIDTH=0.05`), `refine_axis_normal`, the normal-consistent Hermite thickness (`hermite_thickness`, `profile_thickness_cost`), `refine_axis_profile_thickness`, and the at-piece bound (`piece_scale`, `line_shift`).
- `sfs_axes/joint.py` (new, 254 lines): `normal_arm` (A1), `thickness_arm` (B2), `merge_lines` (rank-0 of A1, then of B2, then of the shipped hypothesis; `JOINT_DEDUP_DEG=10.0`, `JOINT_KMAX=3`, `include_shipped_secondaries=True`), `orient_merged` (one final `orient_base_axis`), `select_joint_lines`.
- `sfs_axes/select.py`: `TRI_SELECT = SFS_AXES_TRI_SELECT` (default 1) plus a `tri_select` argument; the joint path returns before the shipped body, so the opt-out is the shipped body untouched. `sfs_axes/potsac.py`: forwards `tri_select` on the `profile` ranker only, leaving the `normal` legacy branch and `run_potsac` alone. `sfs_axes/cli.py`: `--no-tri-select`.
- No `t02`/`t06` identifiers in shipped code (grep clean), zero `\r` in every changed file, 8 files, +1040/−8.
- Deliberately **not** shipped, because the ticket asks only for what the winner needs: the t02 arms A2/C1/C2/D and the t02 metrics module. The seven t02 tests that target them are therefore not ported; the ported set is the 22 t06 cases and the 12 t02 cases whose functions ship.

### Tests
`tests/test_joint.py` (25 cases) and `tests/test_meridian.py` (12) are new; the base-disk case in `tests/test_select.py` now pins the shipped body with `tri_select=False`.

| where | job | result |
|---|---|---|
| Spartan compute node | `35464481` | `79 passed, 1 warning in 36.05s`, `COMPLETED 0:0` |
| laptop | `python -m pytest tests -q` | `79 passed` |

(The first Spartan attempt, `35464460`, ran no tests because the `tora` env has no `pytest`; it exited without failing. `35464481` adds `PYTHONPATH` to the pytest copy at `runs/20261120-1430_9e0fe6a_t02-cost-landscape/work/pylibs`.)

### Pass 1 — reproduction (`35464462`; cached pools `35464461`, `35464621`)
| surfaces | K1 ≤10° | K3 ≤10° | median rank-0 | median d_gt_to_est | Pot A | Pot G at K=1 | Juglet K1/K3 |
|---|---|---|---|---|---|---|---|
| Authors' | 110/141 | 128/141 | 2.7054° | 4.3383 mm | 2.4733 mm | 7/7 | 7/9, 8/9 |
| ours | 116/141 | 127/141 | 2.5631° | 3.7781 mm | — | 7/7 | — |

Ticket 06's numbers are reproduced exactly on the Authors' surfaces; the own-surface row matches Ticket 06's own-surface numbers (116/141, 127/141). SignAxisGuard 0/18 rank-0 pairs and 0 worst-case over K. The cached-pool run reproduces both rows. `Pot_J_Piece_05` best-of-K 2.8307° and `Pot_A_Piece_08` rank-0 4.741° are unchanged from Ticket 06 where they are comparable.

`out/axes03_own` holds **148 of the 163** pot pieces: all **141** GT stems are present; the 15 absent files are pieces with no own-surface mesh in the lane (e.g. `.../20261105-0445_9c5eec2_t305-lane-j/out/geom/Pot_J_Piece_13.S0`), and none of them is in an assembler named set. Pot J's own axes cover all 12 of its named pieces. The Juglet axes are written in native 3x tree units with no `canonicalize()`.

### Pass 2 — the opt-out (`35464482`)
Landed code with `SFS_AXES_TRI_SELECT=0` (and `--no-tri-select`) against the pre-ticket tree `9e0fe6a`: **172/172 pieces SAME**, equal byte counts on every row, `cmp -s` exit 0, **DIFFER=0**; CORPUS-UNCHANGED over 907 corpus files. `out/cmp_axes335_off.txt` is the record.

### Pass 3 — 100%-own-code E2E (switch ON)
Chain: our `MeshPreprocessingHeadless` surfaces (the t319 `LANES`, which carry our `EdgeLineExtraction` `.Bl0`) → landed `sfs_axes` on those surfaces (`out/axes03_own`) → the assembler. `K3R1`/`K3R2` are that chain; `MOR1`/`MOR2` are the control (the same breaklines with the Authors' released axes). No Authors' breakline enters the chain.

| pot | floor (sherd, edge) | K3R1 | K3R2 | MOR1 | MOR2 | verdict |
|---|---|---|---|---|---|---|
| A | 8/8, 15/15 | 8/8, 15/15 | 8/8, 15/15 | 8/8, 15/15 | 8/8, 15/15 | floor and target |
| B | 9/9, 15/15 | 9/9, 15/15 | 9/9, 15/15 | 9/9, 15/15 | 9/9, 15/15 | floor and target |
| C | 4/4, 5/5 | 4/4, 5/5 | 4/4, 5/5 | 4/4, 5/5 | 4/4, 5/5 | floor and target |
| D | 23/28, 55/69 | 24/28, 58/69 | 24/28, 58/69 | 23/28, 55/69 | 23/28, 55/69 | floor met, target (26/28, 63/69) not |
| E | 29/31, 57/62 | 30/31, 59/62 | 30/31, 59/62 | 31/31, 62/62 | 31/31, 62/62 | floor met, target (31/31, 62/62) not |
| F | 5/5, 7/7 | 5/5, 7/7 | 5/5, 7/7 | 5/5, 7/7 | 5/5, 7/7 | floor and target |
| G | 7/7, 10/10 | 7/7, 10/10 | 7/7, 10/10 | 7/7, 10/10 | 7/7, 10/10 | floor and target |
| H | 11/11, 17/17 | 11/11, 17/17 | 11/11, 17/17 | 8/11, 9/17 | 10/11, 15/17 | floor and target |
| I | 25/26, 59/62 | 26/26, 62/62 | 26/26, 62/62 | 25/26, 59/62 | 25/26, 59/62 | floor and target |
| J | 8/11, 16/21 | 8/11, **5/21** | 7/11, **4/21** | 8/11, 16/21 | 8/11, 16/21 | **edge floor missed** |

All ten jobs COMPLETED 0:0 and every pot CORPUS-UNCHANGED; `score/acc_pot{A..J}.tsv` carry all four arms per repeat.

**Pot J is the miss, and it is the axes.** The sherd floor is met (8/11); the edge floor is not (5/21 and 4/21 against 16/21), while the control on the very same breaklines holds 16/21 in both repeats. Our own-surface axes for J are worse than the Authors'-surface axes exactly on the pieces that carry its edges: rank-0 on `Pot_J_Piece_12` 81.4° (Authors' surface 28.3°), `Pot_J_Piece_06` 53.4° (47.9°), `Pot_J_Piece_07` 13.3° (27.2°, better), `Pot_J_Piece_01` 82.8° (89.1°, better). Pot J was already the weakest pot on both surface sets: 4 of its 11 stems reach rank-0 under 10° on the Authors' axes, 5 on ours. Nothing was silently substituted: the K3 arms read only our breaklines and our axes.

**Diagnostic control (`35466812`, `runs/20261121-1600_2e951d9_t03-jctl`)**: the same chain with the axes extracted on the Authors' surfaces (`out/axes03_tri`) gives `J_K3R1` 8/11, 15/21 and `J_K3R2` 8/11, 16/21 — the floor. So the chain meets the J floor when the axes come from the Authors' surfaces and misses it when they come from our own: the stage that loses Pot J is the axes extracted from our surfaces, not the breaklines, the assembler or the selector code. `score/acc_potJ_authorsurface_control.tsv`.

**Juglet** (def_3x axes byte-identical to Ticket 06's `out/axes06_juglet_def3x`; 4 repeats):

| repeat | sherds | edges | cluster seated | max chamfer | Piece-7 joins <5° |
|---|---|---|---|---|---|
| r1 | 8/9 | 7/18 | 9/9 | 0.472 mm | 4/4 |
| r2 | 9/9 | 8/18 | 9/9 | 0.472 mm | 4/4 |
| r3 | 8/9 | 8/18 | 9/9 | 0.471 mm | 4/4 |
| r4 | 8/9 | 8/18 | 9/9 | 0.477 mm | 4/4 |

Best-of-4 (r2): 9/9 sherds, 8/18 edges, cluster 9/9 at ≤0.50 mm, 4/4 joins. **0 of 4 repeats reach the bar**, always short on edges (best 8/18 against 10/18). Ticket 06 reached it in 1 of 4, `dual_k2` in 4 of 4; because the axes here are byte-identical to Ticket 06's, this is the rig's spread and not a change in our output.

### Artifacts (fetched to `C:/PR/artifacts/axis-parity-03/`)
`axes03_audit.json` (jobs from `sacct -X`, Pass 1 per surface, Pass 2 count, Pass 3 per-repeat rows), `gate03.tsv` (55 PASS, 5 FAIL, 2 INFO; the FAILs are Pot J, the Juglet bar and three earlier audit attempts below), `render03_own_e2e.png`, `cmp_axes335_off.txt`, `score/acc_pot{A..J}.tsv`, `score/acc_potJ_authorsurface_control.tsv`, `score/juglet/`.

`render03_own_e2e.png` was inspected: A–I show the same assembled form left and right, H visibly fuller with our axes (11/11 against 8/11); J shows our form loose and the control seated, matching 5/21 against 16/21; the Juglet row shows our vessel beside the oracle.

### Attempts that did not stand
- Audits `35464592`, `35464598`, `35464615` FAILED 1:0 on bugs in the audit script (list-vs-dict rows, axis row order, empty Juglet repeats); fixed, and `35464618` onward completed. Kept in `sacct_all.txt` rather than hidden.
- The first pytest job `35464460` is recorded as COMPLETED 0:0 but ran no tests (no `pytest` in the env); `35464481` is the run that counts.

## Readings (pick one verbatim on a bare `Reading:` line)

- `tri-shipped-and-own-e2e-verified` — tests pass (0 CR), switch OFF `DIFFER 0`, Pass 1 reproduces Ticket 06, Pass 3 meets every floor and the Juglet bar.
- `tri-shipped-own-e2e-differs` — landed code matches Ticket 06 on Authors' surfaces but own-code E2E misses one or more floors; report exact pot/piece diffs and the stage where they appear.
- `blocked: test-or-gate-failed` — unit test, opt-out invariance, reproduction or control failure.

## Out of scope

C++ assembler changes (Ticket 04); capping `K` on base fragments (separate follow-up if Juglet repeat spread is the only miss); docs/intent edits.

## Acceptance

- [ ] Landed code passes all existing + new tests (`>= 77 passed`) locally and on Spartan, zero `\r` in changed Python files, no `t02`/`t06` identifiers in shipped code.
- [ ] Switch OFF reproduces `axes335` bytes on 172/172 (`cmp -s`, `DIFFER 0`).
- [ ] Pass 1 reproduces Ticket 06 numbers above on Authors' surfaces (and own-surface numbers).
- [ ] Pass 3 own-code E2E reported for every repeat with floors and Juglet bar, `sacct -X COMPLETED 0:0`, `CORPUS-UNCHANGED`.
- [ ] Artifacts fetched, `render03_own_e2e.png` inspected, `runs/index.tsv` rows appended, no background watcher left running, `**End state:** ready` plus bare `Reading:`.

**End state:** ready

Reading: tri-shipped-own-e2e-differs
