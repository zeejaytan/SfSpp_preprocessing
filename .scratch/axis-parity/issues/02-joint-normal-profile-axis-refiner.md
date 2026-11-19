# 02: Prototype & validate joint normal+profile axis selector and guarded analytical LM refiner

**What to build:** An offline prototype inside Spartan `<run>/work/impl_joint/` (ZERO edits to tracked `SfSpp_preprocessing/` or `structure-from-sherds-pp/` files) implementing the winning Ticket 01 formulation on top of shipped `axes335` (`commit 9e0fe6a`, keeping `orient_base_axis` ON by default), and validating it against **both Authors' `Axes/` AND shipped `axes335`** across:
1. All `163` corpus pieces (`141` GT-scored, on **both** Authors' `Surfaces/` and Our Own `MeshPreprocessingHeadless` surfaces) + `def_3x` Juglet (`9` pieces), and
2. Full 10-pot E2E assembly (`Pot A..J`, 2 repeats each, `MOR1/2` + `K3R1/2`) + `def_3x` Juglet (`4` repeats + positive controls).

**Answers:** E1
**Blocked by:** 01-diagnose-14-losses-and-own-surfaces-audit
**Status:** needs-triage — blocked by Ticket 01
**Worker:** unassigned
**Budget:** large 8
**Hand-over:** DeepSeek — hidden acceptance check at `C:/PR/artifacts/dsh-handover/axis-parity-02/accept.py` to be staged before dispatch

---

## Design constraints (learned from Tickets 322–336 & 366–368)

1. Prototype lives strictly inside `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t02-joint-axis/work/impl_joint/` as a clean patch over `9e0fe6a` (`impl_joint.diff` saved & verified with `patch -p1`).
2. Keep Ticket 335's `orient_base_axis` (`BASE_ORIENT=1`) intact at the end of `select_union_lines`, and do **NOT** introduce any per-pot, per-piece, or object-size-hardcoded branch.
3. Preserve full `4-DoF` freedom where `Pot_A_Piece_06` and `Pot_A_Piece_08` need `18°–35°` walks (never clamp to `6°` guards or lock 2-DoF pivot globally). Instead, fuse Ticket 01's scale-free normal+profile ranking (`e_hat_i` + `wall_thickness`) with profile-guarded full-cloud analytical LM refinement (`tol=1e-9`) and, only if Ticket 01 proved net gain on rim pieces, blind rim coplanarity (`SfS++ §IV-B2:177`).
4. Keep `keep_lines(c, tau=1.2, kmax=3)` (or re-verify why any alternative ratio holds Pot G `10/10` while keeping A/D/E/H/J rescues).

---

## Pre-registered Parity & E2E Acceptance Bars (must ALL pass to recommend shipping)

### Part A — Axis Parity vs Authors' `Axes/` (`141` GT pieces) & `def_3x` Juglet (`9` pieces)
- **`K1 <= 10°`:** `>= 109/141` (match/beat `axes335` AND strictly beat Authors' `105/141`) on Authors' surfaces; report own-surfaces score beside it.
- **`K3 <= 10°`:** `>= 121/141` (match/beat `axes335` AND strictly beat Authors' `116/141`).
- **Precision parity (the `Gap 1` test):** Overall `141`-piece median rank-0 angle **`<= 2.78°`** (beating Authors' `2.78°`), median radial offset **`<= 4.38 mm`** (beating Authors' `4.38 mm`), AND **`Pot A` median radial offset `<= 3.5 mm`** (down from `6.97 mm` toward Authors' `1.92 mm`).
- **Recovery of Ticket 01 losses:** Recover at least **`4` of the `8`** `K3` loss pieces (`A07, D23, E25, E29, E31, F05, I20, J02`) into `K3 <= 10°` without net regression elsewhere.
- **`def_3x` Juglet (`9` pieces, real 1x mm `/ 3.0`):** `K1 >= 7/9`, `K3 >= 8/9`, `is_base_fragment=True` on `Juglet_Piece_7` only, **`SignAxisGuard = 0/18 (0.00%)`**.

### Part B — 10-Pot (`Pot A..J`, 2 repeats) + `def_3x` Juglet (`4` repeats) E2E Assembly
- **All `10/10` paper pots at or above BOTH `t323` floors AND Ticket 323 achieved scores** (`Pot A 8/8 15/15`, `Pot B 9/9 15/15`, `Pot C 4/4 5/5`, `Pot D >=23/28 >=55/69` targeting `26/28 63/69`, `Pot E 31/31 62/62`, `Pot F 5/5 7/7`, `Pot G 7/7 10/10`, `Pot H 11/11 17/17`, `Pot I >=25/26 >=59/62`, `Pot J >=8/11 >=16/21`), with `MOR1/2` controls green and `CORPUS-UNCHANGED`.
- **`def_3x` Juglet (`t368` `cluster366.py` + `score58` at real `4.596 mm`):** Best of 4 repeats `9/9` sherds, **`>= 10/18` edges**, vertex cluster `9/9 <= 0.50 mm`, `4/4` Piece 7 joins (`3-7, 6-7, 7-8, 7-9`).

### Part C — Deliverables & Visual Check (`C:/PR/artifacts/axis-parity-02/`)
- Fetch `axes02_summary.json`, `gate02.tsv`, `render02_tenpots.png` (11-panel montage + close-up crops on any borderline pot), and `score/acc_pot{A..J}.tsv` + `juglet/`. Inspect visually before writing `Reading:`.

---

## Readings (pick one verbatim on a bare `Reading:` line)
- `joint-refiner-achieves-author-parity-and-passes-ten-pots` — passes EVERY pre-registered Part A parity bar AND all 10 pots + `def_3x` Juglet in Part B; ready to ship in Ticket 03.
- `joint-refiner-improves-axes-but-misses-bar` — improves some metrics over `axes335` but misses one or more pre-registered Part A/B bars; report exact trade-off and whether a follow-up refinement or multi-sherd stage is needed.
- `blocked: missing-or-failed-control` — `MOR` control drops below floor or Ticket 01 prerequisites absent.

## Out of scope
- Editing ANY tracked file in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`.

## Acceptance
- [ ] Zero tracked source edits (`git status --short` modifies only this ticket); `<run>/work/impl_joint.diff` cleanly reproduces prototype from `9e0fe6a` and passes all existing unit tests (`>= 42 passed`).
- [ ] Part A matches/beats both Authors' `Axes/` and `axes335` across `141` GT pieces (`K1 >= 109`, `K3 >= 121`, median `<= 2.78° / <= 4.38 mm`, `Pot A rad <= 3.5 mm`, `>= 4/8` K3 recoveries) and `def_3x` Juglet (`0/18 SignAxisGuard`).
- [ ] Part B holds all `10/10` pots (`A..J`) at/above `t323` floors and passes `def_3x` Juglet (`9/9`, `>= 10/18` edges, `<= 0.50 mm` cluster, `4/4` Piece 7 joins) with `sacct -X COMPLETED 0:0` and `CORPUS-UNCHANGED`.
- [ ] `C:/PR/artifacts/axis-parity-02/{axes02_summary.json,gate02.tsv,render02_tenpots.png,score/}` fetched and visually inspected before writing bare `Reading:` and `**End state:** ready`.
