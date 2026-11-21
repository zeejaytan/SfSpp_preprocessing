# 07: Why do Pot J's axes lose on our own surfaces, and can one scale-free fix close it?

**What to build:** A diagnosis first, then at most two pre-registered fixes, all prototyped on Spartan only (ZERO tracked edits in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`; export a clean `-p1` unified `impl_t07.diff` over commit `325a0a8`, the head of branch `03-ship-joint-axis-and-e2e-own-surfaces-gate`, which already contains the shipped tri selector in `sfs_axes/meridian.py` and `sfs_axes/joint.py`; check `git apply --ignore-whitespace --check`). Goal: make the own-code E2E chain reach Pot J `>= 8/11, >= 16/21` (the Authors-axes control floor) without dropping any other pot below its floor.

**Answers:** E1
**Blocked by:** None (Ticket 03 executed at `325a0a8`, `Reading: tri-shipped-own-e2e-differs`, unmerged)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-21)
**Branch:** 07-pot-j-own-surface-axes, in /c/PR/worktrees/sfs/07
**Worker:** dsh one-shot subagent w07-axis-parity
**Budget:** large 8
**Hand-over:** DeepSeek — hidden acceptance check staged separately by lead

---

## 1. What is already established (read Ticket 03 write-back first; do not re-derive)

Source: `.scratch/axis-parity/issues/03-ship-joint-axis-and-e2e-own-surfaces-gate.md` (on branch `03-ship-joint-axis-and-e2e-own-surfaces-gate`; read with `git show 325a0a8:<path>`), Ticket 06 Comments (on `main`), Ticket 03 Spartan run dirs under `/data/gpfs/projects/punim2657/SfSpp/runs/*t03*` (`out/axes03_tri` = axes from Authors' surfaces, `out/axes03_own` = axes from our own `MeshPreprocessingHeadless` surfaces, `runs/20261121-1600_2e951d9_t03-jctl` = the Pot J control).

- Own-code E2E with the tri selector: 9 of 10 pots meet their floor. **Pot J: `8/11 5/21` and `7/11 4/21`** vs floor `8/11 16/21`; the control (same breaklines, Authors' released axes) holds `8/11 16/21`.
- Same chain with axes extracted from the **Authors' surfaces**: Pot J `8/11 15/21` and `8/11 16/21`. So breaklines, assembler and selector code are not the cause; the axes extracted from our surfaces for Pot J are.
- Per-piece rank-0 angle, ours vs Authors' surface: `Pot_J_Piece_12` `81.4°` vs `28.3°`, `Pot_J_Piece_06` `53.4°` vs `47.9°`, `Pot_J_Piece_07` `13.3°` vs `27.2°`, `Pot_J_Piece_01` `82.8°` vs `89.1°`. Offline Pot J `K3` is `8/11` on Authors' surfaces and `7/11` on ours. Only 4 (Authors') / 5 (ours) of 11 Pot J stems reach rank-0 under `10°`.
- Dead ends already closed (do NOT retest): see `.scratch/axis-parity/spec.md` §4; `K` capping on base fragments is out of scope; `dual_k2` and plain `axes335` are known (Pot J own-surface numbers for them are in Ticket 05/03 outputs and may be used as references).

## 2. Phase 1 — Diagnosis (read-only, no new selector; Spartan compute nodes only)

For all 11 Pot J stems plus the 3 other pots' worst own-vs-Authors gaps (list them from `axes03_audit.json`), on both surface sets, using cached pools if they exist:

1. **Surface comparison:** point count, bounding size, point density (mm between nearest neighbours), normal quality (angle between our normal and the Authors' normal at nearest point, median/90th percentile), and whether the sherd's rim/edge band is trimmed differently. Report per stem in a TSV.
2. **Arm attribution:** for each stem and surface, rank-0 and best-of-`K` angle for `A1`, `B2`, `P`, and the merged `tri`; and whether a candidate within `10°` of GT exists in the seed pool at all (M1) or was lost in refinement/dedup (M2) or lost in ranking (M3). Same taxonomy as Ticket 01 (`.scratch/axis-parity/issues/01-diagnose-14-losses-and-own-surfaces-audit.md`).
3. **Name the cause in one of these buckets (pick, with the numbers):** (a) our normals are noisier or flipped on Pot J so `A1`/`B2` are misled; (b) our surfaces are trimmed/denser/thinner so the position-only `P` arm degrades; (c) pool seeds miss the true basin on our surfaces; (d) something else — say what.
4. Look at it: render at least 4 Pot J stems (GT, Authors' axes, ours on both surfaces) with the sherd points, as `render07_diag.png`, before writing the cause.

**Phase 1 stop rule:** if the cause cannot be put in a bucket with per-stem evidence, finish with `Reading: pot-j-cause-not-isolated` and run NO Phase 2.

## 3. Phase 2 — At most two pre-registered fixes (only if Phase 1 isolates a cause)

Write the fixes into `<run>/work/PREREG07.md` BEFORE running them: each must be scale-free (no per-pot, per-piece or object-size constant), tied to the named bucket, and implemented in `sfs_axes/t07/` plus `tests/test_t07_*.py` (prototype namespace, not shipped). Candidates by bucket (pick only what the evidence points to, max 2):
- (a) normal-quality-weighted or robustly re-estimated normals for `A1`/`B2` residuals (e.g. a local-PCA normal consistency weight), or dropping `A1`/`B2` rank-0 priority when their normal-consistency score is poor and promoting `P`;
- (b) matching the surface preprocessing that the position-only arm expects (e.g. the sampling/stride the `P` arm uses), only if the audit shows a density/trim difference;
- (c) enlarging or diversifying the seed pool by a scale-free rule.

**Part A bars (offline, on `141` GT pieces, both surface sets; Authors' surface numbers must not drop below Ticket 06/03):** Authors `110/141 K1`, `128/141 K3`, median `<= 2.7054°`, `Pot A d_gt_to_est <= 2.4733 mm`, `Pot G 7/7 K=1`, `SignAxisGuard 0/18` rank-0 and `0` worst-case; own surfaces `K1 >= 116/141`, `K3 >= 127/141`, **own `Pot J K3 >= 8/11`** (up from `7/11`), own `Pot_J_Piece_12` best-of-`K <= 30°`. If neither fix passes, finish with `Reading: pot-j-own-surface-not-fixed-offline` (no E2E).

## 4. Phase 3 — E2E (only if a fix passes Part A), same own-code chain as Ticket 03 Pass 3

Stage A first: `Pot J`, `Pot G`, `Pot H`, `Pot D`, `Pot E`, 2 repeats each (`MOR1/2` control + `K3R1/2` ours), then the native-3x `def_3x` Juglet (4 repeats; report every repeat). Gate: Pot J `>= 8/11, >= 16/21` in BOTH repeats; `G 7/7 10/10`; `H 11/11 17/17`; `D >= 23/28 >= 55/69`; `E >= 29/31 >= 57/62`. Stage B (only if A passes): `Pot A, B, C, F, I`, 2 repeats, floors as in Ticket 03. Axes for Pot A..J are extracted from OUR surfaces; the assembler reads our breaklines only; no Authors' breakline enters the K3 arms. Juglet axes in native 3x units (no `/3.0` on written files).

## 5. Harness traps already hit (Tickets 02/05/06/03)

`AX_MO` (`<P>_MOR1/2`) is the Authors' released `Axes/` control, `AX_318` (`<P>_K3R1/2`) is ours. `score58` lacks `--scale`; Piece 7 angles come from its `per_edge` deg column. Export `RUN_DIR` with `sbatch --export=ALL`. Collect `sacct -X` once from the login node into `out/sacct_all.txt`. `corpus_md5` helpers import by name; verify `CORPUS-UNCHANGED` is genuinely computed (a harness import error once printed a false CHANGED). Submit with `--export=ALL`, poll every `sbatch` with `scripts/slurm_poll.sh`, record final `sacct` State/ExitCode. Spartan run dir `runs/<YYYYMMDD-HHMM>_<git7>_t07-potj-own/`; one `runs/index.tsv` row per job with blank `verdict`/`human_note`.

## 6. Deliverables (`C:/PR/artifacts/axis-parity-07/`, fetch, then LOOK at the renders)

`axes07_diag.tsv` (per stem per surface: surface stats, arm angles, M-bucket), `axes07_summary.json` (non-empty `jobs` list from `sacct -X`, cause bucket, per-piece before/after, Part A table, Phase 3 per-repeat table), `gate07.tsv` (header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote`), `render07_diag.png`, `PREREG07.md` (when Phase 2 runs), `impl_t07.diff` (when Phase 2 runs), and `render07_e2e.png` + `score/acc_pot*.tsv` + `score/juglet/` when Phase 3 runs.

## 7. Git

Work only in your ticket worktree/branch; write the results into this ticket; commit with `Worker: DeepSeek` and push the branch. Do NOT merge, push `main`, run `ticket_close.sh`, change `**Status:**`, or edit `structure-from-sherds-pp/`, `docs/`, `intent/`, or other tickets. No background watcher left running. Finish with `**End state:** ready` and one bare `Reading:` line.

## Readings (pick one verbatim)

- `pot-j-own-surface-fixed-e2e-passes` — Part A bars pass and Phase 3 clears Pot J in both repeats and every other gated pot.
- `pot-j-own-surface-fixed-offline-misses-e2e` — Part A passes but Phase 3 misses a floor; give exact pot/repeat.
- `pot-j-own-surface-not-fixed-offline` — cause isolated, no fix passes Part A, no E2E.
- `pot-j-cause-not-isolated` — Phase 1 could not name the cause.
- `blocked: missing-or-failed-control` — input, control or `CORPUS-UNCHANGED` failure.

## Out of scope

Editing tracked files; merging Ticket 03; C++ assembler (Ticket 04); `K` capping on base fragments; Juglet repeat spread.

## Acceptance

- [ ] Phase 1 table covers all 11 Pot J stems on both surfaces with a named cause bucket, or `pot-j-cause-not-isolated`.
- [ ] If Phase 2 ran: `PREREG07.md` written before results, `impl_t07.diff` applies cleanly over `325a0a8`, unit tests pass on a Spartan node (record job id).
- [ ] `sacct -X COMPLETED 0:0` for every counted job, `CORPUS-UNCHANGED`, `runs/index.tsv` rows appended.
- [ ] Deliverables fetched, renders inspected, no watcher left, `**End state:** ready` and bare `Reading:`.
