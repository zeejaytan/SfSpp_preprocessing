# 03: Ship the tri-invariant axis selector into `sfs_axes/` and run the 100%-own-code E2E gate

**What to build:** Land Ticket 06's winner `tri_psec_d10` (`A1` calibrated Huber `width=0.05` rank-0 + `B2` Hermite normal-consistent rank-0 + shipped position-only `select_union_lines` rank-0 and secondaries, `10°` dedup, `K <= 3`, one final `orient_base_axis`) into `SfSpp_preprocessing/sfs_axes/` as the default of the union path, behind one opt-out that restores `axes335` byte-for-byte. Add unit tests. Then run the **100%-own-code E2E gate**: our `MeshPreprocessingHeadless` surfaces -> landed `sfs_axes` -> our `EdgeLineExtraction` breaklines -> `structure-from-sherds-pp` assembler, on all 10 paper pots + native-3x `def_3x` Juglet.

**Answers:** E1
**Blocked by:** None (Ticket 06 resolved at `ad0cc0f`, `Reading: tri-selector-passes-all-ten-pots-and-juglet`)
**Status:** ready-for-agent
**Branch:** set by `ticket_start.sh`
**Worker:** unassigned
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
