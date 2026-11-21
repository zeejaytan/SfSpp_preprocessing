# 03: Ship joint axis refiner into `sfs_axes/` and run 100%-own-code E2E gate

**What to build:** Promote Ticket 06's proven parallel tri-invariant `A1 + B2 + P` selector (`impl_t06.diff`, or fallback `t05`) into `SfSpp_preprocessing/sfs_axes/` as the default on the normalized profile-ranked union path (keeping Ticket 335's `orient_base_axis` ON, adding a clean env/CLI opt-out that restores exact `axes335` bytes), add unit tests with zero CRLF line endings, and run the **100%-own-code E2E verification gate** (`MeshPreprocessingHeadless` surfaces -> landed `sfs_axes` -> `EdgeLineExtraction` breaklines -> `structure-from-sherds-pp` assembler) across all 10 paper pots (`Pot A..J`) and `def_3x` Juglet.

**Answers:** E1
**Blocked by:** None (Ticket 06 resolved with tri-selector-passes-all-ten-pots-and-juglet)
**Status:** needs-triage
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek — hidden acceptance check staged separately by lead

---

## Implementation requirements (preserve LF `\n` line endings in every edited file)

1. **`SfSpp_preprocessing/sfs_axes/` (`select.py`, `profile.py`, `normalized.py`, `potsac.py`, `cli.py`) & `scripts/run_benchmark_172.py`:**
   - Land the exact winning Ticket 05 method cleanly behind a single opt-out switch (e.g. `SFS_AXES_DUAL_SELECT=0` / `--no-dual-select` restoring `axes335` bit-for-bit).
   - Keep `run_potsac` (paper chain) and legacy `UNION_RANKER == "normal"` untouched; preserve `BASE_ORIENT=1` (`orient_base_axis` as final sign step).
2. **`SfSpp_preprocessing/tests/` (`test_select.py` / `test_normalized.py`):**
   - Keep all `>= 42` existing unit tests green; add synthetic & invariance tests verifying `A1 + B2` parallel dual selection, `15°` dedup, opt-out restores pre-03 output bit-for-bit, and normal-sign invariance (`N -> -N`) holds.
3. **100%-own-code E2E gate on Spartan compute nodes (`CORPUS-UNCHANGED`):**
   - Pass 1 (switch ON): extract axes across `Pot A..J` on BOTH (a) Authors' `Surfaces/` (verifying zero regression vs Ticket 05) and (b) **our own `MeshPreprocessingHeadless` surfaces** (`163` pieces, `141` GT-scored), plus `def_3x` Juglet (`0/18 SignAxisGuard`).
   - Pass 2 (opt-out OFF): verify `172/172` byte-identical reproduction of `axes335`.
   - Pass 3 (100%-own-code E2E assembly, 2 repeats/pot + `def_3x` Juglet `4` repeats): stage our own `MeshPreprocessingHeadless` surfaces -> our own landed `sfs_axes` -> our own `EdgeLineExtraction` breaklines -> `structure-from-sherds-pp` assembler (`CORPUS-UNCHANGED`), confirming all 10 pots meet/beat `t323` floors and `def_3x` Juglet reaches `9/9`, `<= 0.50 mm` cluster, `4/4` Piece 7 joins.
4. **Docs & Visual QA (`C:/PR/artifacts/axis-parity-03/`):**
   - Fetch `axes03_audit.json`, `gate03.tsv`, `render03_own_e2e.png`, `cmp_axes335_off.txt`, and `score/acc_pot{A..J}.tsv` + `juglet/`. Inspect `render03_own_e2e.png` visually and prepare `e2e-obj-to-reassembly.md` & `FIXES-LEDGER.md` updates for lead review.

---

## Readings (pick one verbatim on a bare `Reading:` line)
- `joint-axis-shipped-and-own-e2e-verified` — unit tests pass (`0` CRLF), opt-out restores `172/172` `axes335` bytes, and 100%-own-code E2E passes all 10 pots + `def_3x` Juglet (`0/18 SignAxisGuard`).
- `own-e2e-differs-from-t05` — landed `sfs_axes` matches `axes05` on Authors' surfaces but exposes an upstream surface/breakline E2E gap on our own `MeshPreprocessingHeadless` lane; report exact pot/piece diffs.
- `blocked: test-or-gate-failed` — unit test, opt-out invariance, or control failure.

## Out of scope
- Editing C++ assembler files in `structure-from-sherds-pp/class/` (covered by Ticket 04).

## Acceptance
- [ ] Landed code passes all existing + new unit tests (`>= 46 passed`) with zero CRLF across modified Python files.
- [ ] Opt-out switch restores `172/172` byte-identical `axes335` (`cmp -s`, `DIFFER 0`).
- [ ] 100%-own-code E2E (`MeshPreprocessingHeadless` surfaces -> landed `sfs_axes` -> `EdgeLineExtraction` breaklines -> assembler) passes all 10 pots (`Pot A..J`) and `def_3x` Juglet (`9/9`, `0/18 SignAxisGuard`) with `sacct -X COMPLETED 0:0` and `CORPUS-UNCHANGED`.
- [ ] `C:/PR/artifacts/axis-parity-03/{axes03_audit.json,gate03.tsv,render03_own_e2e.png,cmp_axes335_off.txt,score/}` fetched and `render03_own_e2e.png` visually inspected before writing bare `Reading:` and `**End state:** ready`.
